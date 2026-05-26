# Tricorder — KiCad 10 Schematic Guide

> Starting point: blank `tricorder.kicad_sch`  
> Goal: complete, connected schematic with clean ERC  
> Structure: 8 progressive phases — one functional block per phase  
> KiCad version: 10.0.3 (Flatpak)

---

## Table of Contents

1. [Phase 0 — Library Setup](#phase-0--library-setup)
2. [Phase 1 — Organizing the Schematic into Sheets](#phase-1--organizing-the-schematic-into-sheets)
3. [Phase 2 — Power Subsystem](#phase-2--power-subsystem)
4. [Phase 3 — MCU ESP32-S3](#phase-3--mcu-esp32-s3)
5. [Phase 4 — Display and Input](#phase-4--display-and-input)
6. [Phase 5 — Camera OV2640](#phase-5--camera-ov2640)
7. [Phase 6 — Sensors (I2C block)](#phase-6--sensors-i2c-block)
8. [Phase 7 — Audio and GPS](#phase-7--audio-and-gps)
9. [Phase 8 — Final Connections and ERC](#phase-8--final-connections-and-erc)
10. [Quick Reference](#quick-reference)

---

## Phase 0 — Library Setup

### 0.1 — What you already have

The `libs/` directory is committed to the repo and syncs across machines via git:

```
libs/
├── espressif/          ← official Espressif KiCad library (ESP32-S3-WROOM-2 ✓)
└── sparkfun-sen55/     ← reference schematics only (no .kicad_sym)
```

The `libs/sparkfun-sen55` repo contains reference PCB/schematic files for the
SCD41+SEN55 combo board. It is useful as a **wiring reference** — open
`Hardware/SparkFun Indoor Air Quality Sensor - SCD41 SEN55.kicad_sch` in KiCad
to study how Sensirion recommends connecting those sensors.

### 0.2 — What is already in KiCad's built-in libraries

KiCad 10 ships with these parts from our BOM — **no download needed**:

| Component     | KiCad Library             | Symbol name          |
| :------------ | :------------------------ | :------------------- |
| BME680        | Sensor                    | BME680               |
| SCD41         | Sensor_Gas                | SCD41-D-R2           |
| AS7341        | Sensor_Optical            | AS7341DLG            |
| LIS3MDL       | Sensor_Magnetic           | LIS3MDL              |
| BQ25895       | Battery_Management        | BQ25895RTW           |
| MCP23017      | Interface_Expansion       | MCP23017x-x-SO       |
| AP2112K-3.3   | Regulator_Linear          | AP2112K-3.3          |
| MCP601        | Amplifier_Operational     | MCP601-xOT           |

> Tip: before downloading anything, press **A** in the schematic editor and
> search the part number. If it shows up, you're done.

### 0.3 — Parts NOT in KiCad built-in libraries

These need to be obtained via the **impartGUI plugin** (already installed):

| Component     | Why not built-in                                       |
| :------------ | :----------------------------------------------------- |
| ICM-42688-P   | Only older ICM variants (20602, 20948) are in built-in |
| VEML6075      | Not present in Sensor_Optical                          |
| MAX17048      | Only MAX17261/17263 in Battery_Management              |
| WM8960        | Only WM8731 variants in Audio                          |
| INMP441       | Not present in Sensor_Audio                            |
| SEN55         | Not present in Sensor_Gas                              |
| SEN0322       | Not available in any built-in lib                      |
| MICS-6814     | Only MiCS-5524 (different part) in Sensor_Gas          |

All of these are available on LCSC — impartGUI searches LCSC directly
and converts EasyEDA format to KiCad automatically.

### 0.4 — impartGUI setup (one-time)

impartGUI is already installed (`com_github_Steffen-W_impartGUI`).
It is the plugin icon in the schematic editor toolbar.

**Important:** the plugin has a "Local Library" mode that tries to save
parts into the project folder. This mode requires detecting an open project,
which fails inside the Flatpak sandbox (psutil not available).

**Fix — uncheck Local Library:**

```
Open impartGUI → Settings tab → uncheck "Local Library"
```

With Local Library off, parts download to `~/KiCad/EasyEDA.kicad_sym`
(the file already exists with prior downloads).

Register it once as a global library:

```
Schematic Editor → Preferences → Manage Symbol Libraries
→ Global Libraries → [+]
  Nickname : EasyEDA
  Library  : /home/fulgidus/KiCad/EasyEDA.kicad_sym
```

**Workflow for each missing part:**

```
1. Open impartGUI from the toolbar
2. Search by MPN (e.g. ICM-42688-P)
3. Select the correct variant → Import
4. Part appears in EasyEDA.kicad_sym immediately
5. Press A in schematic → EasyEDA → find your part
```

### 0.5 — Register the Espressif library in the project

KiCad needs to know about `libs/espressif/`. Add it at the **project level**
so it only applies to this project and travels with the repo.

```
In the Schematic Editor:
  Preferences → Manage Symbol Libraries → Project Specific Libraries tab → [+]
    Nickname : Espressif
    Library  : ${KIPRJMOD}/../../libs/espressif/symbols/Espressif.kicad_sym
```

`${KIPRJMOD}` expands to the project directory (`cyberdecks/tricorder/`).
`../../libs/` walks up to the repo root.

This creates a `sym-lib-table` file in `cyberdecks/tricorder/` — commit it.

### 0.6 — Create a custom symbols library for hand-drawn parts

Some parts (BB Q10 keyboard, SPEC-O3 connector) don't exist anywhere.
Create a library file to hold them:

```
Symbol Editor → File → New Library
→ save as: libs/custom/tricorder_custom.kicad_sym
→ scope: Project
```

Register it the same way as Espressif:

```
Preferences → Manage Symbol Libraries → Project Specific Libraries → [+]
  Nickname : tricorder_custom
  Library  : ${KIPRJMOD}/../../libs/custom/tricorder_custom.kicad_sym
```

---

## Phase 1 — Organizing the Schematic into Sheets

### Why multi-sheet matters

The tricorder has ~25 ICs and hundreds of connections. On a single A4 sheet
it becomes unreadable. KiCad supports **hierarchical sheets** — each sheet is
a separate `.kicad_sch` file but is part of the same project.

### Adding a sub-sheet in KiCad 10

KiCad 10 reorganized the Place menu. The way to add a hierarchical sheet is:

- **Keyboard shortcut: `S`** in the schematic editor canvas  
- OR click the **"Add Hierarchical Sheet"** icon in the right-side toolbar
  (looks like a rectangle with a folded corner)

Steps:

1. Press `S` (or click the toolbar icon)
2. Click once on the canvas for the top-left corner
3. Click again (or drag) for the bottom-right corner — make it large enough
   to fit the hierarchical pins you will add later
4. The **Sheet Properties** dialog appears:
   - **Sheet name**: `POWER` (human-readable label)
   - **File name**: `sheet_power.kicad_sch` (actual file — KiCad creates it)
5. Click OK — the file is created and the block appears

Double-click the block to open and edit the sub-sheet.

### Recommended sheet structure

```
tricorder.kicad_sch          ← root sheet (title block + sheet symbols only)
├── sheet_power.kicad_sch    ← BQ25895, MAX17048, AP2112K, USB-C
├── sheet_mcu.kicad_sch      ← ESP32-S3-WROOM-2, decoupling, bus labels
├── sheet_display.kicad_sch  ← e-ink FPC, BB Q10, MCP23017
├── sheet_camera.kicad_sch   ← OV2640 FPC
├── sheet_sensors.kicad_sch  ← all 9 I2C sensors + SPEC-O3 + TDS
├── sheet_audio.kicad_sch    ← WM8960, INMP441, speakers, jack
└── sheet_gps.kicad_sch      ← u-blox M10, expansion connectors
```

### Alternative for learning: single sheet with global labels

If hierarchical sheets feel overwhelming for a first schematic, use a
**single sheet** with **Global Labels** for buses:

```
Place → Global Label  (shortcut: Ctrl+L)
```

Global labels with the same name are electrically connected anywhere in the
schematic. Use them for all buses:

```
+3V3        +3V3_GAS      GND
I2C_SDA     I2C_SCL
SPI_MOSI    SPI_MISO    SPI_SCLK
UART_TX     UART_RX
I2S_BCK     I2S_LRCK    I2S_DOUT    I2S_DIN
DVP_D0 … DVP_D7    DVP_VSYNC    DVP_HREF    DVP_PCLK    DVP_XCLK
```

**Recommendation:** Start with a single sheet. Split into sub-sheets after
the schematic is complete and ERC passes. It's much easier to refactor
connectivity when you can see everything at once.

---

## Phase 2 — Power Subsystem

**Components:** BQ25895, MAX17048, AP2112K ×2, USB-C connector, LiPo cell

### Concepts you will learn in this phase

- **Power symbols** (`P` → `+3V3`, `GND`, `VBUS`) — the "invisible wires"
  that connect rails across the whole schematic
- **PWR_FLAG** — KiCad requires at least one per rail to prove something
  drives it; missing PWR_FLAGS cause ERC false positives
- **Decoupling capacitors** — mandatory on every power pin of every IC

### BQ25895 — USB-C charger IC

```
Library: Battery_Management → BQ25895RTW

VBUS  → VBUS  (from USB-C, ~5V)
SYS   → +SYS  (system rail, 3.7–4.2V, powers everything while charging)
BAT   → VBAT  (LiPo cell +)
GND   → GND
SDA   → I2C_SDA
SCL   → I2C_SCL
INT   → (optional: wire to a free GPIO for charger alerts)
```

> SYS is the output that powers the board even while the battery is charging.
> Connect it to the LDO inputs, NOT directly to VBAT.

### MAX17048 — Fuel gauge (LiPo state-of-charge)

```
Library: Battery_Management → MAX17048 (not in built-in — use SamacSys)

VDD  → +3V3
GND  → GND
SDA  → I2C_SDA
SCL  → I2C_SCL
ALRT → (optional: free GPIO for low-battery alert)
CELL → VBAT  (measures cell voltage)
```

### AP2112K-3.3 — LDO regulator (×2 instances)

```
Library: Regulator_Linear → AP2112K-3.3

Instance 1 — main +3V3 rail:
  IN   → +SYS
  OUT  → +3V3
  EN   → +SYS  (always-on; or a GPIO if you want software control)
  GND  → GND
  Cin  → 100nF cap to GND (place right next to IN pin)
  Cout → 1µF cap to GND  (place right next to OUT pin)

Instance 2 — gas sensor +3V3_GAS rail:
  IN   → +SYS
  OUT  → +3V3_GAS
  EN   → GPIO  (allows firmware to cut power to gas sensors when idle)
  GND  → GND
  Cin  → 100nF
  Cout → 1µF
```

> **Why two rails?** The SEN55 has an internal fan and causes current spikes.
> SPEC-O3 and MICS-6814 also draw unevenly. A separate rail isolates this
> switching noise from the IMU, UV sensor, and spectrometer which are
> sensitive to supply ripple.

### USB-C connector

```
Library: Connector → USB_C_Receptacle_USB2.0  (built-in)

VBUS    → VBUS (via 500mA polyfuse → BQ25895 VBUS pin)
D-      → USB_DM  (label, connects to ESP32-S3 GPIO19)
D+      → USB_DP  (label, connects to ESP32-S3 GPIO20)
GND     → GND
CC1     → 5.1kΩ resistor → GND  (USB-C sink configuration)
CC2     → 5.1kΩ resistor → GND
SHIELD  → GND
```

### PWR_FLAG — mandatory

KiCad ERC will complain "Power pin not driven" on every rail that has no
explicit driver unless you place a PWR_FLAG on it.

```
A → search "PWR_FLAG" → place one on each of:
  +3V3, +3V3_GAS, GND, VBAT, +SYS
```

---

## Phase 3 — MCU ESP32-S3

**Component:** ESP32-S3-WROOM-2-N16R8 — from `libs/espressif`

### Placing the symbol

```
A → library: Espressif → ESP32-S3-WROOM-2
```

The WROOM module symbol has ~40 pins. It will be large — give it plenty
of room on the sheet.

### Power pins (required)

```
3V3  → +3V3
GND  → GND  (every GND pin must be connected — there are multiple)
EN   → +3V3 via 10kΩ pull-up resistor
       + 100nF cap from EN to GND  (RC circuit for clean power-on reset)
```

> **ERC tip:** All GND pins on the module must be connected to GND, even
> the ones that look redundant. KiCad will flag unconnected power pins.

### Strapping pins (boot mode)

```
GPIO0  → push-button to GND + 10kΩ pull-up to +3V3
         (hold during reset = enter flash/download mode)
GPIO3  → leave floating or add pull-up 10kΩ (strapping, do not load)
GPIO45 → leave floating (selects VDD_SPI voltage)
GPIO46 → leave floating
```

### USB pins (fixed)

```
GPIO19 → USB_DM  (connect to USB-C D- via ESD protection)
GPIO20 → USB_DP  (connect to USB-C D+ via ESD protection)
```

### Bus net labels

Instead of routing wires across the entire sheet, place a **net label**
(`L` shortcut) on each GPIO pin. Same label name = electrical connection.

| GPIO | Net label       | Connects to                     |
| :--- | :-------------- | :------------------------------ |
| 1    | I2C_SDA         | all I2C devices                 |
| 2    | I2C_SCL         | all I2C devices                 |
| 3    | UART_TX         | GPS, SPEC-O3                    |
| 4    | UART_RX         | GPS, SPEC-O3                    |
| 5    | SPI_MOSI        | e-ink, MicroSD                  |
| 6    | SPI_MISO        | MicroSD                         |
| 7    | SPI_SCLK        | e-ink, MicroSD                  |
| 8    | EINK_CS         | SSD1677                         |
| 9    | EINK_DC         | SSD1677                         |
| 10   | EINK_RST        | SSD1677                         |
| 11   | EINK_BUSY       | SSD1677                         |
| 12   | SD_CS           | MicroSD                         |
| 13   | I2S_BCK         | WM8960, INMP441                 |
| 14   | I2S_LRCK        | WM8960, INMP441                 |
| 15   | I2S_DOUT        | WM8960 (playback)               |
| 16   | I2S_DIN         | WM8960/INMP441 (record)         |
| 17   | DVP_D0          | OV2640                          |
| 18   | DVP_D1          | OV2640                          |
| 21   | DVP_D2          | OV2640                          |
| 38   | DVP_D3          | OV2640                          |
| 39   | DVP_D4          | OV2640                          |
| 40   | DVP_D5          | OV2640                          |
| 41   | DVP_D6          | OV2640                          |
| 42   | DVP_D7          | OV2640                          |
| 43   | DVP_VSYNC       | OV2640                          |
| 44   | DVP_HREF        | OV2640                          |
| 45   | DVP_PCLK        | OV2640                          |
| 46   | DVP_XCLK        | OV2640 (clock output)           |
| 47   | OV2640_RST      | OV2640 reset                    |
| 48   | OV2640_PWDN     | OV2640 power down               |

> **Net labels vs long wires — key concept:**  
> Two pins with the same label are electrically connected, no wire needed.
> Rule of thumb: use a wire only when pins are within ~2cm; use labels
> for everything else. Spaghetti wiring across an A4 sheet is the most
> common beginner mistake.

### Decoupling capacitors

Place one 100nF MLCC between each 3V3 pin and GND on the module.
The WROOM has two 3V3 pins — place 100nF on each.

---

## Phase 4 — Display and Input

### Waveshare 3.7" e-ink — FPC connector

The display connects via a flat-flex cable. You don't place the display
itself in the schematic — you place the **FPC connector** on the PCB.

```
A → Connector_FPC → FFC_ZIF-24  (built-in KiCad)
```

Pin assignment per Waveshare SSD1677 datasheet:

```
Pin 1:  GND
Pin 2:  +3V3
Pin 3:  SCLK   → SPI_SCLK
Pin 4:  MOSI   → SPI_MOSI
Pin 5:  CS     → EINK_CS
Pin 6:  DC     → EINK_DC
Pin 7:  RST    → EINK_RST
Pin 8:  BUSY   → EINK_BUSY
Pins 9-24: NC  (add No-Connect X markers — shortcut: Q)
```

> **No-Connect markers (`Q` shortcut):** Any unconnected pin that you
> intentionally leave open needs an X marker. Without it ERC throws
> "pin unconnected" errors for every one of them.

### MicroSD card

```
A → Connector → Conn_01x06  (or a dedicated MicroSD footprint)

VCC  → +3V3
GND  → GND
CLK  → SPI_SCLK
MOSI → SPI_MOSI
MISO → SPI_MISO
CS   → SD_CS
```

Add 10kΩ pull-up from CS to +3V3 (prevents floating CS during boot).

### BB Q10 Keyboard — custom symbol

This module has no KiCad library entry anywhere. You create it yourself.
This is an important skill — many modules require it.

```
Symbol Editor → File → New Symbol
  Library: tricorder_custom
  Name: BB_Q10_Keyboard

Add pins:
  Pin 1: VCC   — type: Power Input  → +3V3
  Pin 2: GND   — type: Power Input  → GND
  Pin 3: SDA   — type: Bidirectional → I2C_SDA
  Pin 4: SCL   — type: Input        → I2C_SCL
  Pin 5: INT   — type: Output       → free GPIO (keypress interrupt)
  Pin 6: RESET — type: Input        → +3V3 via 10kΩ (or free GPIO)

Add reference field: "BB Q10 Keyboard — I2C 0x1F"
Save.
```

Once saved, `A` → `tricorder_custom` → `BB_Q10_Keyboard`.

### MCP23017 — GPIO expander for side buttons and LEDs

```
Library: Interface_Expansion → MCP23017x-x-SO

VDD   → +3V3
VSS   → GND
SDA   → I2C_SDA
SCL   → I2C_SCL
A0    → GND  (I2C address 0x20)
A1    → GND
A2    → GND
RESET → +3V3 via 10kΩ pull-up
INTA  → free GPIO (interrupt port A)
INTB  → free GPIO (interrupt port B)

GPA0-GPA7, GPB0-GPB7:
  → each button pin: 10kΩ pull-up to +3V3, switch to GND
  → LED pins: 330Ω current-limiting resistor to LED anode
```

---

## Phase 5 — Camera OV2640

### FPC connector — 24-pin 0.5mm pitch

```
A → Connector_FPC → FFC_ZIF-24
```

Pin assignment:

```
Pin 1:  +3V3   (add 10µF + 100nF decoupling right at pin)
Pin 2:  GND
Pin 3:  DVP_XCLK   → DVP_XCLK  (clock in from ESP32, ~20MHz)
Pin 4:  DVP_PCLK   → DVP_PCLK  (pixel clock out)
Pin 5:  DVP_VSYNC  → DVP_VSYNC
Pin 6:  DVP_HREF   → DVP_HREF
Pin 7-14: DVP_D0..DVP_D7
Pin 15: I2C_SDA    → I2C_SDA   (sensor config via I2C)
Pin 16: I2C_SCL    → I2C_SCL
Pin 17: OV2640_RST → OV2640_RST
Pin 18: OV2640_PWDN→ OV2640_PWDN
Pins 19-24: NC
```

> **XCLK note:** The ESP32-S3 generates the OV2640 master clock on GPIO46
> using the LEDC peripheral at ~20MHz. The firmware must initialize this
> before powering up the camera. Without XCLK the sensor is dead.

---

## Phase 6 — Sensors (I2C block)

This phase has 9 sensors. Once you learn the I2C wiring pattern for one,
the rest are copy-paste with different address resistors.

### The universal I2C sensor pattern

Every I2C sensor follows this structure:

```
VDD/VCC  → +3V3  (or +3V3_GAS for gas sensors)
GND      → GND
SDA      → I2C_SDA
SCL      → I2C_SCL
100nF    → between VDD and GND, placed right at the pin
ADDR pin → GND for low address, +3V3 for high address
```

### I2C pull-up resistors — place ONCE only

Pull-ups go once per bus, not on every device. Place them near the ESP32:

```
I2C_SDA → 4.7kΩ → +3V3
I2C_SCL → 4.7kΩ → +3V3
```

### Sensors one by one

#### BME680 — Temperature / Humidity / Pressure / VOC

```
Library: Sensor → BME680

VDD  → +3V3
GND  → GND
SDI  → I2C_SDA
SCK  → I2C_SCL
SDO  → GND  (address 0x76)
CS   → +3V3  (forces I2C mode, disables SPI)
Decoupling: 100nF between VDD and GND
```

#### ICM-42688-P — IMU (accelerometer + gyroscope)

```
Library: SamacSys → ICM-42688-P

VDD   → +3V3
VDDIO → +3V3
GND   → GND
SDA   → I2C_SDA
SCL   → I2C_SCL
AD0   → GND  (address 0x68)
INT1  → free GPIO (data-ready interrupt)
CS    → +3V3  (forces I2C mode)
Decoupling: 100nF + 10µF between VDD and GND
```

> The extra 10µF on the IMU matters. It's sensitive to supply ripple and
> mechanical vibration. Note this for PCB layout: keep it away from the
> SEN55 fan mounting area.

#### LIS3MDL — Magnetometer / compass

```
Library: Sensor_Magnetic → LIS3MDL

VDD  → +3V3
GND  → GND
SDA  → I2C_SDA
SCL  → I2C_SCL
SA1  → GND  (address 0x1C)
CS   → +3V3  (forces I2C mode)
DRDY → NC or free GPIO (data-ready, optional)
Decoupling: 100nF
```

#### VEML6075 — UV-A / UV-B index

```
Library: SamacSys → VEML6075

VDD  → +3V3
GND  → GND
SDA  → I2C_SDA
SCL  → I2C_SCL
(fixed address 0x10, no address selection pin)
Decoupling: 100nF
```

#### AS7341 — 11-channel visible spectrometer

```
Library: Sensor_Optical → AS7341DLG

VDD  → +3V3
GND  → GND
SDA  → I2C_SDA
SCL  → I2C_SCL
INT  → free GPIO (measurement complete interrupt)
LDR  → NC  (external LED driver, not needed for ambient measurement)
(fixed address 0x39)
Decoupling: 100nF
```

#### SCD41 — CO₂ (photoacoustic NDIR)

```
Library: Sensor_Gas → SCD41-D-R2

VDD  → +3V3
GND  → GND
SDA  → I2C_SDA
SCL  → I2C_SCL
(fixed address 0x62)
Decoupling: 10µF + 100nF  (photoacoustic = current spikes, needs bulk cap)
```

> SCD41 supports single-shot mode: trigger one measurement, wait ~5s,
> read result, then sleep. Do not run it continuously — saves ~25mW.

#### SEN55 — PM1/2.5/4/10 + VOC + NOx (fan inside)

```
Library: SamacSys → SEN55-SDN-T

VDD  → +3V3_GAS  (separate rail — internal fan causes current spikes)
GND  → GND
SDA  → I2C_SDA
SCL  → I2C_SCL
(fixed address 0x69)
Connector type: JST XH 5-pin  → use Connector_JST:JST_XH_B5B-XH-A
Decoupling: 100µF + 100nF on VDD_GAS, placed close to the connector
```

#### MICS-6814 — CO / NO₂ / NH₃ (resistive MEMS)

```
Library: SamacSys → MICS-6814

VCC  → +3V3_GAS
GND  → GND
SDA  → I2C_SDA
SCL  → I2C_SCL
(address 0x04)
Decoupling: 100nF
```

#### SEN0322 — O₂ (electrochemical)

```
Library: SamacSys → SEN0322

VCC  → +3V3_GAS
GND  → GND
SDA  → I2C_SDA
SCL  → I2C_SCL
(address 0x73)
Decoupling: 100nF
```

### SPEC-O3 — Ozone, UART interface

Treat as a connector, no IC symbol needed.

```
A → Connector → Conn_01x04

Pin 1: VCC    → +3V3_GAS via N-channel MOSFET (2N7002)
                Gate driven by a free GPIO (software power enable)
Pin 2: GND    → GND
Pin 3: TX_O3  → UART_RX  (sensor transmits, ESP32 receives)
Pin 4: RX_O3  → UART_TX
```

> Power enable MOSFET: The SPEC-O3 has a 15-second warm-up time and
> draws ~60mW idle. Gating it with a MOSFET lets firmware power it only
> when a measurement is needed, saving ~8% of the idle power budget.

### TDS Probe — analog signal chain

The TDS probe signal is weak AC and needs conditioning before the ADC.

```
Step 1 — probe connector:
  A → Connector → Conn_01x02
  Pin 1: VCC_PROBE → +3V3
  Pin 2: TDS_SIGNAL

Step 2 — MCP601 op-amp buffer:
  Library: Amplifier_Operational → MCP601-xOT
  IN+  → TDS_SIGNAL
  IN-  → OUT  (unity-gain buffer configuration)
  VDD  → +3V3
  VSS  → GND
  OUT  → TDS_ADC  (label — connect to a free ADC-capable GPIO)

Step 3 — anti-alias filter:
  100nF cap from TDS_SIGNAL to GND (before the op-amp)
```

---

## Phase 7 — Audio and GPS

### WM8960 — audio codec

```
Library: SamacSys → WM8960CGEFL (or similar variant)

DBVDD, DCVDD, AVDD, PVDD → +3V3
AGND, DGND, PGND → GND  (all ground pins tied together)

BCLK   → I2S_BCK
DACLRC → I2S_LRCK
ADCLRC → I2S_LRCK   (shared clock in standard I2S mode)
DACDAT → I2S_DOUT   (audio data to speakers)
ADCDAT → I2S_DIN    (mic data to ESP32)

SDA    → I2C_SDA   (register control)
SCL    → I2C_SCL
(fixed address 0x1A)

SPKOUTP, SPKOUTN → Left speaker (8Ω 1W)
OUT3             → Right speaker output
HP_L, HP_R       → 3.5mm jack tip/ring
MICBIAS          → INMP441 VDD
```

Decoupling for WM8960 (critical — bad decoupling = audible noise):
```
AVDD : 10µF + 100nF to GND
PVDD : 10µF + 100nF to GND
DBVDD: 100nF to GND
```

### INMP441 — MEMS microphone (I2S digital)

```
Library: SamacSys → INMP441

VDD  → MICBIAS  (from WM8960) — or +3V3 if MICBIAS not used
GND  → GND
SD   → I2S_DIN   (audio data out)
SCK  → I2S_BCK
WS   → I2S_LRCK
L/R  → GND  (selects left channel, address 0)
Decoupling: 100nF
```

### 3.5mm TRRS jack

```
A → Connector_Audio → AudioJack4_SwitchT  (built-in)

TIP     → HP_L    (WM8960)
RING1   → HP_R    (WM8960)
RING2   → MIC_EXT (WM8960 ADC input, 100nF AC-coupling cap in series)
SLEEVE  → GND
SWITCH  → free GPIO + 10kΩ pull-up (jack insertion detection)
```

### Speakers (×2)

```
A → Connector → Conn_01x02  (or Speaker symbol)

Speaker L:
  Pin 1 → SPKOUTP (WM8960)
  Pin 2 → SPKOUTN (WM8960)

Speaker R:
  Pin 1 → OUT3 (WM8960)
  Pin 2 → GND
```

### u-blox M10 GPS

For a first prototype, treat the M10 as a module (black box) rather than
bare IC. The bare IC requires a crystal, RF matching network, and antenna
design — save that for revision 2.

Create a simple custom symbol:

```
Symbol Editor → tricorder_custom → New Symbol: uBlox_M10_Module

Pin 1: VCC  → +3V3
Pin 2: GND  → GND
Pin 3: TXD  → UART_RX  (module transmits, ESP32 receives)
Pin 4: RXD  → UART_TX
Pin 5: PPS  → NC or free GPIO (1 pulse-per-second sync, optional)
```

---

## Phase 8 — Final Connections and ERC

### Pre-ERC checklist

Go through this before running ERC:

- [ ] Every IC has at least 100nF decoupling between VDD and GND
- [ ] All GND pins are connected to GND (including "redundant" ones)
- [ ] All intentionally unconnected pins have a No-Connect marker (`Q`)
- [ ] I2C pull-ups (4.7kΩ) placed exactly once on the bus
- [ ] PWR_FLAG on every power rail (+3V3, +3V3_GAS, GND, VBAT, +SYS)
- [ ] BOOT button (GPIO0) has 10kΩ pull-up
- [ ] EN pin of ESP32-S3 has 10kΩ pull-up to +3V3 + 100nF to GND
- [ ] USB-C CC1/CC2 have 5.1kΩ resistors to GND
- [ ] SPEC-O3 power enable MOSFET is present

### Running the ERC

```
Inspect → Electrical Rules Checker → Run ERC
```

Common errors and fixes:

| ERC message                        | Fix                                                  |
| :--------------------------------- | :--------------------------------------------------- |
| Pin unconnected                    | Add No-Connect marker (Q) on intentional NC pins     |
| Power pin not driven               | Add PWR_FLAG on the named rail                       |
| Wire not connected                 | Find the dangling wire end and connect or delete it  |
| Duplicate net names                | Rename one of the conflicting labels                 |
| Pin connected to multiple outputs  | Check for overlapping wire endpoints                 |
| hier_label_mismatch                | Hierarchical label name doesn't match the sheet pin  |

### Annotating references

Once all components are placed, assign unique reference designators:

```
Tools → Annotate Schematic → Annotate All → OK
```

This assigns R1, R2, C1, C2, U1, U2 … to everything.
Do this after all components are placed, before running final ERC.

### Assigning footprints

```
Tools → Assign Footprints
```

Critical footprint assignments:

| Symbol              | Footprint                                              |
| :------------------ | :----------------------------------------------------- |
| ESP32-S3-WROOM-2    | Espressif:ESP32-S3-WROOM-2  (from libs/espressif)     |
| BME680              | Package_LGA:Bosch_LGA-8_3x3mm_P0.8mm                  |
| ICM-42688-P         | Package_LGA:InvenSense_LGA-14_3x3mm_P0.5mm             |
| LIS3MDL             | Package_LGA:ST_LGA-12_2x2mm_P0.5mm                    |
| WM8960              | Package_QFN:QFN-32_5x5mm_P0.5mm                       |
| BQ25895RTW          | Package_QFN:QFN-24_4x4mm_P0.5mm                       |
| MAX17048            | Package_DFN_QFN:DFN-8_3x2mm_P0.5mm                    |
| MCP23017x-x-SO      | Package_SO:SOIC-28W_7.5x17.9mm_P1.27mm                |
| AP2112K-3.3         | Package_TO_SOT_SMD:SOT-23-5                            |
| Resistors (≤1W)     | Resistor_SMD:R_0402                                    |
| Caps ≤1µF           | Capacitor_SMD:C_0402                                   |
| Caps ≥10µF          | Capacitor_SMD:C_0603                                   |

---

## Quick Reference

### KiCad 10 Schematic Editor shortcuts

| Key         | Action                              |
| :---------- | :---------------------------------- |
| `A`         | Add Symbol                          |
| `P`         | Add Power Port                      |
| `W`         | Draw Wire                           |
| `L`         | Place Net Label                     |
| `Ctrl+L`    | Place Global Label                  |
| `Q`         | Place No-Connect marker             |
| `S`         | Add Hierarchical Sheet (KiCad 10)   |
| `E`         | Edit Properties                     |
| `M`         | Move item                           |
| `G`         | Grab (move keeping wire connections)|
| `R`         | Rotate                              |
| `Ctrl+D`    | Duplicate                           |
| `Ctrl+Z`    | Undo                                |
| `Ctrl+S`    | Save                                |

### I2C address map

```
0x04  MICS-6814    CO / NO₂ / NH₃
0x10  VEML6075     UV-A / UV-B
0x1A  WM8960       audio codec control
0x1C  LIS3MDL      magnetometer
0x1F  BB Q10       keyboard + trackpad
0x20  MCP23017     GPIO expander
0x36  MAX17048     fuel gauge
0x39  AS7341       visible spectrometer
0x62  SCD41        CO₂
0x68  ICM-42688-P  IMU
0x69  SEN55        PM + VOC + NOx
0x6A  BQ25895      charger
0x73  SEN0322      O₂
0x76  BME680       temperature / humidity / pressure / VOC
```

No conflicts. All compatible with 4.7kΩ pull-ups at 3.3V.

### Recommended session plan

```
Session 1 (1h) — Phase 0+1: library registration, create sheets structure
Session 2 (1h) — Phase 2:   power subsystem (most educational phase)
Session 3 (1h) — Phase 3:   MCU, all bus labels
Session 4 (1h) — Phase 4:   display FPC, BB Q10 custom symbol, MCP23017
Session 5 (30m)— Phase 5:   camera FPC
Session 6 (2h) — Phase 6:   all sensors using the repeated I2C pattern
Session 7 (1h) — Phase 7:   audio + GPS
Session 8 (1h) — Phase 8:   ERC cleanup, annotation, footprint assignment

Total: ~9 hours
```

---

*Source: SPEC.md + LIBS.md — Tricorder Deck rev 1.0 / KiCad 10.0.3*
