# Bill of Materials — RGB Earring + Cradle

## Orecchino (×2 — un set)

| Ref       | Descrizione                        | Valore / Package   | Qty | Note                              |
|-----------|------------------------------------|--------------------|-----|-----------------------------------|
| J1        | LiPo 30 mAh con protezione integrata | 12×8×3 mm         | 1   | es. Adafruit #4236 o equiv.      |
| SW1       | Reed switch SMD Normally Open      | 2-pin SMD          | 1   | distanza att. ≤ 5 mm dal magnete |
| Q1        | PMOS SI2313BDS o equivalente       | SOT-23             | 1   | Vth ≈ −0.5 V, Vds max 20 V      |
| Q2–Q4     | NMOS 2N7002 (×3)                   | SOT-23             | 3   | uno per canale R, G, B           |
| U1        | CD4069UB hex inverter CMOS         | TSSOP-14           | 1   | servono solo 3 delle 6 porte     |
| D1        | LED rosso 0603                     | 0603               | 1   | Vf ≈ 2.0 V @ 2 mA               |
| D2        | LED verde 0603                     | 0603               | 1   | Vf ≈ 2.9 V @ 2 mA               |
| D3        | LED blu 0603                       | 0603               | 1   | Vf ≈ 2.9 V @ 2 mA               |
| R1        | 100 kΩ                             | 0402               | 1   | pull-up PMOS gate                |
| R2        | 2.2 MΩ                             | 0402               | 1   | oscillatore rosso                |
| R3        | 220 kΩ                             | 0402               | 1   | smoother rosso                   |
| R4        | 150 Ω                              | 0402               | 1   | current limit LED rosso          |
| R5        | 3.3 MΩ                             | 0402               | 1   | oscillatore verde                |
| R6        | 220 kΩ                             | 0402               | 1   | smoother verde                   |
| R7        | 47 Ω                               | 0402               | 1   | current limit LED verde          |
| R8        | 4.7 MΩ                             | 0402               | 1   | oscillatore blu                  |
| R9        | 220 kΩ                             | 0402               | 1   | smoother blu                     |
| R10       | 47 Ω                               | 0402               | 1   | current limit LED blu            |
| LDR1      | LDR GL5528 o equiv. SMD            | 5 mm o SMD         | 1   | 10 kΩ luce / 1 MΩ buio          |
| C1        | 100 nF decoupling                  | 0402               | 1   | VCC bypass                       |
| C2,C4,C6  | 33 µF tantalio (×3)                | 1206 pol.          | 3   | condensatori oscillatori         |
| C3,C5,C7  | 47 µF tantalio (×3)                | 1206 pol.          | 3   | condensatori smoother            |
| —         | Contatti pogo femmina (×2)         | —                  | 1   | BAT+ e GND, passo 2.54 mm       |

## Alcova di ricarica (cradle ×1)

### Alimentazione interna cradle

| Ref          | Descrizione                          | Valore / Package   | Qty | Note                                      |
|--------------|--------------------------------------|--------------------|-----|-------------------------------------------|
| J_USB        | Connettore USB-C 16-pin SMD          | SMD mid-mount      | 1   | con pin CC1, CC2, VBUS, GND              |
| R_CC1,R_CC2  | 5.1 kΩ (×2)                         | 0402               | 2   | resistori CC USB-C (5V/0.9A)              |
| C_USB        | 10 µF                                | 0805               | 1   | bulk input USB-C                          |
| U_CHG0       | TP4056 LiPo charger (cradle)        | SOP-8              | 1   | carica la batteria interna del cradle     |
| R_PROG_0     | 2.4 kΩ                              | 0402               | 1   | I_CHG = 1200/2400 = 500 mA               |
| C_OUT_0      | 10 µF                                | 0805               | 1   | output filter TP4056_0                    |
| LED_CHG_0    | LED rosso 0603                       | 0603               | 1   | cradle in carica (da USB)                 |
| LED_DONE_0   | LED verde 0603                       | 0603               | 1   | cradle battery piena                      |
| R_CHG_0      | 1 kΩ                                 | 0402               | 1   | current limit LED_CHG_0                   |
| R_DONE_0     | 1 kΩ                                 | 0402               | 1   | current limit LED_DONE_0                  |
| BAT_CRADLE   | LiPo 1 Ah con protezione integrata  | ~25×14×5 mm        | 1   | es. Adafruit #1578 o equivalente          |

### Boost converter (batteria cradle → 5V per TP4056 earrings)

| Ref          | Descrizione                          | Valore / Package   | Qty | Note                                      |
|--------------|--------------------------------------|--------------------|-----|-------------------------------------------|
| U_BOOST      | MT3608 boost converter               | SOT-23-6           | 1   | 3.7 V → 5 V, fino a 2 A                  |
| L1           | Induttore 22 µH                      | 4×4 mm SMD         | 1   | per boost MT3608                          |
| D1           | Schottky SS34                        | SMA                | 1   | diodo rettificatore boost                 |
| C_IN_B       | 10 µF                                | 0805               | 1   | input decoupling boost                    |
| C_OUT_B      | 22 µF                                | 0805               | 1   | output filter boost                       |
| R_FB1        | 100 kΩ                               | 0402               | 1   | Vout = 1.25×(1 + R_FB1/R_FB2)            |
| R_FB2        | 33 kΩ                                | 0402               | 1   | → Vout ≈ 5.04 V                          |

### Caricatori orecchini

| Ref          | Descrizione                          | Valore / Package   | Qty | Note                                      |
|--------------|--------------------------------------|--------------------|-----|-------------------------------------------|
| U2, U3       | TP4056 LiPo charger (×2)            | SOP-8              | 2   | uno per orecchino; VCC = VBOOST 5V       |
| R_PROG_L/R   | 40 kΩ (×2)                          | 0402               | 2   | I_CHG = 1200/40k = 30 mA                 |
| C_OUT_L/R    | 10 µF (×2)                          | 0805               | 2   | output filter TP4056 earring              |
| R_CHG_L/R    | 1 kΩ (×2)                           | 0402               | 2   | current limit LED CHRG earring            |
| R_DONE_L/R   | 1 kΩ (×2)                           | 0402               | 2   | current limit LED STDBY earring           |
| LED_CHG_L/R  | LED rosso 0603 (×2)                  | 0603               | 2   | slot SX/DX in carica                      |
| LED_DONE_L/R | LED verde 0603 (×2)                  | 0603               | 2   | slot SX/DX carica completata              |
| POGO_L/R     | Contatti pogo maschio (×4 tot.)      | ⌀1 mm, h=3mm       | 4   | 2 per orecchino (BAT+, GND)              |
| MAG_L/R      | Magnete neodimio (×2 per slot)       | ⌀3×1.5 mm N42      | 4   | allineamento + trigger Reed switch        |

## Note costruttive

- **TP4056 pin TEMP**: collegare direttamente a VCC per disabilitare il monitoraggio NTC
- **TP4056 CHRG/STDBY**: open-drain attivi bassi → LED con R da 1 kΩ verso VBOOST; catodo al pin TP4056
- **MT3608 EN**: collegare a VIN per tenere il boost sempre attivo (il quiescent è ~1 mA)
- **Polarità magneti**: verificare che il polo corretto del magnete nel cradle sia rivolto verso il Reed switch nell'orecchino
- **PCB orecchino**: 0.6 mm FR4 o flex PI; < 2 g totali con LiPo incollata sul retro
- **USB-C senza PD**: le 5.1 kΩ sui CC richiedono solo 5 V/0.9 A — sufficiente per ricaricare il cradle a 500 mA
- **Flusso di potenza**: USB-C → cradle LiPo → boost 5V → earring TP4056. Se USB non collegato, il cradle funziona da powerbank per gli orecchini
- **Corrente max dalla batteria cradle**: 66 mA (2× earring 30 mA + boost overhead + LED) — la 1Ah dura ~15 h in standby o 15 cicli di ricarica completa degli orecchini
