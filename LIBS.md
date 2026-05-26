# KiCad Libraries — Setup Guide

---

## Struttura directory consigliata

```
~/kicad-libs/
├── espressif/        # ESP32-S3 simboli e footprint
├── sensirion/        # SCD41, SEN55
├── ublox/            # M10 GPS
├── stmicro/          # LIS3MDL, ICM (fallback)
└── snapeda/          # download manuali residui
```

---

## 1. SamacSys Plugin (copre ~80% del BOM)

Installa direttamente dentro KiCad, zero cloni.

```
KiCad → Tools → Plugin and Content Manager
→ cerca "SamacSys"
→ Install → Apply Pending Changes → riavvia KiCad
```

Appare una nuova icona nella toolbar schematica.
Cerchi il part number esatto (es. `BME680`, `WM8960`, `MCP23017`)
e importi simbolo + footprint + 3D model in un click.

Componenti coperti da SamacSys per questo progetto:

```
ESP32-S3-WROOM-2        BME680          ICM-42688-P
AS7341                  VEML6075        MICS-6814
WM8960                  INMP441         BQ25895
MAX17048                MCP23017        OV2640
AP2112K                 SEN0322
```

---

## 2. Espressif — librerie ufficiali ESP32-S3

```bash
cd ~/kicad-libs
git clone https://github.com/espressif/kicad-libraries espressif
```

Contenuto:
- `symbols/`     → ESP32-S3-WROOM-2, ESP32-S3 bare, varianti
- `footprints/`  → LCC, WROOM modules
- `3dmodels/`    → STEP files

Aggiungi in KiCad:

```
Preferences → Manage Symbol Libraries → Add Existing Library
→ ~/kicad-libs/espressif/symbols/Espressif.kicad_sym

Preferences → Manage Footprint Libraries → Add Existing Library
→ ~/kicad-libs/espressif/footprints/
```

---

## 3. Sensirion — SCD41, SEN55

Sensirion **non ha un repo KiCad pubblico su GitHub**.
Le fonti reali, in ordine di comodità:

### Opzione A — KiCad official libraries (già installate)

SCD41 è stato mergiato nelle librerie ufficiali KiCad (MR !3432).
Se hai KiCad 7+ aggiornato, potrebbe essere già presente:

```
KiCad Symbol Chooser → cerca "SCD41"
→ se compare sotto Sensor_Gas: zero download necessari
```

### Opzione B — SnapEDA / SnapMagic (download diretto)

```
SCD41 : https://www.snapeda.com/parts/SCD41-D-R2/Sensirion/view-part/
SEN55 : https://www.snapeda.com/parts/SEN55-SDN-T/Sensirion/view-part/

→ Download → KiCad 7
→ KiCad → File → Import → KiCad Symbol
```

### Opzione C — SparkFun hardware repo (SCD41 + SEN55 insieme)

SparkFun ha un breakout combo con KiCad files pubblici, utile
come riferimento per footprint e schema di connessione:

```bash
cd ~/kicad-libs
git clone --depth=1 \
  https://github.com/sparkfun/SparkFun_Indoor_Air_Quality_Sensor-SCD41-SEN55 \
  sparkfun-sen55
# file KiCad in Hardware/
```

---

## 4. u-blox M10 GPS

u-blox non ha un repo GitHub pubblico. Scarica dalla pagina prodotto:

```
1. vai su https://www.u-blox.com/en/product/m10-shield
2. Resources → Design Files → KiCad
3. scarica il .zip, estrai in ~/kicad-libs/ublox/
```

In alternativa, usa il modulo breakout SparkFun ZOE-M8Q che ha
librerie KiCad su GitHub:

```bash
# alternativa rapida con modulo SparkFun
cd ~/kicad-libs
git clone https://github.com/sparkfun/SparkFun_KiCad_Libraries ublox-alt
```

Per il bare IC M10, se il file non è disponibile usa SamacSys
(copre molti IC u-blox) oppure crea un simbolo connettore manuale
(il modulo viene trattato come black box con pin I2C/UART/power).

---

## 5. STMicroelectronics — LIS3MDL

ST pubblica i file KiCad nella pagina di ogni prodotto:

```
1. vai su https://www.st.com/en/mems-and-sensors/lis3mdl.html
2. Resources → Design Resources → KiCad
3. scarica, estrai in ~/kicad-libs/stmicro/
```

```bash
# oppure, il repo community più completo:
cd ~/kicad-libs
git clone https://github.com/XenGi/lis3mdl.pretty stmicro/LIS3MDL
```

---

## 6. Waveshare e-ink 3.7" — connettore FPC

Waveshare non distribuisce librerie KiCad native.
Il display usa un connettore FPC 24-pin passo 0.5mm.

Approccio consigliato — usa il connettore generico dalla libreria ufficiale KiCad:

```
Symbol    : Connector → Conn_01x24 (o FPC-24)
Footprint : Connector_FPC → FPC-24_Horizontal_FH12-24S
```

Il connettore FH12-24S (Hirose) è quello usato da Waveshare su questi display.
Si trova in `Connector_FPC.pretty` già incluso in KiCad out-of-the-box.

---

## 7. BB Q10 Keyboard module

Non esiste un simbolo standard — è un modulo con interfaccia I2C proprietaria.
Crea un simbolo custom in 5 minuti:

```
KiCad Symbol Editor → File → New Symbol
Nome: BB_Q10_Keyboard
Pin 1: VCC   (power in, 3.3V)
Pin 2: GND
Pin 3: SDA   (I2C)
Pin 4: SCL   (I2C)
Pin 5: INT   (interrupt output, optional)
Pin 6: RESET (optional)
```

Footprint: usa `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical`
oppure il footprint del cavo flat specifico del modulo che acquisti.

---

## 8. SPEC-O3 e TDS probe

Entrambi trattati come connettori — nessuna libreria necessaria.

```
SPEC-O3 (UART):
  Symbol    : Connector → Conn_01x04
  Pin 1: VCC (3.3V)
  Pin 2: GND
  Pin 3: TX
  Pin 4: RX
  Footprint : PinHeader_1x04_P2.54mm

TDS probe (analog):
  Symbol    : Connector → Conn_01x02
  Pin 1: VCC
  Pin 2: SIGNAL (→ ADC ESP32-S3 via op-amp)
  + aggiungi op-amp MCP601 separato (disponibile su SamacSys)
```

---

## 9. SnapEDA — fallback per tutto il resto

Per qualsiasi IC non trovato nei repo sopra:

```
1. vai su https://www.snapeda.com
2. cerca il part number esatto
3. Download → KiCad 7 / KiCad 8
4. importa con File → Import → KiCad Symbol
```

SnapEDA copre praticamente tutto il mercato IC inclusi i sensori
di nicchia (SEN0322, MICS-6814, ecc.).

---

## 10. Script setup completo

```bash
#!/usr/bin/env bash
# setup-kicad-libs.sh
# clona tutte le librerie vendor per il tricorder deck

set -e

LIBS_DIR="${HOME}/kicad-libs"
mkdir -p "${LIBS_DIR}"

echo "→ Espressif (ESP32-S3)"
git clone --depth=1 \
  https://github.com/espressif/kicad-libraries \
  "${LIBS_DIR}/espressif"

echo "→ SparkFun SCD41+SEN55 reference (Sensirion non ha repo KiCad ufficiale)"
git clone --depth=1 \
  https://github.com/sparkfun/SparkFun_Indoor_Air_Quality_Sensor-SCD41-SEN55 \
  "${LIBS_DIR}/sparkfun-sen55"

echo "→ SparkFun (u-blox M10 alternativa)"
git clone --depth=1 \
  https://github.com/sparkfun/SparkFun_KiCad_Libraries \
  "${LIBS_DIR}/sparkfun"

echo ""
echo "✓ librerie clonate in ${LIBS_DIR}"
echo ""
echo "Prossimi passi:"
echo "  1. KiCad → Preferences → Manage Symbol Libraries"
echo "     aggiungi i .kicad_sym da ogni directory"
echo "  2. KiCad → Tools → Plugin Manager → installa SamacSys"
echo "  3. LIS3MDL e ST ICs: scarica da st.com → pagina prodotto → Resources"
echo "  4. u-blox M10 bare: scarica da u-blox.com → pagina M10 → Design Files"
```

Rendi eseguibile e lancia:

```bash
chmod +x setup-kicad-libs.sh
./setup-kicad-libs.sh
```

---

## 11. Riepilogo copertura BOM

| Componente       | Sorgente                 | Metodo                    |
| :--------------- | :----------------------- | :------------------------ |
| ESP32-S3-WROOM-2 | repo Espressif           | git clone                 |
| BME680           | SamacSys plugin          | search in-IDE             |
| ICM-42688-P      | SamacSys plugin          | search in-IDE             |
| LIS3MDL          | st.com / repo STM        | download / clone          |
| AS7341           | SamacSys plugin          | search in-IDE             |
| VEML6075         | SamacSys plugin          | search in-IDE             |
| SCD41            | KiCad built-in / SnapEDA | symbol chooser / download |
| SEN55            | SnapEDA / SparkFun repo  | download / git clone      |
| SEN0322          | SamacSys / SnapEDA       | search in-IDE             |
| MICS-6814        | SamacSys / SnapEDA       | search in-IDE             |
| SPEC-O3          | connettore manuale       | 5 min                     |
| TDS probe        | connettore manuale       | 5 min                     |
| u-blox M10       | u-blox.com / SparkFun    | download                  |
| WM8960           | SamacSys plugin          | search in-IDE             |
| INMP441          | SamacSys plugin          | search in-IDE             |
| BQ25895          | SamacSys plugin          | search in-IDE             |
| MAX17048         | SamacSys plugin          | search in-IDE             |
| MCP23017         | SamacSys plugin          | search in-IDE             |
| OV2640           | SamacSys plugin          | search in-IDE             |
| BB Q10 keyboard  | simbolo manuale          | 10 min                    |
| Waveshare 3.7"   | connettore FPC built-in  | già in KiCad              |
| AP2112K          | SamacSys plugin          | search in-IDE             |
