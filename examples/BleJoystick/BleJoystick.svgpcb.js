const board = new PCB();

// jlc_th.th1
const JH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.700, 1.547), rotate: 0,
  id: 'JH1'
})
// jlc_th.th2
const JH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.739, 1.547), rotate: 0,
  id: 'JH2'
})
// jlc_th.th3
const JH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.700, 1.587), rotate: 0,
  id: 'JH3'
})
// bat.conn
const JJ1 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.634, 1.252), rotate: 0,
  id: 'JJ1'
})
// usb.conn
const JJ2 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.804, 0.165), rotate: 0,
  id: 'JJ2'
})
// usb.cc_pull.cc1.res
const JR1 = board.add(R_0603_1608Metric, {
  translate: pt(1.653, 0.420), rotate: 0,
  id: 'JR1'
})
// usb.cc_pull.cc2.res
const JR2 = board.add(R_0603_1608Metric, {
  translate: pt(1.809, 0.420), rotate: 0,
  id: 'JR2'
})
// tp_bat.tp
const JTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.770, 1.585), rotate: 0,
  id: 'JTP1'
})
// tp_gnd.tp
const JTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.020, 1.585), rotate: 0,
  id: 'JTP2'
})
// gate.pull_res
const JR3 = board.add(R_0603_1608Metric, {
  translate: pt(1.984, 0.769), rotate: 0,
  id: 'JR3'
})
// gate.pwr_fet
const JQ1 = board.add(SOT_23, {
  translate: pt(1.670, 0.633), rotate: 0,
  id: 'JQ1'
})
// gate.amp_res
const JR4 = board.add(R_0603_1608Metric, {
  translate: pt(1.653, 0.883), rotate: 0,
  id: 'JR4'
})
// gate.amp_fet
const JQ2 = board.add(SOT_23, {
  translate: pt(1.861, 0.633), rotate: 0,
  id: 'JQ2'
})
// gate.ctl_diode
const JD1 = board.add(D_SOD_323, {
  translate: pt(1.658, 0.777), rotate: 0,
  id: 'JD1'
})
// gate.btn_diode
const JD2 = board.add(D_SOD_323, {
  translate: pt(1.824, 0.777), rotate: 0,
  id: 'JD2'
})
// reg_3v3.ic
const JU1 = board.add(SOT_89_3, {
  translate: pt(0.537, 1.220), rotate: 0,
  id: 'JU1'
})
// reg_3v3.in_cap.cap
const JC1 = board.add(C_0603_1608Metric, {
  translate: pt(0.483, 1.387), rotate: 0,
  id: 'JC1'
})
// reg_3v3.out_cap.cap
const JC2 = board.add(C_0603_1608Metric, {
  translate: pt(0.639, 1.387), rotate: 0,
  id: 'JC2'
})
// tp_3v3.tp
const JTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.271, 1.585), rotate: 0,
  id: 'JTP3'
})
// prot_3v3.diode
const JD3 = board.add(D_SOD_323, {
  translate: pt(1.519, 1.585), rotate: 0,
  id: 'JD3'
})
// vbat_sense_gate.pre
const JQ3 = board.add(SOT_23, {
  translate: pt(0.076, 1.189), rotate: 0,
  id: 'JQ3'
})
// vbat_sense_gate.pull
const JR5 = board.add(R_0603_1608Metric, {
  translate: pt(0.249, 1.324), rotate: 0,
  id: 'JR5'
})
// vbat_sense_gate.drv
const JQ4 = board.add(SOT_23, {
  translate: pt(0.076, 1.362), rotate: 0,
  id: 'JQ4'
})
// chg.ic
const JU2 = board.add(SOT_23_5, {
  translate: pt(0.896, 1.189), rotate: 0,
  id: 'JU2'
})
// chg.vdd_cap.cap
const JC3 = board.add(C_0805_2012Metric, {
  translate: pt(1.083, 1.161), rotate: 0,
  id: 'JC3'
})
// chg.vbat_cap.cap
const JC4 = board.add(C_0805_2012Metric, {
  translate: pt(0.883, 1.334), rotate: 0,
  id: 'JC4'
})
// chg.prog_res
const JR6 = board.add(R_0603_1608Metric, {
  translate: pt(1.047, 1.324), rotate: 0,
  id: 'JR6'
})
// mcu.ic
const JU3 = board.add(ESP_WROOM_02, {
  translate: pt(0.561, 0.281), rotate: 0,
  id: 'JU3'
})
// mcu.vcc_cap0.cap
const JC5 = board.add(C_0805_2012Metric, {
  translate: pt(1.228, 0.413), rotate: 0,
  id: 'JC5'
})
// mcu.vcc_cap1.cap
const JC6 = board.add(C_0603_1608Metric, {
  translate: pt(1.393, 0.403), rotate: 0,
  id: 'JC6'
})
// mcu.prog.conn
const JJ3 = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(1.329, 0.167), rotate: 0,
  id: 'JJ3'
})
// mcu.boot.package
const JSW1 = board.add(MembraneSwitch_4mm, {
  translate: pt(1.473, 0.491), rotate: 0,
  id: 'JSW1'
})
// mcu.en_pull.rc.r
const JR7 = board.add(R_0603_1608Metric, {
  translate: pt(1.220, 0.519), rotate: 0,
  id: 'JR7'
})
// mcu.en_pull.rc.c
const JC7 = board.add(C_0603_1608Metric, {
  translate: pt(1.376, 0.519), rotate: 0,
  id: 'JC7'
})
// stick
const JU4 = board.add(Joystick_XboxElite2, {
  translate: pt(2.211, 1.547), rotate: 0,
  id: 'JU4'
})
// ax1_div.div.top_res
const JR8 = board.add(R_0603_1608Metric, {
  translate: pt(2.221, 1.151), rotate: 0,
  id: 'JR8'
})
// ax1_div.div.bottom_res
const JR9 = board.add(R_0603_1608Metric, {
  translate: pt(2.221, 1.248), rotate: 0,
  id: 'JR9'
})
// ax2_div.div.top_res
const JR10 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.576), rotate: 0,
  id: 'JR10'
})
// ax2_div.div.bottom_res
const JR11 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.673), rotate: 0,
  id: 'JR11'
})
// trig.ic
const JU5 = board.add(SOT_23, {
  translate: pt(1.344, 1.189), rotate: 0,
  id: 'JU5'
})
// trig.cbyp.cap
const JC8 = board.add(C_0603_1608Metric, {
  translate: pt(1.327, 1.324), rotate: 0,
  id: 'JC8'
})
// trig_div.div.top_res
const JR12 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 1.576), rotate: 0,
  id: 'JR12'
})
// trig_div.div.bottom_res
const JR13 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 1.673), rotate: 0,
  id: 'JR13'
})
// sw[0].package
const JSW2 = board.add(MembraneSwitch_4mm, {
  translate: pt(1.857, 1.547), rotate: 0,
  id: 'JSW2'
})
// sw[1].package
const JSW3 = board.add(MembraneSwitch_4mm, {
  translate: pt(1.975, 1.547), rotate: 0,
  id: 'JSW3'
})
// sw[2].package
const JSW4 = board.add(MembraneSwitch_4mm, {
  translate: pt(2.093, 1.547), rotate: 0,
  id: 'JSW4'
})
// ledr.package
const JD4 = board.add(LED_0603_1608Metric, {
  translate: pt(1.986, 1.151), rotate: 0,
  id: 'JD4'
})
// ledr.res
const JR14 = board.add(R_0603_1608Metric, {
  translate: pt(1.986, 1.248), rotate: 0,
  id: 'JR14'
})
// vbat_sense.div.top_res
const JR15 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 1.576), rotate: 0,
  id: 'JR15'
})
// vbat_sense.div.bottom_res
const JR16 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 1.673), rotate: 0,
  id: 'JR16'
})

board.setNetlist([
  {name: "Jvbat", pads: [["JJ1", "2"], ["JTP1", "1"], ["JR3", "1"], ["JQ1", "2"], ["JR5", "1"], ["JQ4", "2"], ["JU2", "3"], ["JC4", "1"]]},
  {name: "Jgnd", pads: [["JU4", "2"], ["JU4", "3"], ["JU4", "8"], ["JJ1", "1"], ["JJ2", "A1"], ["JJ2", "B12"], ["JJ2", "B1"], ["JJ2", "A12"], ["JTP2", "1"], ["JR4", "1"], ["JQ2", "2"], ["JU1", "1"], ["JD3", "2"], ["JQ3", "2"], ["JU2", "2"], ["JU3", "9"], ["JU3", "19"], ["JU5", "3"], ["JSW2", "2"], ["JSW3", "2"], ["JSW4", "2"], ["JR9", "2"], ["JR11", "2"], ["JR13", "2"], ["JR16", "2"], ["JJ2", "S1"], ["JR6", "2"], ["JC1", "2"], ["JC2", "2"], ["JC3", "2"], ["JC4", "2"], ["JC5", "2"], ["JC6", "2"], ["JJ3", "5"], ["JSW1", "2"], ["JC8", "2"], ["JC7", "2"], ["JR1", "1"], ["JR2", "1"]]},
  {name: "Jv3v3", pads: [["JU4", "5"], ["JU4", "6"], ["JU1", "3"], ["JTP3", "1"], ["JD3", "1"], ["JU3", "1"], ["JU5", "1"], ["JD4", "2"], ["JC2", "1"], ["JU3", "7"], ["JU3", "16"], ["JC5", "1"], ["JC6", "1"], ["JJ3", "1"], ["JC8", "1"], ["JR7", "1"]]},
  {name: "Jgate.pwr_out", pads: [["JQ1", "3"], ["JU1", "2"], ["JC1", "1"]]},
  {name: "Jusb.pwr", pads: [["JJ2", "A4"], ["JJ2", "B9"], ["JJ2", "B4"], ["JJ2", "A9"], ["JU2", "4"], ["JC3", "1"]]},
  {name: "Jstick.ax1", pads: [["JU4", "4"], ["JR8", "1"]]},
  {name: "Jax1_div.output", pads: [["JU3", "3"], ["JR8", "2"], ["JR9", "1"]]},
  {name: "Jstick.ax2", pads: [["JU4", "7"], ["JR10", "1"]]},
  {name: "Jax2_div.output", pads: [["JU3", "15"], ["JR10", "2"], ["JR11", "1"]]},
  {name: "Jstick.sw", pads: [["JU4", "1"], ["JD2", "1"], ["JD1", "1"]]},
  {name: "Jgate.btn_out", pads: [["JU3", "4"], ["JD2", "2"]]},
  {name: "Jgate.control", pads: [["JU3", "5"], ["JR4", "2"], ["JQ2", "1"]]},
  {name: "Jtrig.out", pads: [["JU5", "2"], ["JR12", "1"]]},
  {name: "Jtrig_div.output", pads: [["JU3", "17"], ["JR12", "2"], ["JR13", "1"]]},
  {name: "Jsw[0].out", pads: [["JU3", "10"], ["JSW2", "1"]]},
  {name: "Jsw[1].out", pads: [["JU3", "13"], ["JSW3", "1"]]},
  {name: "Jsw[2].out", pads: [["JU3", "6"], ["JSW4", "1"]]},
  {name: "Jmcu.program_boot_node", pads: [["JR14", "2"], ["JU3", "8"], ["JSW1", "1"], ["JJ3", "2"]]},
  {name: "Jvbat_sense_gate.control", pads: [["JU3", "14"], ["JQ3", "1"]]},
  {name: "Jvbat_sense_gate.output", pads: [["JQ4", "3"], ["JR15", "1"]]},
  {name: "Jvbat_sense.output", pads: [["JU3", "18"], ["JR15", "2"], ["JR16", "1"]]},
  {name: "Jusb.usb.dp", pads: [["JJ2", "A6"], ["JJ2", "B6"]]},
  {name: "Jusb.usb.dm", pads: [["JJ2", "A7"], ["JJ2", "B7"]]},
  {name: "Jusb.conn.cc.cc1", pads: [["JJ2", "A5"], ["JR1", "2"]]},
  {name: "Jusb.conn.cc.cc2", pads: [["JJ2", "B5"], ["JR2", "2"]]},
  {name: "Jgate.pull_res.b", pads: [["JR3", "2"], ["JD1", "2"], ["JQ1", "1"], ["JQ2", "3"]]},
  {name: "Jvbat_sense_gate.pre.drain", pads: [["JQ3", "3"], ["JR5", "2"], ["JQ4", "1"]]},
  {name: "Jchg.stat", pads: [["JU2", "1"]]},
  {name: "Jchg.prog_res.a", pads: [["JR6", "1"], ["JU2", "5"]]},
  {name: "Jmcu.program_uart_node.a_tx", pads: [["JU3", "12"], ["JJ3", "3"]]},
  {name: "Jmcu.program_uart_node.b_tx", pads: [["JU3", "11"], ["JJ3", "4"]]},
  {name: "Jmcu.program_en_node", pads: [["JU3", "2"], ["JJ3", "6"], ["JR7", "2"], ["JC7", "1"]]},
  {name: "Jledr.res.a", pads: [["JR14", "1"], ["JD4", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.3970472440944883, 1.8196850393700787);
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


