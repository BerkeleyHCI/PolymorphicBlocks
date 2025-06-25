const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.501, 0.935), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.540, 0.935), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.501, 0.974), rotate: 0,
  id: 'H3'
})
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 0.165), rotate: 0,
  id: 'J1'
})
// usb.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 0.420), rotate: 0,
  id: 'R1'
})
// usb.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 0.420), rotate: 0,
  id: 'R2'
})
// batt.conn
const J2 = board.add(JST_PH_S2B_PH_K_1x02_P2_00mm_Horizontal, {
  translate: pt(0.633, 0.266), rotate: 0,
  id: 'J2'
})
// tp_gnd.tp
const TP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 0.972), rotate: 0,
  id: 'TP1'
})
// tp.tp
const TP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 0.972), rotate: 0,
  id: 'TP2'
})
// pmos.r1
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(0.511, 0.769), rotate: 0,
  id: 'R3'
})
// pmos.r2
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(0.667, 0.769), rotate: 0,
  id: 'R4'
})
// pmos.mp1
const Q1 = board.add(SOT_23, {
  translate: pt(0.528, 0.633), rotate: 0,
  id: 'Q1'
})
// pmos.mp2
const Q2 = board.add(SOT_23, {
  translate: pt(0.719, 0.633), rotate: 0,
  id: 'Q2'
})
// charger.ic
const U1 = board.add(SOT_23_5, {
  translate: pt(0.081, 0.633), rotate: 0,
  id: 'U1'
})
// charger.vdd_cap.cap
const C1 = board.add(C_0805_2012Metric, {
  translate: pt(0.268, 0.605), rotate: 0,
  id: 'C1'
})
// charger.vbat_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 0.778), rotate: 0,
  id: 'C2'
})
// charger.prog_res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(0.231, 0.769), rotate: 0,
  id: 'R5'
})
// charge_led.package
const D1 = board.add(LED_0603_1608Metric, {
  translate: pt(0.971, 0.595), rotate: 0,
  id: 'D1'
})
// charge_led.res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(0.971, 0.693), rotate: 0,
  id: 'R6'
})
// pmos_load.fet
const Q3 = board.add(SOT_23, {
  translate: pt(1.223, 0.633), rotate: 0,
  id: 'Q3'
})
// pwr_pins
const J3 = board.add(JST_PH_S3B_PH_K_1x03_P2_00mm_Horizontal, {
  translate: pt(1.023, 0.266), rotate: 0,
  id: 'J3'
})

board.setNetlist([
  {name: "vusb", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["U1", "4"], ["D1", "2"], ["C1", "1"]]},
  {name: "gnd", pads: [["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["J3", "1"], ["J3", "3"], ["J2", "1"], ["TP1", "1"], ["R3", "2"], ["U1", "2"], ["Q3", "1"], ["J1", "S1"], ["R5", "2"], ["C1", "2"], ["C2", "2"], ["R1", "1"], ["R2", "1"]]},
  {name: "batt.pwr", pads: [["J2", "2"], ["TP2", "1"], ["R4", "2"], ["Q1", "1"], ["Q2", "3"]]},
  {name: "charger.pwr_bat", pads: [["U1", "3"], ["Q1", "2"], ["Q2", "2"], ["R4", "1"], ["C2", "1"], ["Q3", "3"]]},
  {name: "charge_led.signal", pads: [["U1", "1"], ["R6", "2"]]},
  {name: "pmos_load.pwr_out", pads: [["J3", "2"], ["Q3", "2"]]},
  {name: "usb.usb.dp", pads: [["J1", "A6"], ["J1", "B6"]]},
  {name: "usb.usb.dm", pads: [["J1", "A7"], ["J1", "B7"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "pmos.r1.a", pads: [["R3", "1"], ["Q1", "3"], ["Q2", "1"]]},
  {name: "charger.prog_res.a", pads: [["R5", "1"], ["U1", "5"]]},
  {name: "charge_led.res.a", pads: [["R6", "1"], ["D1", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.416732283464567, 1.1279527559055118);
const xMin = Math.min(limit0[0], limit1[0]);
const xMax = Math.max(limit0[0], limit1[0]);
const yMin = Math.min(limit0[1], limit1[1]);
const yMax = Math.max(limit0[1], limit1[1]);

const filletRadius = 0.1;
const outline = path(
  [(xMin+xMax/2), yMax],
  ["fillet", filletRadius, [xMax, yMax]],
  ["fillet", filletRadius, [xMax, yMin]],
  ["fillet", filletRadius, [xMin, yMin]],
  ["fillet", filletRadius, [xMin, yMax]],
  [(xMin+xMax/2), yMax],
);
board.addShape("outline", outline);

renderPCB({
  pcb: board,
  layerColors: {
    "F.Paste": "#000000ff",
    "F.Mask": "#000000ff",
    "B.Mask": "#000000ff",
    "componentLabels": "#00e5e5e5",
    "outline": "#002d00ff",
    "padLabels": "#ffff99e5",
    "B.Cu": "#ef4e4eff",
    "F.Cu": "#ff8c00cc",
  },
  limits: {
    x: [xMin, xMax],
    y: [yMin, yMax]
  },
  background: "#00000000",
  mmPerUnit: 25.4
})


