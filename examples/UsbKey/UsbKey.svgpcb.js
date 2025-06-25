const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.728, 0.561), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.768, 0.561), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.728, 0.601), rotate: 0,
  id: 'H3'
})
// usb
const J1 = board.add(USB_A_Pads, {
  translate: pt(0.630, 0.463), rotate: 0,
  id: 'J1'
})
// reg_3v3.ic
const U1 = board.add(UDFN_4_1EP_1x1mm_P0_65mm_EP0_48x0_48mm, {
  translate: pt(0.339, 0.591), rotate: 0,
  id: 'U1'
})
// reg_3v3.in_cap.cap
const C1 = board.add(C_0402_1005Metric, {
  translate: pt(0.340, 0.678), rotate: 0,
  id: 'C1'
})
// mcu.swd.conn
const J2 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(0.138, 0.365), rotate: 0,
  id: 'J2'
})
// mcu.ic
const U2 = board.add(QFN_32_1EP_5x5mm_P0_5mm_EP3_45x3_45mm, {
  translate: pt(0.123, 0.123), rotate: 0,
  id: 'U2'
})
// rgb.package
const D1 = board.add(LED_Lumex_SML_LX0404SIUPGUSB, {
  translate: pt(0.035, 0.597), rotate: 0,
  id: 'D1'
})
// rgb.red_res
const R1 = board.add(R_0402_1005Metric, {
  translate: pt(0.147, 0.580), rotate: 0,
  id: 'R1'
})
// rgb.green_res
const R2 = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 0.690), rotate: 0,
  id: 'R2'
})
// rgb.blue_res
const R3 = board.add(R_0402_1005Metric, {
  translate: pt(0.149, 0.690), rotate: 0,
  id: 'R3'
})
// ts1.res
const R4 = board.add(R_0402_1005Metric, {
  translate: pt(0.922, 0.580), rotate: 0,
  id: 'R4'
})
// ts2.res
const R5 = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 0.845), rotate: 0,
  id: 'R5'
})
// tss.cap
const C2 = board.add(C_0402_1005Metric, {
  translate: pt(0.417, 0.845), rotate: 0,
  id: 'C2'
})
// packed_mcu_vdda_cap.cap
const C3 = board.add(C_0402_1005Metric, {
  translate: pt(0.227, 0.845), rotate: 0,
  id: 'C3'
})
// packed_mcu_vdd1_cap.cap
const C4 = board.add(C_0603_1608Metric, {
  translate: pt(0.552, 0.590), rotate: 0,
  id: 'C4'
})

board.setNetlist([
  {name: "gnd", pads: [["J1", "4"], ["U1", "2"], ["U1", "5"], ["U2", "16"], ["U2", "32"], ["U2", "33"], ["C2", "2"], ["U2", "15"], ["U2", "3"], ["C1", "2"], ["J2", "5"], ["C4", "2"], ["C3", "2"]]},
  {name: "v3v3", pads: [["U1", "1"], ["U2", "17"], ["U2", "1"], ["U2", "5"], ["D1", "1"], ["J2", "1"], ["C4", "1"], ["C3", "1"]]},
  {name: "usb.pwr", pads: [["J1", "1"], ["U1", "4"], ["U1", "3"], ["C1", "1"]]},
  {name: "usb.usb.dp", pads: [["U2", "22"], ["J1", "3"]]},
  {name: "usb.usb.dm", pads: [["U2", "21"], ["J1", "2"]]},
  {name: "rgb.signals.red", pads: [["U2", "7"], ["R1", "2"]]},
  {name: "rgb.signals.green", pads: [["U2", "8"], ["R2", "2"]]},
  {name: "rgb.signals.blue", pads: [["U2", "9"], ["R3", "2"]]},
  {name: "ts1.io", pads: [["U2", "27"], ["R4", "1"]]},
  {name: "ts2.io", pads: [["U2", "28"], ["R5", "1"]]},
  {name: "tss.io", pads: [["U2", "29"], ["C2", "1"]]},
  {name: "mcu.swd_node.swdio", pads: [["U2", "23"], ["J2", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["U2", "24"], ["J2", "4"]]},
  {name: "mcu.swd.reset", pads: [["J2", "3"]]},
  {name: "mcu.swd.swo", pads: [["J2", "6"]]},
  {name: "mcu.ic.nrst", pads: [["U2", "4"]]},
  {name: "rgb.red_res.a", pads: [["R1", "1"], ["D1", "2"]]},
  {name: "rgb.green_res.a", pads: [["R2", "1"], ["D1", "3"]]},
  {name: "rgb.blue_res.a", pads: [["R3", "1"], ["D1", "4"]]},
  {name: "ts1.res.b", pads: [["R4", "2"]]},
  {name: "ts2.res.b", pads: [["R5", "2"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.0771653543307087, 0.9818897637795276);
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


