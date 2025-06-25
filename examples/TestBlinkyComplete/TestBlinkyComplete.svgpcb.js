const board = new PCB();

// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.111, 0.165), rotate: 0,
  id: 'J1'
})
// usb.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.960, 0.420), rotate: 0,
  id: 'R1'
})
// usb.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(1.116, 0.420), rotate: 0,
  id: 'R2'
})
// reg.ic
const U1 = board.add(SOT_23_6, {
  translate: pt(0.081, 0.804), rotate: 0,
  id: 'U1'
})
// reg.fb.div.top_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 0.939), rotate: 0,
  id: 'R3'
})
// reg.fb.div.bottom_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 0.939), rotate: 0,
  id: 'R4'
})
// reg.hf_in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.939), rotate: 0,
  id: 'C1'
})
// reg.vbst_cap
const C2 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.036), rotate: 0,
  id: 'C2'
})
// reg.power_path.inductor
const L1 = board.add(L_0603_1608Metric, {
  translate: pt(0.214, 1.036), rotate: 0,
  id: 'L1'
})
// reg.power_path.in_cap.cap
const C3 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 1.036), rotate: 0,
  id: 'C3'
})
// reg.power_path.out_cap.cap
const C4 = board.add(C_0805_2012Metric, {
  translate: pt(0.268, 0.776), rotate: 0,
  id: 'C4'
})
// mcu.swd.conn
const J2 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(0.614, 0.146), rotate: 0,
  id: 'J2'
})
// mcu.ic
const U2 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'U2'
})
// mcu.pwr_cap[0].cap
const C5 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 0.483), rotate: 0,
  id: 'C5'
})
// mcu.pwr_cap[1].cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(0.231, 0.474), rotate: 0,
  id: 'C6'
})
// mcu.pwr_cap[2].cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(0.387, 0.474), rotate: 0,
  id: 'C7'
})
// mcu.pwr_cap[3].cap
const C8 = board.add(C_0603_1608Metric, {
  translate: pt(0.543, 0.474), rotate: 0,
  id: 'C8'
})
// mcu.vdda_cap_0.cap
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(0.699, 0.474), rotate: 0,
  id: 'C9'
})
// mcu.vdda_cap_1.cap
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.590), rotate: 0,
  id: 'C10'
})
// led.package
const D1 = board.add(LED_0603_1608Metric, {
  translate: pt(0.605, 0.766), rotate: 0,
  id: 'D1'
})
// led.res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(0.605, 0.863), rotate: 0,
  id: 'R5'
})

board.setNetlist([
  {name: "usb.gnd", pads: [["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["U1", "1"], ["U2", "8"], ["U2", "23"], ["U2", "35"], ["U2", "47"], ["U2", "44"], ["R5", "2"], ["J1", "S1"], ["C1", "2"], ["C5", "2"], ["C6", "2"], ["C7", "2"], ["C8", "2"], ["C9", "2"], ["C10", "2"], ["R4", "2"], ["R1", "1"], ["R2", "1"], ["J2", "3"], ["J2", "5"], ["J2", "9"], ["C3", "2"], ["C4", "2"]]},
  {name: "usb.pwr", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["U1", "3"], ["U1", "5"], ["C1", "1"], ["C3", "1"]]},
  {name: "reg.pwr_out", pads: [["U2", "1"], ["U2", "9"], ["U2", "24"], ["U2", "36"], ["U2", "48"], ["R3", "1"], ["J2", "1"], ["C5", "1"], ["C6", "1"], ["C7", "1"], ["C8", "1"], ["C9", "1"], ["C10", "1"], ["L1", "2"], ["C4", "1"]]},
  {name: "led.signal", pads: [["U2", "10"], ["D1", "2"]]},
  {name: "usb.usb.dp", pads: [["J1", "A6"], ["J1", "B6"]]},
  {name: "usb.usb.dm", pads: [["J1", "A7"], ["J1", "B7"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "reg.fb.output", pads: [["U1", "4"], ["R3", "2"], ["R4", "1"]]},
  {name: "reg.vbst_cap.neg", pads: [["C2", "2"], ["U1", "2"], ["L1", "1"]]},
  {name: "reg.vbst_cap.pos", pads: [["C2", "1"], ["U1", "6"]]},
  {name: "mcu.swd_node.swdio", pads: [["U2", "34"], ["J2", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["U2", "37"], ["J2", "4"]]},
  {name: "mcu.reset_node", pads: [["U2", "7"], ["J2", "10"]]},
  {name: "mcu.swd.swo", pads: [["J2", "6"]]},
  {name: "mcu.swd.tdi", pads: [["J2", "8"]]},
  {name: "mcu.ic.osc.xtal_in", pads: [["U2", "5"]]},
  {name: "mcu.ic.osc.xtal_out", pads: [["U2", "6"]]},
  {name: "led.res.a", pads: [["R5", "1"], ["D1", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.4385826771653545, 1.1826771653543309);
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


