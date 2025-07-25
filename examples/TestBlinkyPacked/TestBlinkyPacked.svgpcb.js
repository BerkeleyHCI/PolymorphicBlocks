const board = new PCB();

// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 1.907), rotate: 0,
  id: 'J1'
})
// usb.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.162), rotate: 0,
  id: 'R1'
})
// usb.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.162), rotate: 0,
  id: 'R2'
})
// reg.ic
const U1 = board.add(SOT_23_6, {
  translate: pt(0.618, 1.809), rotate: 0,
  id: 'U1'
})
// reg.fb.div.top_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(0.946, 1.944), rotate: 0,
  id: 'R3'
})
// reg.fb.div.bottom_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(0.595, 2.061), rotate: 0,
  id: 'R4'
})
// reg.hf_in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(0.751, 2.061), rotate: 0,
  id: 'C1'
})
// reg.vbst_cap
const C2 = board.add(C_0603_1608Metric, {
  translate: pt(0.907, 2.061), rotate: 0,
  id: 'C2'
})
// reg.power_path.inductor
const L1 = board.add(L_0805_2012Metric, {
  translate: pt(0.779, 1.949), rotate: 0,
  id: 'L1'
})
// reg.power_path.in_cap.cap
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(0.805, 1.781), rotate: 0,
  id: 'C3'
})
// reg.power_path.out_cap.cap
const C4 = board.add(C_0805_2012Metric, {
  translate: pt(0.604, 1.954), rotate: 0,
  id: 'C4'
})
// mcu.ic
const U2 = board.add(ESP32_WROOM_32, {
  translate: pt(0.945, 0.414), rotate: 0,
  id: 'U2'
})
// mcu.vcc_cap0.cap
const C5 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.789), rotate: 0,
  id: 'C5'
})
// mcu.vcc_cap1.cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.773), rotate: 0,
  id: 'C6'
})
// mcu.prog.conn
const J2 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.000, 0.370), rotate: 0,
  id: 'J2'
})
// mcu.boot.package
const SW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.096, 0.593), rotate: 0,
  id: 'SW1'
})
// mcu.en_pull.rc.r
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.773), rotate: 0,
  id: 'R5'
})
// mcu.en_pull.rc.c
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.903), rotate: 0,
  id: 'C7'
})
// sw.package
const SW2 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.289, 1.854), rotate: 0,
  id: 'SW2'
})
// led.led[0].package
const D1 = board.add(LED_0603_1608Metric, {
  translate: pt(1.633, 1.771), rotate: 0,
  id: 'D1'
})
// led.led[1].package
const D2 = board.add(LED_0603_1608Metric, {
  translate: pt(1.789, 1.771), rotate: 0,
  id: 'D2'
})
// led.led[2].package
const D3 = board.add(LED_0603_1608Metric, {
  translate: pt(1.633, 1.868), rotate: 0,
  id: 'D3'
})
// led.led[3].package
const D4 = board.add(LED_0603_1608Metric, {
  translate: pt(1.789, 1.868), rotate: 0,
  id: 'D4'
})
// res_pack
const RN1 = board.add(R_Array_Concave_4x0603, {
  translate: pt(2.027, 1.816), rotate: 0,
  id: 'RN1'
})

board.setNetlist([
  {name: "usb.gnd", pads: [["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["U1", "1"], ["U2", "1"], ["U2", "15"], ["U2", "38"], ["U2", "39"], ["SW2", "2"], ["J1", "S1"], ["C1", "2"], ["C5", "2"], ["C6", "2"], ["J2", "4"], ["SW1", "2"], ["R4", "2"], ["C7", "2"], ["RN1", "8"], ["RN1", "7"], ["RN1", "6"], ["RN1", "5"], ["R1", "1"], ["R2", "1"], ["C3", "2"], ["C4", "2"]]},
  {name: "usb.pwr", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["U1", "3"], ["U1", "5"], ["C1", "1"], ["C3", "1"]]},
  {name: "reg.pwr_out", pads: [["U2", "2"], ["R3", "1"], ["C5", "1"], ["C6", "1"], ["J2", "1"], ["R5", "1"], ["L1", "2"], ["C4", "1"]]},
  {name: "sw.out", pads: [["U2", "8"], ["SW2", "1"]]},
  {name: "mcu.gpio.led_0", pads: [["U2", "26"], ["D1", "2"]]},
  {name: "mcu.gpio.led_1", pads: [["U2", "27"], ["D2", "2"]]},
  {name: "mcu.gpio.led_2", pads: [["U2", "28"], ["D3", "2"]]},
  {name: "mcu.gpio.led_3", pads: [["U2", "29"], ["D4", "2"]]},
  {name: "res_pack.a.0", pads: [["RN1", "1"], ["D1", "1"]]},
  {name: "res_pack.a.1", pads: [["RN1", "2"], ["D2", "1"]]},
  {name: "res_pack.a.2", pads: [["RN1", "3"], ["D3", "1"]]},
  {name: "res_pack.a.3", pads: [["RN1", "4"], ["D4", "1"]]},
  {name: "usb.usb.dp", pads: [["J1", "A6"], ["J1", "B6"]]},
  {name: "usb.usb.dm", pads: [["J1", "A7"], ["J1", "B7"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "reg.fb.output", pads: [["U1", "4"], ["R3", "2"], ["R4", "1"]]},
  {name: "reg.vbst_cap.neg", pads: [["C2", "2"], ["U1", "2"], ["L1", "1"]]},
  {name: "reg.vbst_cap.pos", pads: [["C2", "1"], ["U1", "6"]]},
  {name: "mcu.program_uart_node.a_tx", pads: [["U2", "35"], ["J2", "2"]]},
  {name: "mcu.program_uart_node.b_tx", pads: [["U2", "34"], ["J2", "3"]]},
  {name: "mcu.program_en_node", pads: [["U2", "3"], ["R5", "2"], ["C7", "1"]]},
  {name: "mcu.program_boot_node", pads: [["U2", "25"], ["SW1", "1"]]},
  {name: "mcu.ic.io2", pads: [["U2", "24"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.5401574803149614, 2.308661417322835);
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


