# RGB Earring — Puro Analogico

Orecchino RGB senza microcontrollore: tre oscillatori CMOS a frequenze
irrazionali producono una rotazione cromatica infinita e non ripetuta.
Ricarica tramite alcova magnetica con contatti pogo.

## Struttura progetto

```
earrings/rbg/
├── README.md              ← questo file
├── BOM.md                 ← lista componenti con package e fornitori
└── schematics/
    ├── earring.html       ← schema orecchino (power + oscillatori + driver)
    └── cradle.html        ← schema alcova di ricarica (USB-C + TP4056 ×2)
```

## Come funziona

### Cambio colore

Tre porte NOT del CD4069UB formano tre oscillatori RC indipendenti.
Ogni oscillatore pilota un LED (R, G, B) tramite un N-MOSFET.
Un filtro RC ("smoother") tra oscillatore e gate del MOSFET converte
l'onda quadra in una rampa morbida → il LED sfuma, non lampeggia.

| Canale | R_osc   | T oscillatore | T smoother (τ) |
|--------|---------|---------------|----------------|
| Rosso  | 2.2 MΩ | ≈ 102 s       | ≈ 10 s         |
| Verde  | 3.3 MΩ | ≈ 152 s       | ≈ 10 s         |
| Blu    | 4.7 MΩ | ≈ 217 s       | ≈ 10 s         |

I rapporti tra i periodi sono irrazionali → il pattern non si ripete mai.

### Auto-spegnimento nel cradle

Il cradle contiene un magnete. Il Reed Switch (NO) nell'orecchino:
- **Nel cradle** → Reed chiuso → GATE_P = VBATT → Q1 (PMOS) OFF → circuito spento
- **Fuori dal cradle** → Reed aperto → Q1 controllato da R1/LDR1 → circuito ON

### Dimming ambientale (LDR)

R1 (100 kΩ) da VBATT a GATE_P + LDR1 (GL5528) da GATE_P a GND formano
un partitore resistivo.
- Luce intensa → LDR ≈ 10 kΩ → GATE_P basso → Q1 fortemente ON → LED luminosi
- Buio → LDR ≈ 1 MΩ → GATE_P alto → Q1 parzialmente/non ON → LED tenues

### Ricarica

L'alcova espone un magnete + 2 contatti pogo per orecchino (BAT+, GND).
Due TP4056 indipendenti caricano le due LiPo a 30 mA ciascuna.
LED bicolore (rosso/verde) su ogni slot indica stato di carica.

## Note di progetto

- PCB orecchino: FR4 0.6 mm o flex poliimmide, ~15 × 20 mm
- LED verde e blu: Vf ≈ 2.7–3.0 V con batteria scarica → si spengono prima
  del rosso (l'"tramonto in rosso" è un effetto piacevole, non un difetto)
- La LiPo da 30 mAh deve avere protezione integrata (circuito DW01+FS8205)
- Se la LiPo non ce l'ha integrata, aggiungere un MCP73831 o similare
  con protezione esterna

## Segnali principali

| Net       | Descrizione                                   |
|-----------|-----------------------------------------------|
| VBATT     | Positivo LiPo (3.7 V nominale)                |
| VCC       | Uscita PMOS dopo switch di potenza            |
| GND       | Comune                                        |
| GATE_P    | Gate Q1 PMOS (controllato da R1/SW1/LDR1)    |
| GATE_R/G/B| Gate N-MOSFET per ogni canale LED             |
| OSC_R/G/B | Uscita oscillatore CD4069 (onda quadra)       |
