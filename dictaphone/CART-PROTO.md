# CART-PROTO — Master ↔ Cartridge Protocol

**Rev:** 0.1 · **Date:** 2026-07-13 · **Status:** draft
**Scope:** the wire contract between the **Master** (ESP32-S31, orchestrator) and the **Cartridge** (Linux SBC inference worker, v1.5/v2). Fills SPEC open item "cartridge software contract." Physical link: 14-pin FFC (SPEC §5, J4). Hardware/power in [SPEC.md](SPEC.md); the message/state model below supersedes the earlier `MASTER-SBC-PROTO.md` draft.

Design goal: recording is always the Master's top priority (SPEC R4); the cartridge is a preemptible, power-gated compute peripheral. The Master initiates everything.

---

## 1. Transport stack (chosen for DX fit, not just features)

pw_rpc (Pigweed) has the ideal *design* — protobuf-native services, four call types including bidirectional streaming — but its *packaging* is Bazel/GN/CMake, **not PlatformIO**, so full adoption would force an ecosystem change on the ESP-IDF side. Decision: **use pw_rpc as the design blueprint, not as a dependency.**

| Layer | Choice | Rationale |
|---|---|---|
| Serialization | **protobuf via nanopb** | PlatformIO- and ESP-IDF-friendly; SBC (Linux) side trivial; versioned schema (proto_v) |
| Framing | **COBS + CRC-32** (or small single-file HDLC) | unambiguous frame delimiting + bit-error detection; standalone, no Pigweed build |
| Integrity | **CRC-32 per frame** | the threat on this link is line noise / bit-flips, NOT an adversary → CRC, not a hash/MAC/TLS (encrypting an in-enclosure chip-to-chip link is defending a door while the wall is open) |
| RPC / streaming semantics | **modeled on pw_rpc's 4 call types**, hand-dispatched | unary (job submit/result), server-stream (progress), client-stream, **bidirectional** (future `stt_rt`/`trans_rt`) |
| Transport | **UART now → SPI later** (transport-agnostic) | Opus 48k mono ≈ tens of kbps; a 10-min note ≈ 2 MB → ~7 s at 3 Mbaud UART, fine for "delay acceptable." SPI is the throughput escalation, **not Ethernet** |

**Open item (spike):** confirm whether full pw_rpc can be integrated on ESP-IDF acceptably; if yes it may replace the hand-dispatch. Default assumption is the nanopb + COBS/CRC + thin-dispatch path.

**Explicitly rejected:** Ethernet/TCP (power, wrong abstraction for a 3 cm link, "encryption for free" is false), eRPC (own IDL not protobuf, no streaming), ESP-Hosted (inverts topology: it exposes an ESP's radios to a host; here the ESP is the master).

## 2. Addressing

Two separate bytes in the frame header (src, dst) — 1 extra byte is nothing on a KB-frame link, buys 254 addresses each + clean code.

| Value | Meaning |
|---|---|
| `0x00` | invalid / unprovisioned (a device with no assigned address cannot impersonate) |
| `0x01` | Master |
| `0xFF` | broadcast |
| `0x02`–`0xFE` | cartridges / additional devices |

- **v1 reality:** point-to-point UART, 2 nodes → addressing is dormant but reserved.
- **Arbitration (now):** **Master-polls.** The Master initiates every exchange; the cartridge speaks only when addressed, and always to the Master (`dst = 0x01`). Since the Master is always the initiator, there is never bus contention.
- **Multi-master (future):** the protocol is transport-agnostic. For a future multi-device coordination plane, move control onto the S31's **TWAI (CAN 2.0/FD)**, which provides hardware bit-wise multi-master arbitration; the src/dst bytes map onto CAN arbitration IDs. **Keep bulk audio off CAN** (tiny frames, low throughput) — bulk stays on the fat point-to-point link.
- If pw_hdlc is ever adopted, these map onto the native HDLC address field.

## 3. Message model (protobuf)

Envelope (conceptual — final `.proto` lives in `/proto`):
```proto
message Envelope {
  uint32 proto_v = 1;
  uint32 sw_v    = 2;
  uint32 src     = 3;   // 1 byte, see §2
  uint32 dst     = 4;
  oneof body {
    Query   qry = 10;   // Master → cartridge: status/caps
    Command cmd = 11;   // Master → cartridge: reboot/shutdown/reset/job-control
    Status  sts = 12;   // cartridge → Master: BOOT/AVA/BUSY/ERR/SHUTDOWN/REBOOT
    Job     job = 13;   // job lifecycle (see §5)
    Ack     ack = 14;   // JOB | CMD
    Boot    boot= 15;   // proto_v, sw_v, HardwareProfile, Capabilities
  }
}
```
Types (Status, Command, Query, Job, Capability, HardwareProfile, Load, Log) as in the prior draft — carried as protobuf messages. `int`→`uint32`/`int64` per proto; timestamps as RFC 9557 strings or epoch-ms.

`JobType`: `stt | stt_rt | trans | trans_rt` — the `_rt` variants are the streaming ones (§6).

## 4. Version negotiation (handshake)

Version is a **range**, negotiated at session open — not a single number.
- Cartridge boots → `Status(BOOT)` → sends `Boot{ proto_v_min, proto_v_max, sw_v, hw, capabilities }`.
- Master picks the **highest common** proto_v. If none:
  - **Master rejects cartridge:** show activation error in UI, then **power-gate the cartridge OFF** (a cartridge you can't talk to is useless and shouldn't draw power). Manual retry available.
  - **Cartridge rejects Master's proto_v:** cartridge enters ERROR — blinks its on-board LED, replies over UART with the error message only, and after a 300 s timeout powers itself down (Master cuts PWR_5V regardless once it observes the mismatch).

## 5. Job lifecycle (unary / server-streaming)

```
PWR_5V:ON
cartridge → STS(BOOT) → STS(AVA)
Master → JOB(PENDING){ job_id, job_type, <audio via chunked transfer §5.1> }
cartridge → ACK(JOB)  (or STS(BUSY) / STS(ERR))
cartridge → JOB(STARTED){ elapsed_s, eta_s }   // periodic, ~1 s, NO payload echo
cartridge → JOB(DONE){ result, elapsed_s } → STS(AVA)
```
Job control: `RESTART_JOB`, `DO_JOB_URGENTLY`, `DO_JOB_NOW` by `job_id`. Every job has a **timeout** (not just boot) — a wedged `stt` is truncated and reported FAILED.

### 5.1 Chunked payload transfer (don't hand-roll — the pattern is old)
The audio blob is transferred as a **numbered-chunk session**, not a single giant message:
- Open: `{ transfer_id, total_chunks, chunk_bytes }` — receiver pre-allocates and knows exactly how many to expect.
- Chunks: sequentially numbered, each CRC'd by the frame layer (§1).
- Receiver may request a specific chunk `k` on mismatch (selective retransmit); resume from last good chunk on interruption.
- This is XMODEM/YMODEM/ZMODEM / MCUmgr-SMP territory — **adopt an existing block-transfer pattern**, don't reinvent. With streaming RPC (§6) the same channel carries `stt_rt` frames.

## 6. Real-time streaming (future: `stt_rt` / `trans_rt`)
Modeled on pw_rpc **bidirectional streaming**: Master opens a stream, pushes audio frames as they're captured, cartridge emits partial/final transcription frames back, either side ends with a status. This is why the transport is chosen streaming-capable *now* — the `_rt` job types become a bidi RPC, not a transport rewrite. Backpressure + framing already handled by the transport layer.

## 7. Unresponsive cartridge (escalation)
`RESET` (clear cartridge state, no OS reboot) → `REBOOT` (with 30 s STS(BOOT) wait, then 60 s poll) → power-cycle (`PWR_5V:OFF`, 5 s, `ON`) → back to boot wait. As in the prior draft; unchanged.

## 8. Security note
Per SPEC §7.9: the cartridge never touches storage or keys. Audio crosses this link **in the clear** as volatile RAM data — the same plaintext both chips already hold. The link is inside the sealed enclosure; encrypting it adds nothing against the threat model (anyone who can tap the FFC can probe every bus). Confidentiality lives at storage (AES-XTS) and, later, radio — not here. CRC is for line integrity, not authentication.

## 9. Cross-references
- Connector pinout, power gating, 5 V-on-carrier: SPEC §5 (J4).
- Recording formats fed to STT: SPEC R13 (Voice/Full/Lossless).
- Roadmap (cartridge = v1.5/v2): SPEC §4.
