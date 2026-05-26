# SPEC.md
# Resilient Cyberdeck Architecture Specification
Version: 0.1-draft

---

# 1. Purpose

This document specifies a resilient cyberdeck architecture intended to maintain
partial or degraded operational capability under:

- severe electrical instability,
- partial hardware destruction,
- EMP-like events,
- radiation-induced faults,
- storage corruption,
- subsystem failure,
- field repair conditions,
- prolonged off-grid operation.

The system prioritizes:

1. survivability,
2. recoverability,
3. modularity,
4. fault isolation,
5. field serviceability,
6. graceful degradation.

The system explicitly does NOT prioritize:
- minimal BOM cost,
- miniaturization,
- cosmetic integration,
- consumer-grade simplicity.

---

# 2. Core Design Philosophy

The architecture is divided into two layers:

## Tier A — Survival Control Plane

A distributed MCU quorum responsible for:
- power management,
- rail control,
- fault isolation,
- watchdog supervision,
- recovery operations,
- emergency UI,
- low-power communications,
- boot arbitration.

This layer is considered the true root of control.

## Tier B — High-Performance Compute Layer

A replaceable Linux-capable compute module:
- LattePanda Mu,
- CM5,
- x86 SBC,
- ARM SBC,
- future compute payloads.

This layer is treated as:
- powerful,
- disposable,
- supervised,
- non-authoritative.

Linux is considered a payload environment, not the system authority.

---

# 3. System Overview

## High-Level Architecture

External Power Sources
    -> Power-path / OR-ing layer
    -> Protected DC Bus
    -> Independent power rails
    -> MCU quorum + survival systems
    -> Main compute subsystem

---

# 4. Power Architecture

## 4.1 Input Sources

Supported power sources:

- Battery A (main pack)
- Battery B (reserve pack)
- USB-C PD input
- Solar MPPT input
- Vehicle DC input
- Optional hand-crank input

## 4.2 Battery Chemistry

Preferred chemistry:
- LiFePO4

Rationale:
- thermal stability,
- cycle life,
- lower fire risk,
- field durability.

## 4.3 Power Pathing

Input sources SHALL be isolated using:
- ideal-diode controllers,
- power-path controllers,
- hot-swap controllers,
- surge suppression.

No single power source SHALL represent a total system SPOF.

## 4.4 Rail Segmentation

Subsystems SHALL be electrically isolated into independent rails.

Minimum rails:
- Rail 0: MCU quorum / survival layer
- Rail 1: Main compute layer
- Rail 2: Radios
- Rail 3: Storage
- Rail 4: Displays
- Rail 5: External I/O

## 4.5 Fault Isolation

Subsystem rails SHALL use:
- resettable solid-state circuit breakers,
- programmable load switches,
- current monitoring,
- thermal monitoring.

The system SHALL avoid:
- mechanical relays as primary isolation,
- one-shot fuse dependency,
- non-recoverable protection strategies.

Protection systems SHALL support:
- manual retry,
- supervisor retry,
- quarantine mode,
- field replacement workflows.

## 4.6 Energy Buffering

The protected DC bus SHOULD include:
- supercapacitor buffering,
- transient ride-through capability,
- brownout mitigation.

---

# 5. MCU Quorum Layer

## 5.1 Topology

The control plane SHALL use:
- 3 independent MCUs minimum.

Recommended:
- heterogeneous MCU architectures.

Example:
- STM32,
- RP2040,
- AVR/MSP430/SAMD/PIC.

## 5.2 Quorum Rules

Critical actions SHALL require:
- 2-of-3 agreement.

Examples:
- rail shutdown,
- compute reset,
- source switchover,
- firmware rollback,
- storage isolation.

## 5.3 MCU Responsibilities

The MCU quorum SHALL support:
- watchdog supervision,
- power arbitration,
- rail telemetry,
- battery monitoring,
- fault logging,
- event timestamping,
- boot source selection,
- firmware recovery,
- degraded-mode operation.

## 5.4 Persistence

Critical logs/configuration SHALL reside in:
- FRAM,
- MRAM,
- redundant flash storage.

The system SHALL NOT depend solely on Linux filesystems
for survival-critical state retention.

---

# 6. Displays

## 6.1 Display Redundancy

The system SHALL contain:
- 2 MCU-driven survival displays minimum.

The Linux/main display is NOT considered a survival display.

## 6.2 Display Characteristics

Preferred survival display technologies:
- e-paper,
- transflective LCD,
- ultra-low-power OLED.

## 6.3 Display Control

Displays SHALL:
- subscribe to quorum state,
- tolerate primary MCU election changes,
- operate independently.

No single display controller SHALL be a total failure point.

---

# 7. Main Compute Layer

## 7.1 Supported Compute Payloads

Examples:
- LattePanda Mu,
- Raspberry Pi CM5,
- Ryzen Embedded SBCs,
- Intel N-series SBCs,
- future modular compute systems.

## 7.2 Design Assumption

The main compute layer SHALL be treated as:
- replaceable,
- resettable,
- non-authoritative.

## 7.3 Required Capabilities

Main compute SHOULD provide:
- Linux operation,
- high-level networking,
- SDR support,
- local AI tooling,
- storage management,
- mapping/navigation,
- documentation access.

---

# 8. Communications

## 8.1 Meshtastic Layer

The system SHALL include:
- 2 RAK4631-based Meshtastic modules minimum.

## 8.2 Radio Separation

Radio modules SHALL support:
- independent power control,
- independent firmware,
- independent antennas,
- independent failure domains.

## 8.3 Radio Roles

Suggested roles:

RAK-A:
- primary mesh node,
- telemetry,
- Linux integration.

RAK-B:
- low-power beacon,
- emergency fallback,
- survival-only communications.

## 8.4 SDR Receive Layer

The system SHOULD include:
- one or more RTL-SDR-compatible receivers,
- appropriate antennas or antenna ports,
- optional band-pass filtering,
- optional RF attenuators,
- software tooling for emergency signal reception and decoding.

The SDR layer is intended for:
- passive monitoring,
- emergency broadcast reception,
- local RF environment awareness,
- weather/aviation/marine/utility monitoring where legally permitted,
- diagnostic inspection of onboard radio emissions.

## 8.5 Meshtastic End-to-End Diagnostics

The RTL-SDR layer SHOULD support end-to-end diagnosis of Meshtastic nodes.

Diagnostic uses include:
- confirming that RAK-A or RAK-B is transmitting,
- estimating signal presence and frequency offset,
- detecting antenna/feedline failure,
- detecting stuck transmit or unexpected emissions,
- validating that failover radio behavior is observable over RF.

The SDR receiver SHALL NOT be considered a replacement for normal Meshtastic packet-level telemetry.
It is an independent RF-observation path.

## 8.6 RF Shielding and Self-Interference Control

Power management and RF layout SHALL minimize self-inflicted jamming and QRM.

Design measures SHOULD include:
- independent power rails for SDR and transmit radios,
- switchable SDR power,
- switchable transmitter power,
- physical separation between noisy compute modules and RF front ends,
- shielded RF compartments where practical,
- shielded or filtered DC/DC converters,
- ferrites and common-mode chokes on relevant cables,
- filtered bulkhead antenna connectors,
- careful grounding strategy,
- selectable quiet mode that disables noisy subsystems during weak-signal reception.

The system SHOULD support an RF quiet diagnostic state in which:
- main compute may be suspended or powered down,
- display backlights may be dimmed or disabled,
- unnecessary DC/DC converters may be disabled,
- only the selected radio/SDR path remains active.

## 8.7 Survival Communications

At least one radio SHALL remain operable during:
- degraded mode,
- reserve-power mode,
- Linux failure conditions.

At least one passive receive path SHOULD remain available in degraded mode when power budget allows.

---

# 9. Storage

## 9.1 Redundancy

The architecture SHOULD support:
- mirrored storage,
- offline backups,
- removable media.

## 9.2 Isolation

Each storage device SHALL have:
- independent rail control,
- independent fault isolation.

## 9.3 Recovery

The system SHOULD support:
- immutable OS snapshots,
- rollback boot,
- recovery images,
- offline recovery mode.

---

# 10. External Interfaces

## 10.1 Protection

External interfaces SHALL use:
- TVS protection,
- ESD suppression,
- resettable protection,
- surge mitigation.

## 10.2 Sacrificial Design

External ports SHALL be considered:
- high-risk,
- sacrificial,
- field-replaceable.

---

# 11. Degraded Operating Modes

## 11.1 Normal Mode

Capabilities:
- Linux compute,
- full UI,
- high-bandwidth networking,
- storage services,
- external displays.

## 11.2 Degraded Mode

Capabilities:
- MCU primary election,
- emergency displays,
- partial communications,
- storage diagnostics,
- rail management.

## 11.3 Survival Mode

Capabilities:
- quorum-only operation,
- reserve battery operation,
- emergency UI,
- low-power radio,
- fault diagnostics,
- repair assistance.

---

# 12. Field Serviceability

The architecture SHALL prioritize:
- modular replacement,
- accessible connectors,
- rail test points,
- diagnostic indicators,
- replaceable daughterboards.

The system SHALL avoid:
- irreversible potting,
- hidden service dependencies,
- solder-only repair assumptions.

---

# 13. Threat Model

Primary resilience targets:
- electrical instability,
- transient overvoltage,
- partial EMP exposure,
- radiation-induced faults,
- thermal faults,
- software corruption,
- storage corruption,
- subsystem shorts,
- operator error.

Non-goals:
- military-certified nuclear hardening,
- direct blast survivability,
- classified TEMPEST compliance.

---

# 14. Architectural Principle

The cyberdeck SHALL:
- fail gracefully,
- remain diagnosable,
- remain repairable,
- preserve minimum functionality,
- preserve communications capability,
- preserve operator control.

End of specification.
