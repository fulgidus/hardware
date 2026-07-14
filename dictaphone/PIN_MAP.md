# PIN MAP — ESP32-S31-WROOM-3 (project: full-offline AI dictaphone)

**Module:** ESP32-S31-WROOM-3-**N16R16V** (16 MB flash / 16 MB PSRAM octal 1.8 V) · 99-pad castellated, on-board PCB antenna, 22×30×3.5 mm
**Source:** ESP32-S31-WROOM-3 Datasheet v0.1 (2026-05-21) + ESP32-S31 Series Datasheet v0.2. **PRELIMINARY** — re-verify at layout.
**Rev:** 1.0 (first freeze from real datasheet)

---

## 0. Key facts verified from datasheet (decisions this locks)

1. **microSD = dedicated pins, zero GPIO cost.** SD_D0–D3 / SD_CLK / SD_CMD are module pins 27–32 (chip GPIO20–25 via IO MUX Card 1). They do NOT consume the GPIOs we need. D3 pull-up mandatory (else card falls to SPI mode).
2. **Touch = IO6–IO19 (14 channels), no conflict with SD.** Confirmed independent pin banks.
3. **DAC on IO4 + IO5** (hardware, 0–3.3 V, sine LUT) → buzzer tones/melodies for free; **PAM8904 + LEDC-buzzer path can be dropped** (piezo driven by DAC, or keep piezo+simple drive on a DAC pin).
4. **ASRC** (hardware audio sample-rate converter, → 48 kHz) → PDM-from-T5838 to 48 kHz Opus, CPU-free.
5. **PSRAM 16 MB** on every WROOM-3 SKU → pre-roll ring buffer is generous.
6. **USB-HS OTG = dedicated pins 40/41** (USB_DP/DM). Not GPIO-matrixable; single OTG → external mux for USB-C↔cartridge share.
7. **PDM RX** present in I2S (datasheet §5.2.2.4 lists "PDM RX mode: raw PDM data reception"). ✅ T5838 works.
8. **Strapping: GPIO60, GPIO61** (boot mode) + **GPIO37** (JTAG source, NO internal pull — must be driven, not floating). Keep these free of hard-tied peripherals or handle carefully.
9. **Analog comparator on IO37–IO40**, **ADC1 IO42–49, ADC2 IO50–57**, **DAC IO4/IO5** — analog-capable pins to spend last on digital.
10. **EN (pin 5)** needs RC delay (R=10 k, C=1 µF) per datasheet; coordinate with LTC2954 (it drives EN/kill).

## 1. Reserved / do-not-touch pins

| Module pin | Name | Why reserved |
|---|---|---|
| 5 | EN | CHIP_PU; RC delay + LTC2954 kill. Not a GPIO. |
| 40, 41 | USB_DP / USB_DM | USB-HS OTG (dedicated). → USB-C via mux U14. |
| 68, 69 | TX0 / RX0 (GPIO58/59) | UART0 boot log / console. Keep for debug; usable later. |
| 42, 43 | IO33 / IO34 | USB Serial/JTAG (GPIO33/34) — flashing & debug. Keep free. |
| 71, 70 | IO61 / IO60 | **Strapping** (boot mode). May be IO after reset, but keep bare. |
| 46 | IO37 | **Strapping** (JTAG src), no internal pull + analog comparator. Avoid. |
| 33–39, 91 | NC | Not connected. |
| flash bus | (internal) | pins 27–33 of chip = flash; in-module, not exposed. |

## 2. Project pin allocation (freeze)

Legend: **LP** = wake-capable in deep sleep (chip pins 5–13 → LP_GPIO0–7).
Mapping module→chip: IO0=LP_GPIO0, IO1=LP_GPIO1, IO2=LP_GPIO2, IO3=LP_GPIO3, IO4=LP_GPIO4, IO5=LP_GPIO5, IO6=LP_GPIO6, IO7=LP_GPIO7. **Only IO0–IO7 are LP/wake-capable.**

### 2.a Wake sources (must be LP_GPIO — scarce: 8 total, minus DAC use)
| Signal | Module pin | LP ch | Note |
|---|---|---|---|
| REC slider | IO0 (8) | LP_GPIO0 | wake from deep sleep; also XTAL_32K_N (unused, we have 40 MHz xtal) |
| STEALTH slider | IO1 (9) | LP_GPIO1 | wake; also XTAL_32K_P (unused) |
| RTC-INT (RV-3028) | IO2 (6) | LP_GPIO2 | timed wake; LP_UART/LP_SPI capable |
| MIC_WAKE (T5838 AAD D2) | IO3 (7) | LP_GPIO3 | VOX voice-activity wake |
| **LP_I2C-A (always-on bus)** | IO6 (12)=SCL, IO7 (13)=SDA | LP_GPIO6/7 | RTC + fuel gauge on **LP_I2C** → readable by LP core in sleep. **Steals 2 touch channels** (see §2.d) |

Remaining LP: IO4, IO5 → **used by DAC** (§2.b). LP budget fully spent. VBUS-detect + PB-INT move to HP GPIO with EXT1 wake if needed, or share.

### 2.b Audio / buzzer
| Signal | Module pin | Function used | Note |
|---|---|---|---|
| Buzzer / tones | IO4 (10) | **DAC ch0** | replaces PAM8904+LEDC path |
| (spare DAC) | IO5 (11) | DAC ch1 | optional 2nd tone / analog out |
| I2S1 → ES8311 BCLK | IO8 (14) | I2S (matrix) | codec for playback + TRRS analog mic-in |
| I2S1 LRCLK | IO9 (15) | I2S | |
| I2S1 DOUT→codec | IO10 (16) | I2S | |
| I2S1 DIN←codec (ADC) | IO11 (17) | I2S | enables TRRS lavalier |
| ES8311 ctrl | on I2C-B | — | |
| class-D EN / jack-detect | 2× HP GPIO | GPIO | mute on jack insert |

### 2.c Mic (T5838, PDM, 1.8 V domain)
| Signal | Module pin | Note |
|---|---|---|
| PDM CLK → mic | IO12 (18) | via level shifter U16 (3V3→1.8V) |
| PDM DATA ← mic | IO13 (19) | via shifter (1.8V→3V3) |
| THSEL (AAD config) | IO14 (20) | one-wire; via shifter |
| WAKE ← mic | IO3 (LP_GPIO3) | see §2.a |

### 2.d Touch keypad
14 touch channels = IO6–IO19. **IO6/IO7 taken by LP_I2C-A**, IO8–IO14 taken by audio/mic above. Remaining touch-capable: **IO15, IO16, IO17, IO18, IO19** = 5 pads native.
→ **Decision:** 5 direct touch pads is too few for a 12-key PIN pad. Options:
  (a) **touch matrix** (touch_element lib): 5 ch → up to 6 keys; or 7 ch → 12 keys — but we don't have 7 free.
  (b) **reclaim pins**: move audio I2S off IO8–IO11 onto non-touch GPIOs (IO42+, plenty free), freeing IO8–IO14 back to touch → then IO8–IO19 = up to 12 touch pads direct. **← recommended.**
→ **Resolution:** I2S1, PDM, THSEL relocated to high GPIOs (IO42–IO57 range, all matrix-routable), returning IO8–IO19 to touch. Gives **12 direct touch pads** (IO8–IO19) + IO6/IO7 for LP_I2C. Updated in §2.g.

### 2.e Storage (dedicated pins — no GPIO cost)
| Signal | Module pin | Note |
|---|---|---|
| SD_D0–D3 | 27,28,29,30 | 4-bit SDIO; D3 pull-up |
| SD_CLK | 31 | |
| SD_CMD | 32 | |

### 2.f USB-C
| Signal | Module pin | Note |
|---|---|---|
| USB_DP / USB_DM | 40 / 41 | via mux U14 (DNP) to share with cartridge FFC |

### 2.g Relocated audio/mic (freeing touch) + control outputs — high GPIOs (matrix)
All of IO42–IO57, IO60, IO61 are matrix-routable HP GPIOs (many also ADC/comparator — spend digital last).
| Signal | Suggested module pin | Note |
|---|---|---|
| I2S1 BCLK / LRCLK / DOUT / DIN | IO42, IO43, IO44, IO45 | to ES8311 (matrix) |
| PDM CLK / DATA / THSEL | IO46, IO47, IO48 | to T5838 via shifters (1.8 V) |
| Haptic DRV2605L | on I2C-B | trigger optional on 1 GPIO |
| Buzzer | IO4 (DAC) | §2.b |
| LED addressable (RMT) | IO49 | behind EN_LED switch |
| Marker button (quiet tactile) | IO50 | |
| Phototransistor tamper (comparator) | IO37→ NO (strapping); use **IO38 or IO39** (comparator PAD COMP1/2) | always-on rail → wake |
| Jack detect | IO51 | |
| class-D / codec EN | IO52 | |
| EN_SD / EN_PERIPH / EN_AUDIO / EN_LED / CART_EN | IO53, IO54, IO55, IO56, IO57 | load-switch enables |
| CART_PGOOD/IRQ | IO60 | (strapping — ok as input after boot) |
| LTC2954 KILL / PB-INT | IO61 + 1 more | coordinate with EN |
| Fuel-gauge / RTC | LP_I2C-A on IO6/IO7 | always-on |
| OLED / DRV2605L / cart-EEPROM / VCNL4040 | I2C-B on 2 GPIOs (e.g. IO35/IO36) | switched-rail bus |
| VCNL4040 INT (ear-mode) | 1 spare HP GPIO (e.g. IO52 group) | prox interrupt; not wake-critical (playback-time only) |

### 2.h Touch keypad (final)
**IO8–IO19 = 12 direct touch pads** (chip TOUCH_CHANNEL2–13) + VREF_TOUCH (module has it internally). IO6/IO7 = LP_I2C-A. ✅ full 12-key PIN pad, no matrix needed.

## 3. Power-domain map
| Domain | Pins | Rail |
|---|---|---|
| Digital IO (VDDPST_1/3/4) | most GPIOs | 3V3 |
| SD IO (VDDPST_SD) | SD_* | 3V3 (or 1.8 V switchable — chip supports 1.8 V SD; we use 3.3 V) |
| PSRAM (VDD_PSRAM_1P8) | internal | 1.8 V (module-internal) |
| Mic (external) | T5838 | **1V8_MIC (U15 LDO)** + shifters U16 |

## 4. GPIO budget
- Touch: 12 (IO8–IO19)
- LP_I2C-A: 2 (IO6, IO7)
- LP wake: IO0,IO1,IO2,IO3 (4) + DAC IO4,IO5 (2)
- Audio+mic (matrix): ~7 (IO42–IO48)
- Control/LED/EN/detect: ~11 (IO49–IO57, IO60, IO61)
- Reserved: USB (2), UART0 (2), USB-JTAG (2), strapping (IO37)
**Total used ≈ 42–45 of ~54 usable module GPIOs. Headroom OK.**

## 5. Open (layout-time, from datasheet)
- Confirm SD 3.3 V vs 1.8 V switching choice (we pick 3.3 V; chip supports 1.8 V SD if UHS wanted later).
- EN RC-delay ↔ LTC2954 coexistence timing.
- 1.8 V-domain: only PSRAM internal here (WROOM-3 puts PSRAM 1.8 V in-module), so **no external 1.8 V-domain GPIO trap** like S3's IO47/48 — good, one less caveat than feared.
- Antenna keepout: 22×30 module, keepout along one 22 mm edge — aligns with the protruding-tab plan.
