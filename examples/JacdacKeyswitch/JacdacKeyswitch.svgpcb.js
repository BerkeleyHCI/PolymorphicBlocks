const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.862, 1.038), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.902, 1.038), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.862, 1.078), rotate: 0,
  id: 'H3'
})
// edge.conn
const EC1 = board.add(JD_PEC_02_Prerouted_recessed, {
  translate: pt(0.113, 0.883), rotate: 0,
  id: 'EC1'
})
// edge.status_led.package
const D1 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 0.718), rotate: 0,
  id: 'D1'
})
// edge.status_led.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 0.815), rotate: 0,
  id: 'R1'
})
// edge.tvs_jd_pwr.diode
const D2 = board.add(D_0402_1005Metric, {
  translate: pt(0.193, 0.805), rotate: 0,
  id: 'D2'
})
// edge.tvs_jd_data.diode
const D3 = board.add(D_0402_1005Metric, {
  translate: pt(0.037, 0.902), rotate: 0,
  id: 'D3'
})
// jd_mh1
const MH1 = board.add(jacdac_hole_DATA_notched_MH1, {
  translate: pt(1.020, 1.038), rotate: 0,
  id: 'MH1'
})
// jd_mh2
const MH2 = board.add(jacdac_hole_GND_MH2, {
  translate: pt(1.059, 1.038), rotate: 0,
  id: 'MH2'
})
// jd_mh3
const MH3 = board.add(jacdac_hole_PWR_MH3, {
  translate: pt(1.098, 1.038), rotate: 0,
  id: 'MH3'
})
// jd_mh4
const MH4 = board.add(jacdac_hole_GND_MH4, {
  translate: pt(1.138, 1.038), rotate: 0,
  id: 'MH4'
})
// edge2.conn
const EC2 = board.add(JD_PEC_02_Prerouted_recessed, {
  translate: pt(0.460, 0.883), rotate: 0,
  id: 'EC2'
})
// edge2.status_led.package
const D4 = board.add(LED_0603_1608Metric, {
  translate: pt(0.406, 0.718), rotate: 0,
  id: 'D4'
})
// edge2.status_led.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(0.406, 0.815), rotate: 0,
  id: 'R2'
})
// edge2.tvs_jd_pwr.diode
const D5 = board.add(D_0402_1005Metric, {
  translate: pt(0.540, 0.805), rotate: 0,
  id: 'D5'
})
// edge2.tvs_jd_data.diode
const D6 = board.add(D_0402_1005Metric, {
  translate: pt(0.384, 0.902), rotate: 0,
  id: 'D6'
})
// tp_gnd.tp
const TP1 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.085, 1.091), rotate: 0,
  id: 'TP1'
})
// tp_jd_pwr.tp
const TP2 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.372, 1.091), rotate: 0,
  id: 'TP2'
})
// reg_3v3.ic
const U1 = board.add(SOT_23_5, {
  translate: pt(0.775, 0.756), rotate: 0,
  id: 'U1'
})
// reg_3v3.in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(0.753, 0.891), rotate: 0,
  id: 'C1'
})
// reg_3v3.out_cap.cap
const C2 = board.add(C_0603_1608Metric, {
  translate: pt(0.909, 0.891), rotate: 0,
  id: 'C2'
})
// tp_3v3.tp
const TP3 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.659, 1.091), rotate: 0,
  id: 'TP3'
})
// mcu.swd.conn
const J1 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(0.870, 0.325), rotate: 0,
  id: 'J1'
})
// mcu.ic
const U2 = board.add(QFN_28_4x4mm_P0_5mm, {
  translate: pt(0.836, 0.104), rotate: 0,
  id: 'U2'
})
// mcu.pwr_cap0.cap
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(1.114, 0.285), rotate: 0,
  id: 'C3'
})
// mcu.pwr_cap1.cap
const C4 = board.add(C_0603_1608Metric, {
  translate: pt(0.791, 0.472), rotate: 0,
  id: 'C4'
})
// sw.package
const SW1 = board.add(SW_Hotswap_Kailh_MX, {
  translate: pt(0.307, 0.285), rotate: 0,
  id: 'SW1'
})
// rgb.package
const D7 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(1.126, 0.744), rotate: 0,
  id: 'D7'
})
// rgb.red_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(1.265, 0.718), rotate: 0,
  id: 'R3'
})
// rgb.green_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(1.143, 0.867), rotate: 0,
  id: 'R4'
})
// rgb.blue_res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(1.299, 0.867), rotate: 0,
  id: 'R5'
})
// jd_if.ferrite
const FB1 = board.add(L_0603_1608Metric, {
  translate: pt(1.357, 0.143), rotate: 0,
  id: 'FB1'
})
// jd_if.rc.r
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(1.513, 0.143), rotate: 0,
  id: 'R6'
})
// jd_if.rc.c
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(1.357, 0.240), rotate: 0,
  id: 'C5'
})
// jd_if.clamp_hi
const D8 = board.add(D_SOD_323, {
  translate: pt(1.363, 0.037), rotate: 0,
  id: 'D8'
})
// jd_if.clamp_lo
const D9 = board.add(D_SOD_323, {
  translate: pt(1.528, 0.037), rotate: 0,
  id: 'D9'
})

board.setNetlist([
  {name: "jd_data.jd_data", pads: [["MH1", "MH1"], ["EC1", "1"], ["EC2", "1"], ["FB1", "1"], ["D3", "1"], ["D6", "1"]]},
  {name: "jd_pwr", pads: [["MH3", "MH3"], ["EC1", "3"], ["EC2", "3"], ["TP2", "1"], ["U1", "1"], ["D2", "1"], ["U1", "3"], ["D5", "1"], ["C1", "1"]]},
  {name: "gnd", pads: [["MH2", "MH2"], ["MH4", "MH4"], ["EC1", "2"], ["EC2", "2"], ["TP1", "1"], ["U1", "2"], ["U2", "4"], ["SW1", "2"], ["R1", "2"], ["D2", "2"], ["D3", "2"], ["D9", "2"], ["R2", "2"], ["D5", "2"], ["D6", "2"], ["C1", "2"], ["C2", "2"], ["J1", "5"], ["C3", "2"], ["C4", "2"], ["C5", "2"]]},
  {name: "jd_status", pads: [["U2", "1"], ["D1", "2"], ["D4", "2"]]},
  {name: "v3v3", pads: [["U1", "5"], ["TP3", "1"], ["U2", "3"], ["D7", "2"], ["D8", "1"], ["C2", "1"], ["J1", "1"], ["C3", "1"], ["C4", "1"]]},
  {name: "sw.out", pads: [["U2", "19"], ["SW1", "1"]]},
  {name: "rgb.signals.red", pads: [["U2", "16"], ["R3", "2"]]},
  {name: "rgb.signals.green", pads: [["U2", "17"], ["R4", "2"]]},
  {name: "rgb.signals.blue", pads: [["U2", "15"], ["R5", "2"]]},
  {name: "jd_if.signal", pads: [["U2", "26"], ["D8", "2"], ["D9", "1"], ["R6", "1"]]},
  {name: "edge.status_led.res.a", pads: [["R1", "1"], ["D1", "1"]]},
  {name: "edge2.status_led.res.a", pads: [["R2", "1"], ["D4", "1"]]},
  {name: "mcu.swd_node.swdio", pads: [["U2", "20"], ["J1", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["U2", "21"], ["J1", "4"]]},
  {name: "mcu.reset_node", pads: [["U2", "5"], ["J1", "3"]]},
  {name: "mcu.swd.swo", pads: [["J1", "6"]]},
  {name: "rgb.red_res.a", pads: [["R3", "1"], ["D7", "3"]]},
  {name: "rgb.green_res.a", pads: [["R4", "1"], ["D7", "4"]]},
  {name: "rgb.blue_res.a", pads: [["R5", "1"], ["D7", "1"]]},
  {name: "jd_if.ferrite.b", pads: [["FB1", "2"], ["R6", "2"], ["C5", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.709448818897638, 1.2625984251968505);
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


