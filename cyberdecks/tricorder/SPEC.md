# Tricorder Deck — Hardware Specification

> Revisione: 1.0  
> Forma: palmtop PADD, ~70mm × 150mm, tascabile  
> MCU: ESP32-S3-WROOM-2-N16R8  
> Firmware target: MicroPython (custom build con camera driver)

---

## 1. Architettura generale

Single PCB. Tutti i sensori onboard salvo expansion bus modulare.
Nessun coprocessore, nessun secondo MCU.

```
Bus SPI  → e-ink display, MicroSD, OV2640 camera (DVP separato)
Bus I2C  → tutti i sensori onboard, keyboard, power ICs, GPIO expander
Bus UART → GPS, SPEC-O3, expansion
Bus I2S  → WM8960 audio codec (mic + speaker)
Bus DVP  → OV2640 (parallelo 8-bit, dedicato)
USB      → USB-C OTG nativo ESP32-S3
```

---

## 2. MCU

| Campo          | Valore                                  |
| :------------- | :-------------------------------------- |
| IC             | ESP32-S3-WROOM-2-N16R8                  |
| Core           | Xtensa LX7 dual-core 240MHz             |
| Flash          | 16MB SPI Octal                          |
| PSRAM          | 8MB OPI PSRAM                           |
| WiFi           | 802.11 b/g/n (2.4GHz)                   |
| BT             | BLE 5.0 + Bluetooth Classic             |
| GPIO utente    | ~30 (GPIO26–37 occupati da flash/PSRAM) |
| USB            | USB 2.0 OTG nativo                      |
| Alimentazione  | 3.3V                                    |

---

## 3. Display

| Campo          | Valore                        |
| :------------- | :---------------------------- |
| IC             | Waveshare 3.7" e-Paper        |
| Controller     | SSD1677                       |
| Risoluzione    | 280 × 480 px                  |
| Area attiva    | 56.7mm × 81.4mm               |
| Colori         | B/W/Grey 4 livelli            |
| Interfaccia    | SPI                           |
| Refresh full   | ~2s                           |
| Refresh partial| ~0.3s (aggiornamento valori)  |
| Alimentazione  | 3.3V                          |
| Prezzo stimato | ~18€                          |

Note: lato corto (56.7mm) allineato alla larghezza tastiera BB Q10 (~60mm).
Partial refresh usato per aggiornamento live valori sensori.

---

## 4. Input

| Campo          | Valore                              |
| :------------- | :---------------------------------- |
| IC             | BlackBerry Q10 keyboard module      |
| Interfaccia    | I2C, indirizzo 0x1F                 |
| Tasti          | 35 + trackpad ottico capacitivo     |
| Larghezza      | ~60mm                               |
| Connettore     | FPC o header JST a seconda del mod  |

| Campo          | Valore                              |
| :------------- | :---------------------------------- |
| IC             | MCP23017                            |
| Interfaccia    | I2C, indirizzo 0x20–0x27 (config)   |
| GPIO aggiuntivi| 16 pin (pulsanti laterali, LED)     |

---

## 5. Camera

| Campo          | Valore                              |
| :------------- | :---------------------------------- |
| Sensore        | OV2640                              |
| Versione       | senza filtro IR-cut                 |
| Interfaccia    | DVP 8-bit (parallelo)               |
| Risoluzione    | fino a 2MP (UXGA 1600×1200)         |
| Output         | JPEG hardware on-chip               |
| Uso            | foto singola, no video              |
| Connettore PCB | FPC 24-pin                          |
| Prezzo stimato | ~4€                                 |

Note: firmware richiede micropython-camera-driver (lemariva),
build custom necessaria — non in MicroPython mainline.

---

## 6. Sensori onboard

### 6.1 Ambientale base

| IC       | Misure                              | Bus  | Indirizzo | Prezzo |
| :------- | :---------------------------------- | :--- | :-------- | :----- |
| BME680   | Temperatura, umidità, pressione, VOC| I2C  | 0x76/0x77 | ~5€    |
| ICM-42688-P | Accelerometro, giroscopio, IMU  | I2C  | 0x68/0x69 | ~4€    |
| LIS3MDL  | Magnetometro, bussola 3 assi        | I2C  | 0x1C/0x1E | ~3€    |
| VEML6075 | UV-A, UV-B, indice UV               | I2C  | 0x10      | ~3€    |
| AS7341   | Spettro visibile 11 canali 430–680nm| I2C  | 0x39      | ~8€    |

### 6.2 Qualità dell'aria e gas

| IC           | Misure                              | Bus  | Indirizzo  | Prezzo |
| :----------- | :---------------------------------- | :--- | :--------- | :----- |
| SCD41        | CO₂ (fotoacustico NDIR)             | I2C  | 0x62       | ~35€   |
| SEN0322      | O₂ (elettrochimico)                 | I2C  | 0x73       | ~25€   |
| SEN55        | PM1/2.5/4/10, VOC index, NOx, T, RH | I2C  | 0x69       | ~35€   |
| MICS-6814    | CO, NO₂, NH₃ (MEMS resistivo)      | I2C  | 0x04       | ~12€   |
| SPEC-O3      | Ozono O₃ (elettrochimico)           | UART | —          | ~40€   |
| TDS probe    | Total dissolved solids (acqua)      | ADC  | —          | ~5€    |

Note SCD41: fotoacustico Sensirion, nessun consumabile, warm-up ~3s.
Note SEN0322: elettrochimico, vita ~2 anni, tenere orientato verticalmente.
Note SEN55: fan interno (laser scattering PM), unica parte meccanica del device.
Note MICS-6814: sensore MEMS resistivo, deriva nel tempo, nessun warm-up critico.
Note SPEC-O3: warm-up ~15s, output UART ASCII, alimentazione 3.3V.
Note TDS: sonda analogica esterna, richiede op-amp (MCP601 o simile) + ADC ESP32-S3.

### 6.3 Posizione

| IC        | Misure             | Bus  | Indirizzo | Prezzo |
| :-------- | :----------------- | :--- | :-------- | :----- |
| u-blox M10| GPS/GNSS, geotag   | UART | —         | ~12€   |

---

## 7. Audio

| IC / Componente | Funzione                            | Bus  | Indirizzo |
| :-------------- | :---------------------------------- | :--- | :-------- |
| WM8960          | Codec audio: ADC + DAC + amp 1W×2   | I2S + I2C | 0x1A |
| INMP441         | Microfono MEMS I2S                  | I2S  | —         |
| Speaker ×2      | 8Ω 1W, stereo                       | —    | —         |
| Jack 3.5mm TRRS | Cuffie + mic esterno                | —    | —         |

Note: speaker utile per feedback sonoro geiger (click), sonar ping,
alert soglie UV/gas. WM8960 gestisce mux headphone/speaker automatico
via GPIO detect jack.

---

## 8. Power

| IC / Componente | Funzione                        | Bus  | Indirizzo |
| :-------------- | :------------------------------ | :--- | :-------- |
| BQ25895         | Charger USB-C PD, I2C ctrl      | I2C  | 0x6A      |
| MAX17048        | Fuel gauge LiPo                 | I2C  | 0x36      |
| AP2112K ×2      | LDO 3.3V (rail sensori gas separato) | — | —     |
| LiPo 3000mAh    | Cella principale                | —    | —         |
| USB-C connector | PD, OTG, JTAG/debug             | —    | —         |

### Budget consumo (stime)

| Condizione             | Consumo  | Autonomia (3000mAh) |
| :--------------------- | :------- | :------------------ |
| Idle (e-ink statico)   | ~320mW   | ~33h                |
| Attivo acquisizione    | ~520mW   | ~20h                |
| SEN55 fan attivo       | +120mW   | —                   |
| Peak (tutto attivo)    | ~800mW   | ~12h                |

---

## 9. Expansion bus

Connettori fisici su PCB, accessibili esternamente:

| Connettore      | Tipo       | Sensori modulari tipici                      |
| :-------------- | :--------- | :------------------------------------------- |
| STEMMA/Qwiic    | I2C        | qualsiasi breakout I2C compatibile 3.3V      |
| UART header     | UART TTL   | geiger counter, LiDAR TFmini, radar LD2410   |
| SPI header      | SPI        | spettrometro C12880MA (Hamamatsu), radar BGT60LTR11 |
| GPIO ×4         | raw 3.3V   | trigger/echo HC-SR04, pulse counting, 1-Wire |

---

## 10. Indirizzi I2C — mappa completa

| Indirizzo | IC           | Funzione                     |
| :-------- | :----------- | :--------------------------- |
| 0x04      | MICS-6814    | CO, NO₂, NH₃                 |
| 0x10      | VEML6075     | UV-A, UV-B                   |
| 0x1A      | WM8960       | audio codec ctrl             |
| 0x1C      | LIS3MDL      | magnetometro                 |
| 0x1F      | BB Q10       | keyboard + trackpad          |
| 0x20      | MCP23017     | GPIO expander                |
| 0x36      | MAX17048     | fuel gauge                   |
| 0x39      | AS7341       | spettro visibile             |
| 0x62      | SCD41        | CO₂                          |
| 0x68      | ICM-42688-P  | IMU                          |
| 0x69      | SEN55        | PM + VOC + NOx               |
| 0x6A      | BQ25895      | charger                      |
| 0x73      | SEN0322      | O₂                           |
| 0x76      | BME680       | temp/umidità/pressione/VOC   |

Nessun conflitto. Tutti compatibili con pull-up 4.7kΩ a 3.3V.

---

## 11. Pin assignment ESP32-S3 (draft)

| GPIO  | Funzione           | Bus   | Note                        |
| :---- | :----------------- | :---- | :-------------------------- |
| 0     | BOOT button        | —     | strapping, non usare freely |
| 1     | I2C SDA            | I2C   | pull-up 4.7kΩ               |
| 2     | I2C SCL            | I2C   | pull-up 4.7kΩ               |
| 3     | UART0 TX           | UART  | GPS / SPEC-O3               |
| 4     | UART0 RX           | UART  | GPS / SPEC-O3               |
| 5     | SPI MOSI (SPI2)    | SPI   | e-ink + SD condiviso        |
| 6     | SPI MISO (SPI2)    | SPI   | SD                          |
| 7     | SPI SCLK (SPI2)    | SPI   | e-ink + SD condiviso        |
| 8     | E-ink CS           | SPI   | —                           |
| 9     | E-ink DC           | GPIO  | —                           |
| 10    | E-ink RST          | GPIO  | —                           |
| 11    | E-ink BUSY         | GPIO  | input                       |
| 12    | SD CS              | SPI   | —                           |
| 13    | I2S BCK            | I2S   | WM8960 + INMP441            |
| 14    | I2S LRCK           | I2S   | WM8960 + INMP441            |
| 15    | I2S DOUT           | I2S   | → WM8960 (playback)         |
| 16    | I2S DIN            | I2S   | ← WM8960 / INMP441 (rec)   |
| 17    | DVP D0             | DVP   | OV2640                      |
| 18    | DVP D1             | DVP   | OV2640                      |
| 19    | USB D-             | USB   | fisso                       |
| 20    | USB D+             | USB   | fisso                       |
| 21    | DVP D2             | DVP   | OV2640                      |
| 38    | DVP D3             | DVP   | OV2640                      |
| 39    | DVP D4             | DVP   | OV2640                      |
| 40    | DVP D5             | DVP   | OV2640                      |
| 41    | DVP D6             | DVP   | OV2640                      |
| 42    | DVP D7             | DVP   | OV2640                      |
| 43    | DVP VSYNC          | DVP   | OV2640                      |
| 44    | DVP HREF           | DVP   | OV2640                      |
| 45    | DVP PCLK           | DVP   | OV2640                      |
| 46    | DVP XCLK           | GPIO  | clock out → OV2640          |
| 47    | OV2640 RESET       | GPIO  | —                           |
| 48    | OV2640 PWDN        | GPIO  | power down camera           |

Rimangono liberi per TDS ADC, jack detect, LED status, SPEC-O3 power enable.

---

## 12. Stack firmware

```
micropython-camera-driver  fork lemariva, build custom obbligatoria
uasyncio                   event loop principale
machine.I2C                bus sensori
machine.SPI                display + SD
machine.I2S                audio WM8960
machine.UART               GPS, SPEC-O3
machine.ADC                TDS probe
ubluetooth / aioble        BLE scanning, BLEeding port
```

---

## 13. Form factor

```
Dimensioni stimate   : ~70mm × 150mm × 14mm
Peso stimato         : ~120g (PCB + batteria + enclosure)
Display              : occupa tutta la larghezza, metà altezza (fronte)
Tastiera             : metà inferiore fronte
Retro                : camera, sensori ottici/gas, speaker, expansion port
Laterale             : pulsanti (via MCP23017), jack 3.5mm, USB-C
```

---

## 14. BOM — riepilogo costi stimati

| Categoria         | Totale stimato |
| :---------------- | :------------- |
| MCU               | ~8€            |
| Display           | ~18€           |
| Camera            | ~4€            |
| Tastiera + expander| ~17€          |
| Sensori base      | ~23€           |
| Sensori gas/aria  | ~117€          |
| Audio             | ~13€           |
| Power             | ~16€           |
| PCB + passivi     | ~15€           |
| Connettori misc   | ~5€            |
| **Totale**        | **~236€**      |

Escluso: enclosure, cavi FPC custom, eventuali moduli expansion.
