#!/usr/bin/env python3
"""RGB Earring — KiCad 7 Schematic Generator v2
Layout pulito, fili reali, flow sinistra→destra.
"""
import uuid, sys

def uid(): return str(uuid.uuid4())
G = 2.54
def g(n): return round(n * G, 3)

_buf = []
def out(s): _buf.append(s)
def wire(x1,y1,x2,y2):
    out(f'  (wire (pts (xy {x1:.3f} {y1:.3f}) (xy {x2:.3f} {y2:.3f}))\n    (stroke (width 0) (type default)) (uuid "{uid()}"))')
def junc(x,y):
    out(f'  (junction (at {x:.3f} {y:.3f}) (diameter 0) (color 0 0 0 0)\n    (uuid "{uid()}"))')
def noconn(x,y):
    out(f'  (no_connect (at {x:.3f} {y:.3f}) (uuid "{uid()}"))')
def lbl(text,x,y,angle=0):
    out(f'  (label "{text}" (at {x:.3f} {y:.3f} {angle})\n    (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid()}"))')

def pwr_sym(name,x,y,angle=0):
    ref=f"#PWR{uid()[:4]}"
    out(f'  (symbol (lib_id "power:{name}")\n    (at {x:.3f} {y:.3f} {angle}) (unit 1)\n    (exclude_from_sim no)(in_bom no)(on_board no)\n    (uuid "{uid()}")\n    (property "Reference" "{ref}" (at {x:.3f} {y+1.27:.3f} 0)\n      (effects (font (size 1.27 1.27)) hide))\n    (property "Value" "{name}" (at {x:.3f} {y-1.778:.3f} 0)\n      (effects (font (size 1.27 1.27))))\n    (property "Footprint" "" (at 0 0 0)\n      (effects (font (size 1.27 1.27)) hide))\n    (property "Datasheet" "" (at 0 0 0)\n      (effects (font (size 1.27 1.27)) hide))\n    (pin "1" (uuid "{uid()}"))\n    (instances (project "earring"\n      (path "/{uid()}" (reference "{ref}") (unit 1))))\n  )')

def gnd(x,y): pwr_sym("GND",x,y)
def vcc(x,y): pwr_sym("VCC",x,y)

def comp(lib_id,x,y,ref,value,fp,unit=1,angle=0,
         rdx=1.524,rdy=0,ra=90,vdx=-1.524,vdy=0,va=90):
    rx,ry=x+rdx,y+rdy; vx2,vy=x+vdx,y+vdy
    out(f'  (symbol (lib_id "{lib_id}")\n    (at {x:.3f} {y:.3f} {angle}) (unit {unit})\n    (exclude_from_sim no)(in_bom yes)(on_board yes)\n    (uuid "{uid()}")\n    (property "Reference" "{ref}" (at {rx:.3f} {ry:.3f} {ra})\n      (effects (font (size 1.27 1.27))))\n    (property "Value" "{value}" (at {vx2:.3f} {vy:.3f} {va})\n      (effects (font (size 1.27 1.27))))\n    (property "Footprint" "{fp}" (at {x:.3f} {y:.3f} 0)\n      (effects (font (size 1.27 1.27)) hide))\n    (property "Datasheet" "~" (at {x:.3f} {y:.3f} 0)\n      (effects (font (size 1.27 1.27)) hide))\n    (pin "1" (uuid "{uid()}"))\n    (instances (project "earring"\n      (path "/{uid()}" (reference "{ref}") (unit {unit}))))\n  )')

RP,CP,LP=3.81,2.54,3.81

def R(ref,val,x,y,fp="Resistor_SMD:R_0402_1005Metric",angle=0):
    if angle==0:
        comp("Device:R",x,y,ref,val,fp,rdx=1.524,rdy=0,ra=90,vdx=-1.524,vdy=0,va=90)
    else:
        comp("Device:R",x,y,ref,val,fp,angle=90,rdx=0,rdy=-1.524,ra=0,vdx=0,vdy=1.524,va=0)

def rt(x,y): return (x,y-RP)
def rb(x,y): return (x,y+RP)
def rl(x,y): return (x-RP,y)
def rr(x,y): return (x+RP,y)

def C(ref,val,x,y,polar=False,fp="Capacitor_SMD:C_0402_1005Metric"):
    lib="Device:C_Polarized" if polar else "Device:C"
    fp2="Capacitor_SMD:C_1206_3216Metric" if polar else fp
    comp(lib,x,y,ref,val,fp2,rdx=1.016,rdy=0,ra=90,vdx=-1.016,vdy=0,va=90)

def ct(x,y): return (x,y-CP)
def cb(x,y): return (x,y+CP)

def LED(ref,val,x,y,fp="LED_SMD:LED_0603_1608Metric"):
    comp("Device:LED",x,y,ref,val,fp,rdx=0,rdy=-2.54,ra=0,vdx=0,vdy=2.54,va=0)

def la(x,y): return (x-LP,y)
def lk(x,y): return (x+LP,y)

def NMOS(ref,x,y):
    comp("Transistor_FET:2N7002",x,y,ref,"2N7002","Package_TO_SOT_SMD:SOT-23",
         rdx=3,rdy=-2,ra=0,vdx=3,vdy=2,va=0)

def ng(x,y): return (x-2.54,y)
def nd(x,y): return (x+3.81,y-5.08)
def ns(x,y): return (x+3.81,y+5.08)

def PMOS(ref,x,y):
    comp("Transistor_FET:SI2313BDS",x,y,ref,"SI2313BDS","Package_TO_SOT_SMD:SOT-23",
         rdx=3,rdy=-2,ra=0,vdx=3,vdy=2,va=0)

def pg(x,y): return (x-2.54,y)
def ps(x,y): return (x+3.81,y-5.08)
def pd2(x,y): return (x+3.81,y+5.08)

def GATE(ref,unit,x,y):
    comp("74xx:CD4069UB",x,y,ref,"CD4069UB","Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
         unit=unit,rdx=0,rdy=-3.81,ra=0,vdx=0,vdy=3.81,va=0)

def ga(x,y): return (x-5.08,y)
def gy(x,y): return (x+5.08,y)

def GPWR(ref,x,y):
    comp("74xx:CD4069UB",x,y,ref,"CD4069UB","Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
         unit=7,rdx=4,rdy=0,ra=0,vdx=-4,vdy=0,va=0)

def gvdd(x,y): return (x,y-5.08)
def ggnd(x,y): return (x,y+5.08)

def REED(ref,x,y):
    comp("Device:SW_Reed",x,y,ref,"Reed_NO","Standex-Meder_OrkR60_Handsoldering",
         rdx=0,rdy=-3.81,ra=0,vdx=0,vdy=3.81,va=0)

def ra2(x,y): return (x-3.81,y)
def rb2(x,y): return (x+3.81,y)

def CONN(ref,val,x,y):
    comp("Connector:Conn_01x02_Pin",x,y,ref,val,
         "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
         rdx=0,rdy=-5.08,ra=0,vdx=0,vdy=5.08,va=0)

def cp1(x,y): return (x+2.54,y+1.27)
def cp2(x,y): return (x+2.54,y-1.27)

# ─── lib_symbols ──────────────────────────────────────────────────────────────
LIBS = r"""  (lib_symbols
    (symbol "Device:R"
      (pin_numbers hide)(pin_names (offset 0) hide)
      (exclude_from_sim no)(in_bom yes)(on_board yes)
      (property "Reference" "R" (at 1.524 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at -1.524 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "R_0_1"
        (rectangle (start -1.016 -2.286) (end 1.016 2.286)
          (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "R_1_1"
        (pin passive line (at 0 3.81 270) (length 1.524)
          (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -3.81 90) (length 1.524)
          (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
    (symbol "Device:C"
      (pin_numbers hide)(pin_names (offset 0.254) hide)
      (exclude_from_sim no)(in_bom yes)(on_board yes)
      (property "Reference" "C" (at 1.016 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (at -1.016 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "C_0_1"
        (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))
        (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none))))
      (symbol "C_1_1"
        (pin passive line (at 0 2.54 270) (length 1.778)
          (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -2.54 90) (length 1.778)
          (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
    (symbol "Device:C_Polarized"
      (pin_numbers hide)(pin_names (offset 0.254) hide)
      (exclude_from_sim no)(in_bom yes)(on_board yes)
      (property "Reference" "C" (at 1.016 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (at -1.016 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "C_Polarized_0_1"
        (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))
        (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))
        (polyline (pts (xy 0.762 1.524) (xy 1.524 1.524) (xy 1.524 0.762)) (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "C_Polarized_1_1"
        (pin passive line (at 0 2.54 270) (length 1.778)
          (name "+" (effects (font (size 1.27 1.27)))) (number "+" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -2.54 90) (length 1.778)
          (name "-" (effects (font (size 1.27 1.27)))) (number "-" (effects (font (size 1.27 1.27)))))))
    (symbol "Device:LED"
      (pin_numbers hide)(pin_names (offset 1.016) hide)
      (exclude_from_sim no)(in_bom yes)(on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "D" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "LED_0_1"
        (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27) (xy 1.27 0) (xy -1.27 -1.27))
          (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0.508) (type default)) (fill (type none)))
        (polyline (pts (xy 0.508 1.016) (xy 1.524 2.032)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -0.254 0.508) (xy 0.762 1.524)) (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "LED_1_1"
        (pin passive line (at -3.81 0 0) (length 2.54)
          (name "A" (effects (font (size 1.27 1.27)))) (number "A" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 0 180) (length 2.54)
          (name "K" (effects (font (size 1.27 1.27)))) (number "K" (effects (font (size 1.27 1.27)))))))
    (symbol "Device:SW_Reed"
      (pin_names (offset 1.016))(pin_numbers hide)
      (exclude_from_sim no)(in_bom yes)(on_board yes)
      (property "Reference" "SW" (at 0 2.794 0) (effects (font (size 1.27 1.27))))
      (property "Value" "SW_Reed" (at 0 -2.794 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "SW_Reed_0_1"
        (circle (center 0 0) (radius 2.159) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.524 -0.508) (xy 1.524 0.762)) (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "SW_Reed_1_1"
        (pin passive line (at -3.81 0 0) (length 1.651)
          (name "A" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 0 180) (length 1.651)
          (name "B" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
    (symbol "Transistor_FET:2N7002"
      (pin_names (offset 0.254))(pin_numbers hide)
      (exclude_from_sim no)(in_bom yes)(on_board yes)
      (property "Reference" "Q" (at 5.08 1.27 0) (effects (font (size 1.27 1.27))))
      (property "Value" "2N7002" (at 5.08 -1.27 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "2N7002_0_1"
        (polyline (pts (xy 1.905 0) (xy 2.54 0)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 2.54 -1.905) (xy 2.54 1.905)) (stroke (width 0.508) (type default)) (fill (type none)))
        (polyline (pts (xy 2.54 0.635) (xy 3.81 1.905) (xy 3.81 2.54)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 2.54 -0.635) (xy 3.81 -1.905) (xy 3.81 -2.54)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 3.302 -2.159) (xy 3.81 -1.905) (xy 3.302 -1.651)) (stroke (width 0) (type default)) (fill (type outline)))
        (circle (center 3.2 0) (radius 2.794) (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "2N7002_1_1"
        (pin input line (at -2.54 0 0) (length 4.445)
          (name "G" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 5.08 90) (length 2.54)
          (name "S" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 -5.08 270) (length 2.54)
          (name "D" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))))
    (symbol "Transistor_FET:SI2313BDS"
      (pin_names (offset 0.254))(pin_numbers hide)
      (exclude_from_sim no)(in_bom yes)(on_board yes)
      (property "Reference" "Q" (at 5.08 1.27 0) (effects (font (size 1.27 1.27))))
      (property "Value" "SI2313BDS" (at 5.08 -1.27 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "SI2313BDS_0_1"
        (polyline (pts (xy 1.905 0) (xy 2.54 0)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 2.54 -1.905) (xy 2.54 1.905)) (stroke (width 0.508) (type default)) (fill (type none)))
        (polyline (pts (xy 2.54 0.635) (xy 3.81 1.905) (xy 3.81 2.54)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 2.54 -0.635) (xy 3.81 -1.905) (xy 3.81 -2.54)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 3.302 2.159) (xy 3.81 1.905) (xy 3.302 1.651)) (stroke (width 0) (type default)) (fill (type outline)))
        (circle (center 3.2 0) (radius 2.794) (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "SI2313BDS_1_1"
        (pin input line (at -2.54 0 0) (length 4.445)
          (name "G" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 -5.08 270) (length 2.54)
          (name "S" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 5.08 90) (length 2.54)
          (name "D" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))))
    (symbol "Connector:Conn_01x02_Pin"
      (pin_names (offset 1.016))(pin_numbers hide)
      (exclude_from_sim no)(in_bom yes)(on_board yes)
      (property "Reference" "J" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Conn_01x02_Pin" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Conn_01x02_Pin_0_1"
        (rectangle (start -1.27 -2.54) (end 0 2.54)
          (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "Conn_01x02_Pin_1_1"
        (pin passive line (at 2.54 1.27 180) (length 2.54)
          (name "Pin_1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 2.54 -1.27 180) (length 2.54)
          (name "Pin_2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
    (symbol "74xx:CD4069UB"
      (pin_names (offset 0.254))(pin_numbers hide)
      (exclude_from_sim no)(in_bom yes)(on_board yes)
      (property "Reference" "U" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "CD4069UB" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:TSSOP-14_4.4x5mm_P0.65mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "CD4069UB_0_1"
        (polyline (pts (xy -2.54 -2.032) (xy 0 -2.032) (xy 2.54 0) (xy 0 2.032) (xy -2.54 2.032) (xy -2.54 -2.032))
          (stroke (width 0.254) (type default)) (fill (type background)))
        (circle (center 3.048 0) (radius 0.508) (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "CD4069UB_1_1"
        (pin input line (at -5.08 0 0) (length 2.54)
          (name "A" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin output inverted (at 5.08 0 180) (length 1.524)
          (name "Y" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
      (symbol "CD4069UB_2_1"
        (pin input line (at -5.08 0 0) (length 2.54)
          (name "A" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin output inverted (at 5.08 0 180) (length 1.524)
          (name "Y" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27))))))
      (symbol "CD4069UB_3_1"
        (pin input line (at -5.08 0 0) (length 2.54)
          (name "A" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin output inverted (at 5.08 0 180) (length 1.524)
          (name "Y" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27))))))
      (symbol "CD4069UB_7_1"
        (pin power_in line (at 0 -5.08 270) (length 2.54)
          (name "VDD" (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at 0 5.08 90) (length 2.54)
          (name "GND" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))))
    (symbol "power:GND"
      (pin_names (offset 0))(pin_numbers hide)
      (exclude_from_sim no)(in_bom no)(on_board no)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (at 0 -2.032 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "GND_0_1"
        (polyline (pts (xy 0 0) (xy 0 -1.524) (xy 1.27 -1.524) (xy 0 -2.794) (xy -1.27 -1.524) (xy 0 -1.524))
          (stroke (width 0) (type default)) (fill (type none))))
      (symbol "GND_1_1"
        (pin power_in line (at 0 0 90) (length 0)
          (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))
    (symbol "power:VCC"
      (pin_names (offset 0))(pin_numbers hide)
      (exclude_from_sim no)(in_bom no)(on_board no)
      (property "Reference" "#PWR" (at 0 1.27 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "VCC" (at 0 3.556 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "VCC_0_1"
        (polyline (pts (xy -0.762 0.762) (xy 0 1.524) (xy 0.762 0.762)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0 0) (xy 0 1.524)) (stroke (width 0) (type default)) (fill (type none))))
      (symbol "VCC_1_1"
        (pin power_out line (at 0 0 270) (length 0)
          (name "VCC" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))
  )"""

# ═══════════════ CIRCUIT ═════════════════════════════════════════════════════

def build_power():
    # J1 LiPo at grid (7,20)
    J1x,J1y = g(7),g(20)
    CONN("J1","LiPo_30mAh",J1x,J1y)
    p1=cp1(J1x,J1y); p2=cp2(J1x,J1y)
    VY=p1[1]           # VBATT y-level
    VXR=g(36)
    wire(p1[0],p1[1],VXR,VY)
    lbl("VBATT",VXR,VY)
    wire(p2[0],p2[1],p2[0]-2.54,p2[1]); gnd(p2[0]-2.54,p2[1])

    # SW1 Reed at (16,22)
    SW1x,SW1y=g(16),g(22)
    REED("SW1",SW1x,SW1y)
    s1a=ra2(SW1x,SW1y); s1b=rb2(SW1x,SW1y)
    wire(s1a[0],s1a[1],s1a[0],VY); wire(s1a[0],VY,p1[0],VY); junc(s1a[0],VY)
    GPX,GPY=g(24),SW1y
    wire(s1b[0],s1b[1],GPX,GPY)

    # R1 at (22,24) vertical: top→VBATT, bot→GATE_P
    R1x,R1y=g(22),g(24)
    R("R1","100k",R1x,R1y)
    wire(rt(R1x,R1y)[0],rt(R1x,R1y)[1],R1x,VY); junc(R1x,VY)
    wire(rb(R1x,R1y)[0],rb(R1x,R1y)[1],GPX,GPY); junc(GPX,GPY)

    # LDR1 at GPX,(28): GATE_P→GND
    LDx,LDy=GPX,g(28)
    R("LDR1","GL5528",LDx,LDy)
    wire(rt(LDx,LDy)[0],rt(LDx,LDy)[1],GPX,GPY)
    wire(rb(LDx,LDy)[0],rb(LDx,LDy)[1],LDx,rb(LDx,LDy)[1]+3.81)
    gnd(LDx,rb(LDx,LDy)[1]+3.81)

    # Q1 PMOS at (30,22): G=GATE_P, S=VBATT, D→VCC
    Q1x,Q1y=g(30),g(22)
    PMOS("Q1",Q1x,Q1y)
    wire(GPX,GPY,pg(Q1x,Q1y)[0],pg(Q1x,Q1y)[1])
    wire(ps(Q1x,Q1y)[0],ps(Q1x,Q1y)[1],ps(Q1x,Q1y)[0],VY)
    junc(ps(Q1x,Q1y)[0],VY); wire(ps(Q1x,Q1y)[0],VY,VXR,VY)
    VCCY=pd2(Q1x,Q1y)[1]; VCCXR=g(96)
    wire(pd2(Q1x,Q1y)[0],pd2(Q1x,Q1y)[1],VCCXR,VCCY)
    lbl("VCC",VCCXR,VCCY)

    # C1 100nF decoupling at (34,25)
    C1x,C1y=g(34),g(25)
    C("C1","100n",C1x,C1y)
    wire(ct(C1x,C1y)[0],ct(C1x,C1y)[1],C1x,VCCY); junc(C1x,VCCY)
    wire(cb(C1x,C1y)[0],cb(C1x,C1y)[1],C1x,cb(C1x,C1y)[1]+2.54)
    gnd(C1x,cb(C1x,C1y)[1]+2.54)

    # U1 power at (38,26)
    U1x,U1y=g(38),g(26)
    GPWR("U1",U1x,U1y)
    wire(gvdd(U1x,U1y)[0],gvdd(U1x,U1y)[1],U1x,VCCY); junc(U1x,VCCY)
    wire(ggnd(U1x,U1y)[0],ggnd(U1x,U1y)[1],U1x,ggnd(U1x,U1y)[1]+2.54)
    gnd(U1x,ggnd(U1x,U1y)[1]+2.54)
    return VCCY


def channel(unit, Rref, Rval, Cref, Rsref, Csref,
            Qref, Rlref, Rlval, Dref, Dval, y_row, VCCY):
    """
    One oscillator+driver channel. All wired explicitly.
    Columns on 2.54 grid:
      xA=g(42) OSC_IN/C_osc    xB=g(52) gate     xC=g(62) OSC_OUT
      xD=g(69) R_smooth        xE=g(76) GATE/Csm  xF=g(84) NMOS
    """
    xA,xB,xC,xD,xE,xF = g(42),g(52),g(62),g(69),g(76),g(84)
    y_fb = y_row - g(6)   # feedback R above gate

    # ── Feedback R (horizontal, spans xA..xC at y_fb) ────────────────────────
    Rcx = round((xA+xC)/2, 3)
    R(Rref, Rval, Rcx, y_fb, angle=90)
    # horizontal R angle=90: pin1 at (Rcx-3.81, y_fb), pin2 at (Rcx+3.81, y_fb)
    wire(xA, y_fb, rl(Rcx,y_fb)[0], y_fb)       # extend left to xA
    wire(xA, y_fb, xA, y_row)                    # drop down to gate level
    wire(rr(Rcx,y_fb)[0], y_fb, xC, y_fb)       # extend right to xC
    wire(xC, y_fb, xC, y_row)                    # drop down

    # ── CD4069 gate ───────────────────────────────────────────────────────────
    GATE(f"U1{'ABC'[unit-1]}", unit, xB, y_row)
    wire(xA, y_row, ga(xB,y_row)[0], ga(xB,y_row)[1])
    junc(xA, y_row)
    wire(gy(xB,y_row)[0], gy(xB,y_row)[1], xC, y_row)
    junc(xC, y_row)

    # ── C_osc vertical at (xA, y_row+4g) ─────────────────────────────────────
    Coy = y_row + g(4)
    C(Cref, "33u", xA, Coy, polar=True)
    wire(ct(xA,Coy)[0],ct(xA,Coy)[1], xA, y_row)
    wire(cb(xA,Coy)[0],cb(xA,Coy)[1], xA, cb(xA,Coy)[1]+g(1))
    gnd(xA, cb(xA,Coy)[1]+g(1))

    # ── R_smooth horizontal (xC..xE at y_row) ────────────────────────────────
    R(Rsref, "220k", xD, y_row, angle=90)
    wire(xC, y_row, rl(xD,y_row)[0], y_row)
    wire(rr(xD,y_row)[0], y_row, xE, y_row)
    junc(xE, y_row)

    # ── C_smooth vertical at (xE, y_row+4g) ──────────────────────────────────
    Csy = y_row + g(4)
    C(Csref, "47u", xE, Csy, polar=True)
    wire(ct(xE,Csy)[0],ct(xE,Csy)[1], xE, y_row)
    wire(cb(xE,Csy)[0],cb(xE,Csy)[1], xE, cb(xE,Csy)[1]+g(1))
    gnd(xE, cb(xE,Csy)[1]+g(1))

    # ── NMOS Q at xF ─────────────────────────────────────────────────────────
    NMOS(Qref, xF, y_row)
    wire(xE, y_row, ng(xF,y_row)[0], ng(xF,y_row)[1])
    qd=nd(xF,y_row); qs=ns(xF,y_row)
    wire(qs[0],qs[1], qs[0],qs[1]+g(1)); gnd(qs[0],qs[1]+g(1))

    # ── LED horizontal at same y as drain ────────────────────────────────────
    Dy=qd[1]; Dx=qd[0]
    Lcx=Dx-LP    # LED center: K at (Lcx+3.81)=Dx
    LED(Dref, Dval, Lcx, Dy)
    wire(lk(Lcx,Dy)[0],lk(Lcx,Dy)[1], qd[0],qd[1])   # K→D direct

    # ── R_lim vertical above LED.A ────────────────────────────────────────────
    lax=la(Lcx,Dy)[0]
    Rly=Dy - g(4)
    R(Rlref, Rlval, lax, Rly)
    wire(rb(lax,Rly)[0],rb(lax,Rly)[1], lax,Dy)       # bot→LED.A
    vcc(lax, rt(lax,Rly)[1]-g(1))                       # VCC above
    wire(rt(lax,Rly)[0],rt(lax,Rly)[1], lax,rt(lax,Rly)[1]-g(1))


def build():
    VCCY=build_power()
    # Three channels: y_row spaced by g(18)=45.72mm
    channel(1,"R2","2.2M","C2","R3","C3","Q2","R4","150","D1","LED_Red",  g(22),VCCY)
    channel(2,"R5","3.3M","C4","R6","C5","Q3","R7","47", "D2","LED_Green",g(40),VCCY)
    channel(3,"R8","4.7M","C6","R9","C7","Q4","R10","47","D3","LED_Blue", g(58),VCCY)


def generate():
    global _buf; _buf=[]
    root=uid()
    build()
    body="\n".join(_buf)
    return f"""(kicad_sch
  (version 20230121)
  (generator "kicad_sch")
  (generator_version "7.0")
  (uuid "{root}")
  (paper "A3")
  (title_block
    (title "RGB Earring — Analogico puro")
    (date "2025-05-24") (rev "1.0") (company "fulgidus")
    (comment 1 "CD4069UB × 3 oscillatori RC | 3 × 2N7002 driver LED | SI2313BDS power switch")
    (comment 2 "T_osc: R=102s G=152s B=217s — ratio irrazionale, pattern non si ripete"))
{LIBS}
{body}
  (sheet_instances (path "/" (page "1")))
)
"""

if __name__=="__main__":
    content=generate()
    with open("earring.kicad_sch","w") as f: f.write(content)
    # quick checks
    opens=content.count("("); closes=content.count(")")
    nsym=content.count('(symbol (lib_id')
    nwire=content.count('(wire ')
    njunc=content.count('(junction ')
    print(f"✅ earring.kicad_sch  {len(content):,}B")
    print(f"   parens {opens}/{closes}  syms={nsym}  wires={nwire}  junctions={njunc}")
