const board = new PCB();

// jlc_th.th1
const OH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.479, 1.698), rotate: 0,
  id: 'OH1'
})
// jlc_th.th2
const OH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.519, 1.698), rotate: 0,
  id: 'OH2'
})
// jlc_th.th3
const OH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.479, 1.737), rotate: 0,
  id: 'OH3'
})
// obd
const OU1 = board.add(J1962, {
  translate: pt(0.637, 1.698), rotate: 0,
  id: 'OU1'
})
// ferrite.fb
const OFB1 = board.add(L_0603_1608Metric, {
  translate: pt(0.303, 1.726), rotate: 0,
  id: 'OFB1'
})
// reg_3v3.ic
const OU2 = board.add(SOT_23_6, {
  translate: pt(0.081, 1.189), rotate: 0,
  id: 'OU2'
})
// reg_3v3.fb.div.top_res
const OR1 = board.add(R_0603_1608Metric, {
  translate: pt(0.452, 1.324), rotate: 0,
  id: 'OR1'
})
// reg_3v3.fb.div.bottom_res
const OR2 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.454), rotate: 0,
  id: 'OR2'
})
// reg_3v3.hf_in_cap.cap
const OC1 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.454), rotate: 0,
  id: 'OC1'
})
// reg_3v3.boot_cap
const OC2 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 1.454), rotate: 0,
  id: 'OC2'
})
// reg_3v3.power_path.inductor
const OL1 = board.add(L_1210_3225Metric, {
  translate: pt(0.291, 1.184), rotate: 0,
  id: 'OL1'
})
// reg_3v3.power_path.in_cap.cap
const OC3 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 1.341), rotate: 0,
  id: 'OC3'
})
// reg_3v3.power_path.out_cap.cap
const OC4 = board.add(C_0805_2012Metric, {
  translate: pt(0.287, 1.334), rotate: 0,
  id: 'OC4'
})
// reg_3v3.en_res
const OR3 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.551), rotate: 0,
  id: 'OR3'
})
// prot_3v3.diode
const OD1 = board.add(D_SOD_323, {
  translate: pt(0.063, 1.735), rotate: 0,
  id: 'OD1'
})
// mcu.ic
const OU3 = board.add(ESP_WROOM_02, {
  translate: pt(0.561, 0.281), rotate: 0,
  id: 'OU3'
})
// mcu.vcc_cap0.cap
const OC5 = board.add(C_0805_2012Metric, {
  translate: pt(1.228, 0.235), rotate: 0,
  id: 'OC5'
})
// mcu.vcc_cap1.cap
const OC6 = board.add(C_0603_1608Metric, {
  translate: pt(1.393, 0.226), rotate: 0,
  id: 'OC6'
})
// mcu.prog.conn
const OJ1 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(1.299, 0.079), rotate: 0,
  id: 'OJ1'
})
// mcu.en_pull.rc.r
const OR4 = board.add(R_0603_1608Metric, {
  translate: pt(1.220, 0.342), rotate: 0,
  id: 'OR4'
})
// mcu.en_pull.rc.c
const OC7 = board.add(C_0603_1608Metric, {
  translate: pt(1.376, 0.342), rotate: 0,
  id: 'OC7'
})
// can.ic
const OU4 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.774, 1.228), rotate: 0,
  id: 'OU4'
})
// can.vdd_cap.cap
const OC8 = board.add(C_0603_1608Metric, {
  translate: pt(0.687, 1.403), rotate: 0,
  id: 'OC8'
})
// ledr.package
const OD2 = board.add(LED_0603_1608Metric, {
  translate: pt(1.096, 1.151), rotate: 0,
  id: 'OD2'
})
// ledr.res
const OR5 = board.add(R_0603_1608Metric, {
  translate: pt(1.096, 1.248), rotate: 0,
  id: 'OR5'
})
// ledg.package
const OD3 = board.add(LED_0603_1608Metric, {
  translate: pt(1.331, 1.151), rotate: 0,
  id: 'OD3'
})
// ledg.res
const OR6 = board.add(R_0603_1608Metric, {
  translate: pt(1.331, 1.248), rotate: 0,
  id: 'OR6'
})
// ledw.package
const OD4 = board.add(LED_0603_1608Metric, {
  translate: pt(1.566, 1.151), rotate: 0,
  id: 'OD4'
})
// ledw.res
const OR7 = board.add(R_0603_1608Metric, {
  translate: pt(1.566, 1.248), rotate: 0,
  id: 'OR7'
})
// vobd_sense.div.top_res
const OR8 = board.add(R_0603_1608Metric, {
  translate: pt(1.801, 1.151), rotate: 0,
  id: 'OR8'
})
// vobd_sense.div.bottom_res
const OR9 = board.add(R_0603_1608Metric, {
  translate: pt(1.801, 1.248), rotate: 0,
  id: 'OR9'
})

board.setNetlist([
  {name: "Ognd", pads: [["OU1", "5"], ["OU2", "1"], ["OD1", "2"], ["OU3", "9"], ["OU3", "19"], ["OU4", "2"], ["OU4", "8"], ["OR6", "2"], ["OR7", "2"], ["OR9", "2"], ["OC1", "2"], ["OC5", "2"], ["OC6", "2"], ["OJ1", "5"], ["OC8", "2"], ["OR2", "2"], ["OC7", "2"], ["OC3", "2"], ["OC4", "2"]]},
  {name: "Ovobd", pads: [["OFB1", "2"], ["OU2", "3"], ["OR8", "1"], ["OR3", "1"], ["OC1", "1"], ["OC3", "1"]]},
  {name: "Ov3v3", pads: [["OD1", "1"], ["OU3", "1"], ["OU4", "3"], ["OD2", "2"], ["OR1", "1"], ["OU3", "7"], ["OU3", "16"], ["OC5", "1"], ["OC6", "1"], ["OJ1", "1"], ["OC8", "1"], ["OR4", "1"], ["OL1", "2"], ["OC4", "1"]]},
  {name: "Oobd.pwr", pads: [["OU1", "16"], ["OFB1", "1"]]},
  {name: "Ocan.can.canh", pads: [["OU4", "7"], ["OU1", "6"]]},
  {name: "Ocan.can.canl", pads: [["OU4", "6"], ["OU1", "14"]]},
  {name: "Ocan.controller.txd", pads: [["OU4", "1"], ["OU3", "6"]]},
  {name: "Ocan.controller.rxd", pads: [["OU4", "4"], ["OU3", "5"]]},
  {name: "Omcu.program_boot_node", pads: [["OR5", "2"], ["OU3", "8"], ["OJ1", "2"]]},
  {name: "Oledg.signal", pads: [["OU3", "13"], ["OD3", "2"]]},
  {name: "Oledw.signal", pads: [["OU3", "14"], ["OD4", "2"]]},
  {name: "Ovobd_sense.output", pads: [["OU3", "3"], ["OR8", "2"], ["OR9", "1"]]},
  {name: "Oreg_3v3.fb.output", pads: [["OU2", "4"], ["OR1", "2"], ["OR2", "1"]]},
  {name: "Oreg_3v3.boot_cap.neg", pads: [["OC2", "2"], ["OU2", "2"], ["OL1", "1"]]},
  {name: "Oreg_3v3.boot_cap.pos", pads: [["OC2", "1"], ["OU2", "6"]]},
  {name: "Oreg_3v3.en_res.b", pads: [["OR3", "2"], ["OU2", "5"]]},
  {name: "Omcu.program_uart_node.a_tx", pads: [["OU3", "12"], ["OJ1", "3"]]},
  {name: "Omcu.program_uart_node.b_tx", pads: [["OU3", "11"], ["OJ1", "4"]]},
  {name: "Omcu.program_en_node", pads: [["OU3", "2"], ["OJ1", "6"], ["OR4", "2"], ["OC7", "1"]]},
  {name: "Oledr.res.a", pads: [["OR5", "1"], ["OD2", "1"]]},
  {name: "Oledg.res.a", pads: [["OR6", "1"], ["OD3", "1"]]},
  {name: "Oledw.res.a", pads: [["OR7", "1"], ["OD4", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.9769685039370084, 1.8905511811023625);
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


