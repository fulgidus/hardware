# SPEC — Full-Offline AI Dictaphone ("maximum privacy")

**Rev:** 1.4 (VCNL4040 prox+ALS added; ear-mode + auto-brightness) · **Date:** 2026-07-13 · **Status:** pre-schematic
**Legend:** ✅ resolved · ⚠devkit = needs physical S31 to measure/verify · companion doc: PIN_MAP.md
**Silicon baseline:** ESP32-S31 (datasheet v0.2 PRELIMINARY — all ⚠devkit items must be re-checked against datasheet ≥1.0)

---

## 1. Rationale

Dictaphone with **fully on-device** AI transcription: no data ever leaves user-owned hardware. Recording always takes priority over any other function. Strong encryption at rest. Extensible platform (inference cartridge, opportunistic wireless integrations).

## 2. Requirements (testable)

| ID | Requirement | Acceptance criterion |
|---|---|---|
| R1 | Mono audio, 48 kHz / 16-bit capture, **Opus** (Ogg) or **FLAC** per profile (R13) | playable file; bitrate per active profile |
| R2 | Reliable timestamping of notes | RTC drift < 2 s/month (RV-3028) |
| R3 | Local transcription en-US + it-IT (v2) | WER targets: en ≤ 12 %, it ≤ 18 % on proprietary "real dictaphone" test set |
| R4 | Recording is **always top priority** | REC never blocked/degraded by transcription or transfers |
| R5 | Encryption at rest | AES-XTS vault; keys never leave the S31 key manager |
| R6 | True-off + deep sleep + quick activation | off = 0 µA (disconnect switch); wake→first sample with pre-roll from PSRAM ring buffer |
| R7 | ≥ 72 h on profile: deep sleep + one 5-min note per hour | bench-verified, budget §6 |
| R8 | microSD exFAT as interchange format | dual-LUN USB MSC: open partition always visible, vault only when unlocked |
| R9 | Crash-safety without journaling | max loss = last segment (≤ 8 s); archive never corrupted |
| R10 | Hardware-enforced stealth mode | physical slider: no buzzer, no LEDs (or minimal), haptics only |
| R11 | Eyes-free feedback | distinct haptic patterns for start/stop/battery; no haptics during REC |
| R12 | **VOX mode: autonomous voice-activated recording** | armed-VOX standby ≤ 200 µA system; voice onset→first sample ≤ 1 s; silence timeout closes file crash-safe and re-arms; false-trigger rate tunable (AAD D2 thresholds/min-pulse). Lawful use is the user's responsibility (jurisdiction-dependent) |
| R13 | **Configurable recording profiles** (leverage T5838 quality) | Three presets, config on SD; per-mode default binding: **Voice** (Opus ~24–32 kbps, speech-optimized — for small SD / edge cases), **Full** (Opus fullband 48–64 kbps — **default**; best for ambient/VOX/multi-speaker + feeds ASR better), **Lossless** (FLAC 48/16 — opt-in archive). Encoder + hardware ASRC handle all; profile switch must not violate R4. File-size metadata leakage is a non-issue (FW is open-source ⇒ encoding public); optional block padding available but not required |

## 3. Architecture

```
                        ┌────────────────────────────────────────────┐
 I2S mic (flex+foam) ───┤                                            │
 microSD (SDMMC 4-bit)──┤   ESP32-S31-WROOM-3                        │── antenna on protruding
 12-pad touch keypad ───┤   sensing · storage · keys · radio · sleep │   tab (keyring hole,
 REC/STEALTH sliders ───┤   AES-XTS on-the-fly · USB MSC dual-LUN    │   copper-free bumper, TVS)
 LTC2954 / disconnect ──┤                                            │
                        └──────┬──────────────┬──────────────────────┘
                          USB-C (HS,      14-pin FFC expansion
                          mux DNP)        UART 5M + VBAT_SW + I2C-B + USB(DNP)
                                                │
                                     ┌──────────┴──────────┐
                                     │ CARTRIDGE v1.5/v2   │  5V boost + SoM,
                                     │ (Core3506 / CM3S)   │  immutable rootfs,
                                     │ power-gated, RAM-only│ Moonshine/ASR
                                     └─────────────────────┘
```

Principles: the SD card and the keys belong **exclusively** to the S31. The cartridge receives audio in RAM over the link, returns text, and gets powered off. Two separate I2C buses per power domain (I2C-A always-on, I2C-B switched).

## 4. Roadmap (two lanes)

**HW/FW lane:** v1 secure dictaphone (this SPEC) → v1.1 push backup + NTP + signed OTA → v1.2 wireless admin → v1.3 companion export (descoped) → v1.5 cartridge carrier → v2 on-device transcription.
**ML lane (starts NOW, in parallel):** it-IT/en benchmarks on Radxa Zero 3 + Core3506: Moonshine tiny/base/medium-streaming (en); fine-tuned Moonshine-it vs whisper small vs zipformer vs Parakeet 0.6B (it). Metrics: WER, RTF, peak RAM, boot-to-first-token, **Wh/note including boot**. The outcome selects the cartridge silicon (512 MB vs 2 GB class).

---

## 5. CRITICAL TABLE — BOM + Pin Map + Power (min/max)

Conventions: currents at 3.3 V unless noted; **Sleep** = system deep sleep (switched rails OFF); **Typ** = typical draw in the relevant active state; **Max** = peak. ⚠devkit = to be verified (preliminary datasheet or bench measurement pending).

| Ref | Component / P/N | Function | S31 pins / signals | Rail | I sleep | I typ | I max | € | Notes |
|---|---|---|---|---|---|---|---|---|---|
| U1 | **ESP32-S31-WROOM-3-N16R16V** (16 MB flash / **16 MB PSRAM** octal 1.8 V, in-module) ✅ verified WROOM-3 DS v0.1: all SKUs = 16 MB PSRAM (N8R16V/N16R16V/N32R16V differ in flash only) | MCU, radio, crypto, USB | — | 3V3 | 15–25 µA ⚠devkit | 45–90 mA (REC+Opus) | 350 mA (WiFi TX) | 5.0 | 99-pad castellated, 22×30×3.5 mm, PCB antenna, keepout on one 22 mm edge (aligns with tab plan). PSRAM 16 MB = generous pre-roll ring buffer. **No external 1.8 V-domain GPIO trap** (PSRAM 1.8 V is module-internal, unlike S3 IO47/48). ⚠ **Two distinct 1.8 V domains — do not conflate:** (a) PSRAM 1.8 V = internal, no external impact; (b) **mic 1.8 V = external, REQUIRED** (U15 LDO + U16 shifters, see M1). **DAC on IO4/IO5** + **hardware ASRC** (→48 kHz) — see BZ1, M1 |
| U1a | · 12-pad touch keypad | PIN/UI | **GPIO6–17** + VREF_TOUCH; GPIO18–19 spare | — | (incl. U1) | — | — | 0 | pads ≥10 mm under 1.6 mm FR4; calibrate with assembled case |
| U1b | · USB OTG **HS** | MSC dual-LUN / cartridge | **dedicated pins 44/45** | — | — | — | — | — | single OTG: mux U14 |
| U1c | · USB Serial/JTAG | debug/flash | GPIO33–34 (reserved) | — | — | — | — | — | FS, CDC/JTAG only |
| U1d | · strapping | boot | GPIO60–61 | — | — | — | — | — | tolerant functions only |
| U1e | · SDMMC 4-bit | microSD link | **DEDICATED module pins** SD_D0–D3/CLK/CMD (module pins 27–32) — ✅ verified WROOM-3 DS: separate from GPIO bank, **zero GPIO cost, no touch conflict**. D3 pull-up mandatory | — | — | — | — | — | chip Card-1 (GPIO20–25 internally). 3.3 V rail (1.8 V SD switchable if UHS wanted later) |
| U1f | · I2S0 (PDM RX) + **ASRC** | mic in | 2 GPIOs via matrix (IO46/47), CLK out + DATA in | — | — | — | — | — | ✅ PDM RX confirmed (WROOM-3 DS §5.2.2.4). **Hardware ASRC** converts PDM sample rate → 48 kHz for Opus, CPU-free |
| U1g | · I2S1 | codec/amp | 3–4 pins via matrix | — | — | — | — | — | 4th pin if ES8311 (ADC) |
| U1h | · I2C-A always-on | RTC, fuel gauge | 2 pins | 3V3 | — | — | — | — | pull-ups to 3V3 |
| U1i | · I2C-B switched | OLED, DRV2605L, cartridge ID EEPROM, VCNL4040 prox/ALS | 2 pins | EN_PERIPH | — | — | — | — | pull-ups on switched rail (prevents back-powering) |
| U1j | · UART1 | cartridge link, 5 Mbaud | 2 pins (on FFC) | — | — | — | — | — | 1.2 MB/note ≈ 2.5 s |
| U1k | · wake inputs (LP) | REC(IO0) / STEALTH(IO1) / RTC-INT(IO2) / MIC_WAKE-AAD(IO3) | **LP_GPIO0–3** | — | — | — | — | — | only IO0–IO7 are LP/wake-capable (8 total). IO4/IO5=DAC, IO6/IO7=LP_I2C-A. VBUS/PB-INT → HP GPIO w/ EXT1 wake |
| U1m | · LP_I2C-A (always-on) | RTC + fuel gauge, readable by LP core in sleep | IO6(SCL)/IO7(SDA) | LP domain | — | — | — | — | LP_I2C lets LP core poll fuel gauge during deep sleep |
| U1l | · touch + control | **12 touch pads IO8–IO19** (full PIN pad, no matrix); KILL, marker, LED(RMT), buzzer(DAC), EN×5, codec/jack, PGOOD on IO42–61 | see PIN_MAP.md | — | — | — | — | — | ~42–45/54 usable GPIOs; audio/mic relocated to high GPIOs to free touch bank |
| M1 | **TDK T5838** (PDM, 68 dBA SNR, EIN 26 dBA SPL, AOP 133 dB SPL) on flex + foam | bottom-port MEMS mic, **sole mic** (no fallback) | → I2S0 PDM RX (IO46/47) + WAKE→**LP_GPIO3 (IO3)** + THSEL(IO48) | **1V8_MIC (U15)** | 0.8–1 µA (CLK off) / **110 µA (AAD D2 armed)** | 0.31 mA (HQ, CLK 2.0–3.7 MHz) | 0.34 mA | 2.0 | ✅ DS-000383: **VDD 1.62–1.98 V STRICT (abs max 1.98 V)** ⇒ U15 rail + U16 shifters mandatory. AAD D2: voice-band detect w/ CLK OFF, abs threshold 40–87 dB SPL, relative +3…+20 dB adaptive, min-pulse reject; config via THSEL one-wire (lost on power cycle ⇒ reconfig at boot). Mic wake-up 6 ms |
| U15 | **TPS7A02-018** LDO 1.8 V | always-on mic rail | 3V3→1V8_MIC | — | Iq 25 nA | — | 200 mA | 0.4 | powers M1 + shifter B-side; also cleans mic supply (PSRR) |
| U16 | **SN74AXC2T45 ×2** level translators | CLK+THSEL (3V3→1V8), DATA+WAKE (1V8→3V3) | between U1 and M1 | 3V3 + 1V8_MIC (always-on) | ~2–5 µA total | — | — | 0.6 | REQUIRED: 3.3 V on mic pins violates abs max; 1.8 V VOH (≈1.26 V min) unreadable by 3.3 V GPIO. Must stay powered in deep sleep for WAKE path |
| J1 | microSD push-push slot + TVS array | storage | → SDMMC | **EN_SD** | 0 (rail off) | 30–60 mA (write) | 100–200 mA burst | 1.5 | rail ON in "armed"; re-init ~150 ms from deep sleep |
| U2 | **RV-3028-C7** + supercap/coin | RTC | I2C-A + INT→LP_GPIO2 | 3V3 | 0.05 µA | 0.05 µA | 0.1 µA | 2.0 | R2; NTP sync from v1.1 |
| U3 | **MAX17048** | fuel gauge | I2C-A | 3V3 | 3 µA (hib.) | 23 µA | 23 µA | 1.0 | |
| U4 | **BQ24074** | charger + power-path | VBUS, /CHG, ISET | VBAT | 1–6 µA from batt. | — | 1.5 A charge | 1.5 | runs while plugged; powers system from VBUS |
| U5 | **TPS62840** | 3.3 V buck | VBAT→3V3 | — | Iq 60 **nA** | η > 90 % | 750 mA | 1.0 | key part for R7 |
| U6 | **LTC2954** | long-press on/off + kill | PB, INT→HP GPIO, KILL→**EN (pin 5)** | VBAT | **~7 µA typ** ✅ (LTC2954 datasheet) | 7 µA | — | 2.5 | shutdown always graceful. **Coordinate with EN RC-delay** (R=10 k, C=1 µF per WROOM-3 DS): LTC2954 KILL drives the same EN node — verify RC + kill timing don't fight at power-up |
| SW1 | Recessed slide disconnect | **true-off** | in series with VBAT (upstream of everything) | — | **0 µA** | — | — | 0.5 | R6 |
| U7–10 | **TPS22918 ×4** | load switches EN_SD / EN_PERIPH / EN_AUDIO / EN_LED | EN from GPIOs | — | < 1 µA each (off) | — | 2 A each | 2.0 | |
| U11 | **TPS22919** or sized P-FET | expansion VBAT_SW | CART_EN | — | < 1 µA | — | ≥ 2 A ⚠size it | 0.5 | SoM peaks 1.5–2 A |
| H1 | Coin LRA + **DRV2605L** | haptics (primary feedback channel) | I2C-B + trigger | EN_PERIPH | 0 (rail off) | 60–90 mA burst 10–30 ms | 150 mA | 2.0 | anchored to case; **never during REC** (R11) |
| BZ1 | Piezo on **DAC (IO4/IO5)** — no charge-pump | alarms/findability, tones/melodies | DAC ch0 (IO4) | 3V3 | 0 (idle) | 3–10 mA burst | 20 mA | 0.2 | ✅ simplified: WROOM-3 has hardware DAC w/ sine LUT → PAM8904 + LEDC path **dropped**. If louder SPL needed later, add a small piezo driver on the DAC output (footprint only) |
| A1 | **ES8311 mono codec + class-D amp** (e.g. MAX98357A as amp, or PAM8302) | playback / fun audio + **TRRS analog mic-in** | I2S1 (4-wire: BCLK/LRCLK/DIN/DOUT) + I2C-B ctrl + EN | **EN_AUDIO** | 0 (rail off) | 30–120 mA | 350–500 mA (speaker peak) | 2.5 | ✅ DECIDED: ES8311 gives ADC (line/lavalier in via TRRS) + DAC in one chip; auto-mute speaker on jack detect; codec ctrl on I2C-B |
| J2 | **TRRS CTIA** jack + detect (+ mic bias if ES8311) | headphones / lavalier | jack-det GPIO | EN_AUDIO | 0 | 5–30 mA (headphones) | 60 mA | 1.5 | tallest part: co-design with cell |
| D1 | **OLED grayscale, SSD1327-class** (128×128, 16-level gray, I2C) | status/PIN UX; waveform, anti-aliased type, brightness-dimmable | I2C-B | EN_PERIPH | 0 (rail off) | 8–20 mA | 30 mA | 3.0 | ✅ grayscale (not boolean SSD1306) → real AA + luminance control; stays on I2C-B (no new pins). White emitter; dim = mimicry in dark environments. 1.5" size TBD vs space; re-init on wake |
| D2 | **SK6812MINI-E ×2–3 RGBW** | status LEDs | 1 GPIO (RMT ✅ standard peripheral, S31 feature list confirms) | **EN_LED** (from VBAT + series diode) | 0 (rail off) | 5–15 mA | ~60 mA/px (full white) | 0.5 | ~1 mA/px quiescent ⇒ rail must be cut in sleep |
| SW2 | REC slider (sub-min SPDT) | recording on/off | **LP_GPIO0** | — | 0 | — | — | 0.6 | state readable by thumb; wake source |
| SW3 | STEALTH slider | hw-enforced profile (R10) | **LP_GPIO1** | — | 0 | — | — | 0.6 | |
| SW4 | **Quiet** low-profile tactile (EVQP0-class, 100–160 gf) | marker | 1 HP GPIO | — | 0 | — | — | 0.3 | board farthest from acoustic port; DSP trim possible |
| Q1 | **Phototransistor** + comparator (e.g. ALS-PT19 + tiny comp) | tamper-evidence (enclosure open in light) | → LP_GPIO6 (wake) | **always-on** | < 1 µA | — | — | 0.1 | RoHS-clean (no Cd/LDR); armed post-enrollment; maintenance-mode disarm |
| Q2 | **VCNL4040** (IR proximity + ALS, integrated emitter, I2C) | ear-mode proximity (mute touch + route to earpiece + screen off during playback) **and** ambient-light → OLED auto-brightness | I2C-B + INT→HP GPIO | EN_PERIPH | 0 (rail off) | ~few µA–0.2 mA gated | — | 0.9 | modulated IR emission → built-in ambient-light rejection (the "coded emission" is internal). Prox = playback-time only (not a wake source). ALS bonus = auto-dim for discretion. INT not wake-critical |
| J3 | USB-C (anchored mid/TH) + 5.1 k CC ×2 + USBLC6 | charging + MSC | → U1b via U14 | VBUS | 0 | — | 1.5 A | 1.4 | |
| U14 | USB HS mux (FSUSB42-class) — **DNP in v1** | USB-C ↔ cartridge | 44/45 ↔ J3/FFC | 3V3 | < 1 µA | — | — | 0.4 | footprint provisioned |
| B1 | LiPo **LP103395 3700 mAh** (~10×34×95 mm) + PCM | power source | → SW1 → U4/U5 | — | self-discharge | — | — | 6.5 | ✅ DECIDED: length-dominant (classic dictaphone form); sets device long axis. Charge time from BQ24074 @1.5 A ≈ 2.7 h (0.4C) — consider higher-current charger if faster needed |
| J4 | 14-pin 0.5 mm FFC | cartridge expansion | VBAT_SW×2, VBUS_5V, CART_EN, PGOOD, UART×2, I2C-B×2, USB±(DNP), GPIO, GND×2 | — | 0 | — | — | 0.4 | 5 V boost lives **on the carrier** (DNP in v1) |
| MEC | 3–4 PCB case stack + antenna tab/keyring + screws + mic flex | mechanics | 3D antenna keepout; generous slot radii | — | — | — | — | 8–12 | ESD: TVS on everything exposed |

**Prototype BOM total: ~€43–48** (cartridge excluded; buzzer path simplified via on-chip DAC, PAM8904 dropped).

## 6. Power states and R7 verification (72 h)

| State | Active contributors | Estimated I | Notes |
|---|---|---|---|
| True-off (SW1 open) | nothing | **0 µA** | cell self-discharge only |
| Off-latch (LTC2954) | U6 + U4 leak + U5 Iq | ~8–12 µA | everyday shutdown |
| **Deep sleep** | U1 + U2 + U3(hib) + U6 + U5 + leakage | **~30–55 µA** ⚠devkit | all EN_* rails OFF |
| **Armed-VOX** (deep sleep + T5838 **AAD D2**) | U1 sleep + M1 AAD D2 (110 µA) + U16 shifters | **~145–170 µA** | mic asserts WAKE on voice-band activity (CLK off); onset→first sample ~0.4–0.7 s ⚠devkit (S31 boot w/ secure boot + SD init 150 ms + mic 6 ms); AAD A variant (20 µA, cruder 60 dB SPL threshold) for loud-env scenarios |
| Armed-preroll (light-sleep + ring buffer) | U1 light + M1 LP + SD idle | 2.5–5 mA ⚠devkit | zero-loss pre-roll; use sparingly (timeout policy) |
| **REC** | U1 encode + M1 + SD write | 60–110 mA avg | SD peaks 200 mA |
| REC + headphones | + A1/J2 | +10–40 mA | |
| USB-MSC / charging | from VBUS | n/a for R7 | on-the-fly XTS: verify AES vs SD throughput ⚠devkit |
| Cartridge active (v1.5+) | VBAT_SW | 0.8–2 A burst | prefer while charging (configurable policy) |

**R7 verification** (requirement profile: 72 notes × 5 min, deep sleep otherwise):
REC 6 h × 90 mA = **540 mAh** · deep sleep 66 h × 0.05 mA = **3.3 mAh** · UI/wake/haptics overhead ≈ **50 mAh** → **≈ 595 mAh** on 3700 mAh cell = **>6× margin**. ✅ R7 vastly exceeded; the 72 h profile could run ~5× over before empty. Armed-preroll abuse (120 mAh/day) is negligible at this capacity.
**R12 (VOX) standby math:** armed-VOX ≈ 0.16 mA → 3700 mAh / 0.16 mA ≈ **~23000 h (>2.5 years) of pure listening standby** — cell self-discharge and calendar aging dominate entirely. With 2 h/day triggered recording (~180 mAh/day) → ~2–3 weeks per charge. False triggers remain the wildcard (tune AAD D2). **Note:** the 3700 mAh cell is sized for real-world all-day use and long VOX vigils, not for R7 — R7 was never the binding constraint.

## 7. Security architecture

### 7.1 Write-free / read-protected asymmetry (core model)
Recording NEVER requires a secret — the device is a **locked mailbox**: anyone holding it can post (record), only the key holder can open (read). Implemented with **asymmetric sealing**, not a shared symmetric key:
- **Write path (always available, incl. VOX, incl. lockout):** each note is sealed with the vault's **public key** (X25519/ECIES-style). The public key is not a secret — it may sit in cleartext flash/RAM. An armed or stolen device therefore holds **no sensitive key material**: a finder can seal note N+1 but cannot read notes 1..N. This closes the symmetric-mailbox gap (where the write key could also read).
- **Read path (gated):** decryption needs the **private key**, which does not exist in usable form on an at-rest device — it is unwrapped only on successful PIN/PUK.

### 7.2 Three-ring key hierarchy (PIN is never the key)
The indirection that makes PIN-change cheap and data immovable:
```
PIN/passphrase ──unlocks──▶ KEK ──unwraps──▶ vault PRIVATE key ──reads──▶ data
      (wrapper)              (key-encryption key)     (fixed for vault life)      (sealed to PUBLIC key)
```
- **One asymmetric keypair per vault, fixed for life.** Generated at enrollment, never rotated. Public seals (write), private reads. Data is sealed once and never re-touched until deliberate read.
- **Private key stored wrapped**, not in clear: `priv_wrapped = wrap(private, KEK)`. Multiple independent wrappers of the *same* private key may coexist:
  - `priv_wrapped_by_TEE` — KEK custodied by S31 key manager (convenient; TEE-dependent).
  - `priv_wrapped_by_passphrase` — `KEK = Argon2id(passphrase)`, USB-entered (paranoid; TEE-independent).
  - This is the "two security levels" idea done right: **two wrappers of one key, not two partitions and no data migration.**
- **Change PIN/passphrase = re-wrap ~32 bytes**, never re-encrypt data: unlock private with old wrapper → re-wrap with new KEK → overwrite `priv_wrapped`. Cost is constant regardless of vault size. (Rejected naïve scheme `key = Argon2id(PIN)` would force re-encrypting everything on PIN change — the reason the middle ring exists.)
- Data at rest under the private-key domain; bulk symmetric layer (**AES-XTS**, HW AES on-the-fly) for full-partition/MSC performance, its key sealed under the vault public key.
- **PUK (strong):** authorizes recovery from lockout / re-wrap (7.5). **PIN (quick):** unwraps the private key into RAM for a **user-defined unlock window** (7.3).

### 7.3 Unlock window & deep-sleep policy (user-defined)
The unwrapped **private key** lives in volatile RAM only while awake+unlocked. Timeout configurable (5 min / 1 h / until-sleep). Whether it survives deep sleep is a **user-defined** setting (comfort vs. exposure); default zeroizes on deep-sleep entry. Any tamper event overrides toward secure regardless. Writing/VOX are unaffected (public key only).

### 7.4 PIN → PUK → (lockout | wipe) escalation (SIM-style, recoverable)
- **Normal:** PIN unlocks reading. **Writing/VOX survive every state below.**
- **Lockout ("curl up"):** triggered by N wrong PINs (default 3) OR tamper Lv3 OR duress-PIN. Action: zeroize read key from RAM (data stays encrypted+intact), increment monotonic counter, close reading. Recover with PUK.
- **Wipe (opt-in, default OFF):** destroys the wrapped master key (data → noise, permanent). Triggered only if user-enabled, or after M failed **PUK** attempts (default 10).
- **Anti-rollback:** attempt counter is the S31 **hardware monotonic counter** (anchored to key manager / secure boot), so a power-cycle or SD-restore cannot rewind it.

### 7.5 PUK verification (single-hash + hardware rate-limit)
No progressive work-factor, no artificial sleeps — both were security theater here (see 7.8). The PUK is a **local authorization factor** for a *live* device, not a key-derivation secret (keys are custodied, not derived — 7.1/7.8). Its only realistic threat is on-device online guessing, countered by the hardware monotonic counter, not by CPU cost.
```
stored_hash = Argon2id(PUK, salt, N_modest)      # once at provisioning; keeps PUK out of a partial dump
verify(candidate):                                # runs in secure world
    ok = constant_time_eq(Argon2id(candidate, salt, N_modest), stored_hash)
    if ok:  atomically reset monotonic counter, release recovery
    else:   atomically increment monotonic counter, apply backoff/lockout per 7.4
```
- **Rate-limit = monotonic counter** (anti-rollback, survives power-cycle/SD-restore), not per-hash cost.
- `verify-OK → reset` is a single atomic transaction inside the secure world; "reset counter" is never a separately callable verb.
- Change-PUK is a distinct explicit op (verify old → new stored_hash → write).
- Secrets zeroized explicitly (`mbedtls_platform_zeroize`).

### 7.5b Auth flow, duress hashing & session model (TEE as authority, UI as thin client)
The Rich-world UI holds **no policy and no secrets**. All auth logic lives behind the secure-world wall; the UI is a dumb client that asks and obeys.

**Duress-PIN is hashed like any other secret** — NOT stored in clear. All candidate secrets (real PIN, PUK, duress) run the **same Argon2id, same cost, same path**; the outcome branches only *after* the identical-duration computation. This makes duress temporally indistinguishable from a normal attempt (a cleartext `memcmp` for duress would be microseconds vs. ~1 s Argon2id → observable side-channel revealing that a duress exists). Hashing the duress is what makes it invisible.

**Duress is accepted at every auth prompt** (PIN prompt AND PUK prompt) — a universal "open it" response under coercion, so the user needn't recall which trap-secret applies in which state. Same hash-compare path, so no special-casing by context.

**API (secure world):**
```
initiate_unlock() → { code: "pin"|"puk", remaining: number, err?: ErrorCode }
submit_secret(input) → UNLOCK_OK | UNLOCK_KO | ERROR | REBOOT_REQUIRED
                       (+ {code, remaining, err} payload on KO/ERROR)
```
- **UNLOCK_OK:** secret matched → TEE unwraps private key into its own protected RAM, opens a **session**, returns an **opaque session handle** (see below).
- **UNLOCK_KO / ERROR:** payload tells the UI what to prompt next; the UI has zero lockout logic — after N fails the TEE itself escalates the next `code` to `"puk"`.
- **REBOOT_REQUIRED:** the *only* duress-visible outcome, and defined UI-side as a state that *could* have benign causes. On a duress match the TEE **crypto-erases the private-key wrappers BEFORE returning** (destruction complete & atomic at return); it then returns REBOOT_REQUIRED. The UI shows a generic "Hardware error, rebooting…" and reboots — it never holds a "duress happened" flag. On next boot the device finds no wrappers → boots virgin (first-run). No persistent duress state exists to find forensically.
- **`remaining` caveat:** exact attempt count is itself a signal; in Discreet/coercion contexts the TEE may return a coarse `low_attempts` bool instead of the true number. (Design decision, per profile.)

**Session handle (opaque, NOT self-contained — deliberately un-JWT):**
- The handle the UI holds is a **dumb opaque token** (random index). It carries **no `valid_until`, no claims, nothing interpretable** — unlike a JWT. All session state (validity, expiry, which private key) lives **inside the TEE**, indexed by the handle. A Rich-world RAM dump yields only a meaningless ticket, not a forgeable/readable session.
- The UI never holds the PIN/PUK for reuse. After UNLOCK_OK it uses the **handle** for all subsequent TEE ops (read/decrypt/export); the private key stays in TEE-protected RAM for the unlock window (7.3).
- **Sliding expiry, TEE-managed:** legitimate activity slides the internal expiry forward; inactivity lets it lapse. No separate "refresh token" — renewal is a side effect of use, handled behind the wall.
- **Invalidation is opaque to the UI:** timeout, deep-sleep, or tamper all make the TEE zeroize the private key and invalidate the handle. The next op returns UNLOCK_KO `{code:"pin"}`; the UI restarts from `initiate_unlock` without knowing *why* (expiry? sleep? intrusion?). That ignorance is a feature.
- **PUK re-enables the PIN as policy, not by capturing it:** unlocking via PUK resets lockout (7.4) so the TEE accepts the PIN again going forward. The UI never learns the PIN; "next prompt is `code:pin`" means the TEE will accept it, not that the UI stored it.

### 7.6 Tamper-evidence (phototransistor, not LDR)
Enclosure-open detection **in lit environments** — a tamper-*evident* layer, not a wall (does not catch dark-room opening, JTAG on exposed pads, or SD chip-off; those are covered by AES-XTS on the card).
- **Sensor:** phototransistor/photodiode (RoHS-clean, µs response, <1 µA in comparator mode) on the **always-on rail** → LP_GPIO wake. Armed only after first enrollment.
- **Lv1 (always):** tamper → zeroize the unwrapped private key from RAM, force PIN.
- **Lv2 (always):** append-only tamper log with RTC timestamp in vault → owner learns of the intrusion at next unlock (this is what makes it *evident*).
- **Lv3 (opt-in):** tamper counter → after threshold (or combined with duress) triggers lockout/wipe per §7.4.
- **Maintenance mode:** owner disarms tamper (from menu, while unlocked) before legitimately opening for SD/battery service — no false alarm.

### 7.7 Duress-PIN → crypto-erase (optional, set at provisioning)
A decoy PIN, indistinguishable from a normal PIN until entered. On entry:
1. **Destroy every wrapper of the vault private key** — all of `priv_wrapped_by_TEE` and `priv_wrapped_by_passphrase` (few bytes each, in OTP/protected RAM/flash — the one place physical overwrite is meaningful, not wear-leveled bulk). Millisecond-scale, **atomic, irreversible**. Without any wrapper, the private key can never be reconstructed; the public-sealed data is permanently unreadable.
2. Vault is now mathematically unrecoverable — no re-encryption, no bulk overwrite (sealed data without the private key = noise). Pulling the battery after this point saves nothing.
3. Cover message: **"Hardware error. Rebooting in 5 s…"** — countdown is pure theater; destruction already completed at step 1. Implies no vault exists, justifies a clean reboot.
4. Factory reset → boots as a virgin device (first-run setup). The duress-PIN died with the vault; a reset device has no PINs and no special state. No way back, ever.

**Crypto-erase completeness requirement:** every datum must be sealed under the vault public key — no plaintext copies on the open partition, in caches, or in half-written notes. Disciplined by the write/read asymmetry (7.1).

### 7.8 Root assumption — data-at-rest reduces to the private-key wrappers
Stated plainly: **data-at-rest confidentiality reduces to whatever protects the vault private key.** In the default TEE-only posture, that is the S31 secure world — if the TEE is defeated (glitch, side-channel, chip-off), `priv_wrapped_by_TEE` yields the private key directly and all data with it; PIN/PUK hashes are irrelevant then (attacker holds the key, not a hash to crack). This is the deliberate cost of the **custodied-key (mailbox) model**, chosen for **write-without-unlock** (7.1). **Escape hatch:** enabling `priv_wrapped_by_passphrase` (7.2) adds a wrapper whose security is a strong USB-entered passphrase, **independent of the TEE** — at the cost of entering it to read. The passphrase-derived-key alternative (work-factor would matter) is incompatible with blind recording and was rejected as the *sole* mechanism, but survives here as an *optional second wrapper*. Consequence: **item 9.c#18 (S31 secure-world maturity) is the most load-bearing assumption for the default posture; the passphrase wrapper is the hedge.**

### 7.9 Other
- **Cartridge:** never touches storage or keys; audio in volatile RAM only, returns text, powered off. Signed immutable rootfs.
- **Stealth:** physical GPIO, not a software preference.
- **Open-partition caveat:** firmware never writes recordings to the clear partition by default; documented foot-gun.
- **Hidden volumes (deniable encryption):** firmware-only option, annotated for v1.x.

## 8. Storage & crash-safety (no journaling — UDF ruled out: no ESP-IDF implementation exists)

1. Self-healing container on truncation: **Ogg/Opus** (checksummed pages) recovers to last valid page; **FLAC** (Lossless profile) is framed with per-frame sync codes + CRC ⇒ decoders resync to last intact frame. Both degrade gracefully to "lose only the tail".
2. Contiguous pre-allocation + append-only writes + metadata sync every 4–8 s (applies to all profiles).
3. Boot-time recovery: trim to last valid page/frame, rename.
4. Bulk capacitance on EN_SD + brownout detect for the pathological power cut.
5. littlefs (power-loss-safe) on internal flash for config/state/job queue.
6. **Note:** Lossless writes ~5–10× more data/s than Voice → larger crash tail in absolute bytes, but still bounded by the sync interval; R4 (recording priority) unaffected at 3700 mAh.

## 9. File naming, metadata & markers

### 9.1 Filename
Pattern: **`${id}.${timestamp}.${ext}`** where
- `id` = short unique base32/hex handle (collision-free, primary key; survives rename/export).
- `timestamp` = `YYYYMMDDThhmmss.sss±zzzz` — millisecond precision, numeric UTC offset, **no `:` and no `Z`** (exFAT-safe; `Z` and `±zzzz` are mutually exclusive so the offset form is used). Offset chosen over `Z` for forensic locality (records where, not just when).
- `ext` = `opus` (Voice/Full) or `flac` (Lossless).
- Example: `a1b2c3.20260713T143002.317+0200.opus`
- The **canonical RFC 9557** form (with `:` and named zone, e.g. `2026-07-13T14:30:02.317+02:00[Europe/Rome]`) lives in metadata, not the filename.

### 9.2 Container metadata (Vorbis comment for Opus; FLAC native tags)
User-facing, human-authored fields live **inside the container**, not the filename:
- `TITLE` — user-chosen name (optional; used on export/upload/share, else `id` shown).
- `REC_PROFILE` — voice | full | lossless.
- `RECORDED_AT` — canonical RFC 9557 timestamp.
- `TZ` — named zone if known.
- `DURATION`, `SAMPLE_RATE`, encoder version, firmware version.
- These are **encrypted at rest** (inside the AES-XTS vault) → external tools see them only after unlock. Consistent with the mailbox model: metadata is as private as the audio.

### 9.3 Markers (chapter points from the marker button)
- **Primary: chapter markers** in-container (`CHAPTERxxx`/`CHAPTERxxxNAME` Vorbis comments for Opus; FLAC cuepoints/tags) — *written at finalization*, not mid-stream, to avoid rewriting the header of an append-only file.
- **During recording: sidecar `${id}.${timestamp}.jsonl`** — one JSON object per line, appended live on each marker press (`{"t_ms":123456,"label":null}`). Append-only JSONL is crash-safe by construction (a torn last line is discarded on parse) and matches the recording's own crash model.
- **Reconciliation:** at stop / next boot after power-cut / recovery, the sidecar is merged into container chapters; sidecar retained until merge confirmed, then optionally kept as source-of-truth log. This gives markers that survive a mid-recording power loss — the container chapters alone would not.

## 10. Open items

### 9.a RESOLVED (via datasheet — WROOM-3 DS v0.1 + S31 Series DS v0.2 now in hand)
| # | Item | Resolution |
|---|---|---|
| 1 | SDMMC pins | **Dedicated module pins** SD_D0–D3/CLK/CMD (27–32); zero GPIO cost, no touch conflict; D3 pull-up |
| 2 | RMT on S31 | Standard peripheral; 1 GPIO (IO49) drives RGBW chain |
| 3 | WROOM-3 memory | **All SKUs = 16 MB PSRAM**; target **N16R16V** (16 MB flash). PSRAM ring buffer generous |
| 4 | PDM RX | Confirmed (WROOM-3 DS §5.2.2.4); + hardware **ASRC** → 48 kHz CPU-free |
| 5 | T5838 supply | 1.62–1.98 V strict → U15 LDO + U16 shifters |
| 6 | LTC2954 Iq | ~7 µA typ |
| 7 | Audio A1 | ES8311 + class-D |
| 8 | Battery | LP103395 3700 mAh |
| 9 | **Pin map** | **FROZEN** in PIN_MAP.md from real datasheet: 12 touch pads IO8–19, LP wake IO0–3, LP_I2C IO6/7, DAC IO4/5, audio/mic on IO42–48, control IO49–61 |
| 10 | Buzzer | **On-chip DAC (IO4)** → PAM8904 dropped |
| 11 | 1.8 V-domain GPIO trap | **None** — PSRAM 1.8 V is module-internal (unlike S3 IO47/48) |

### 9.b CLOSABLE NOW WITHOUT S31 (design/layout desk, not blocked on silicon)
| # | Item | How |
|---|---|---|
| 12 | EN RC-delay ↔ LTC2954 KILL coexistence | Both drive EN (pin 5); design timing so RC (10 k/1 µF) and kill pulse don't fight at power-up |
| 13 | VBAT_SW switch sizing for cartridge | Size TPS22919/P-FET from LP103395 max discharge + assumed SoM 2 A peak |
| 14 | LRA→mic acoustic isolation | Mechanical (foam durometer, standoff, flex distance); validate on any ESP32 + T5838 bench |
| 15 | Touch-through-FR4 feasibility | Bench on any ESP32-S3 + 1.6 mm FR4 coupon — de-risks before S31 arrives |
| 16 | ES8311 analog mic-in front-end (bias, AC-couple, anti-alias) | Codec datasheet + app notes |
| 17 | Antenna tab / keyring detuning + ESD | 22 mm-edge keepout confirmed; mock-up + TVS |

### 9.c REQUIRES REAL S31 (physical measurement — cannot be closed by research)
| # | Item | Why silicon-bound | Priority |
|---|---|---|---|
| 18 | **esp_tee / key manager maturity**: KEK wrap/destroy, monotonic counter, atomic verify→reset (§7.8) | Most load-bearing assumption; API maturity only knowable on current IDF+silicon | **1st** |
| 19 | Deep/light-sleep & armed-VOX real currents (§6) | Datasheet gives typ; actual system draw needs measurement | 2nd |
| 20 | AES-XTS throughput vs SD 4-bit vs USB-HS (does HW AES keep up on-the-fly?) | Real bus + crypto engine timing | 2nd |
| 21 | VOX onset latency (secure-boot wake + SD init) vs R12 ≤ 1 s | End-to-end wall-clock on real boot path | 3rd |
| 22 | it-IT ML benchmark (parallel lane, cartridge silicon) | Needs Radxa Zero 3 / Core3506, not S31 — independent of this board; **start now** | parallel |

**Net:** with both datasheets in hand, 11 items are closed by documentation, 6 are design-desk tasks not blocked by silicon, and only 4 genuinely need the S31 in hand (plus the ML lane on different silicon). **Pin map is frozen (PIN_MAP.md); PCB schematic and layout are unblocked.** The §7.8 TEE spike (#18) is the one gating risk for the security model and should be the first devkit task.
