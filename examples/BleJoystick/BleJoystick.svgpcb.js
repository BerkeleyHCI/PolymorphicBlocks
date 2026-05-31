const board = new PCB();

// jlc_th.th1
const JH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.950, 1.551), rotate: 0,
  id: 'JH1'
})
// jlc_th.th2
const JH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.989, 1.551), rotate: 0,
  id: 'JH2'
})
// jlc_th.th3
const JH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.950, 1.591), rotate: 0,
  id: 'JH3'
})
// bat.conn
const JJ1 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.233, 1.252), rotate: 0,
  id: 'JJ1'
})
// usb.conn
const JJ2 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.804, 0.640), rotate: 0,
  id: 'JJ2'
})
// tp_bat.tp
const JTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.770, 1.589), rotate: 0,
  id: 'JTP1'
})
// tp_usb.tp
const JTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.020, 1.589), rotate: 0,
  id: 'JTP2'
})
// tp_gnd.tp
const JTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.271, 1.589), rotate: 0,
  id: 'JTP3'
})
// mp2722.ic
const JU1 = board.add(MPS_QFN_22_2_5x3_5mm_P0_4mm, {
  translate: pt(1.924, 0.280), rotate: 0,
  id: 'JU1'
})
// mp2722.vbst_cap.cap
const JC1 = board.add(C_0603_1608Metric, {
  translate: pt(1.826, 0.309), rotate: 0,
  id: 'JC1'
})
// mp2722.pmid_cap.cap
const JC2 = board.add(C_0805_2012Metric, {
  translate: pt(1.661, 0.202), rotate: 0,
  id: 'JC2'
})
// mp2722.batt_cap.cap
const JC3 = board.add(C_1206_3216Metric, {
  translate: pt(1.904, 0.045), rotate: 0,
  id: 'JC3'
})
// mp2722.vcc_cap.cap
const JC4 = board.add(C_0805_2012Metric, {
  translate: pt(1.835, 0.202), rotate: 0,
  id: 'JC4'
})
// mp2722.power_path.inductor
const JL1 = board.add(L_1210_3225Metric, {
  translate: pt(1.684, 0.062), rotate: 0,
  id: 'JL1'
})
// mp2722.power_path.in_cap.cap
const JC5 = board.add(C_0805_2012Metric, {
  translate: pt(2.008, 0.202), rotate: 0,
  id: 'JC5'
})
// mp2722.power_path.out_cap.cap
const JC6 = board.add(C_0805_2012Metric, {
  translate: pt(1.661, 0.319), rotate: 0,
  id: 'JC6'
})
// reg_3v3.ic
const JU2 = board.add(SOT_89_3, {
  translate: pt(0.589, 1.220), rotate: 0,
  id: 'JU2'
})
// reg_3v3.in_cap.cap
const JC7 = board.add(C_0603_1608Metric, {
  translate: pt(0.535, 1.387), rotate: 0,
  id: 'JC7'
})
// reg_3v3.out_cap.cap
const JC8 = board.add(C_0603_1608Metric, {
  translate: pt(0.691, 1.387), rotate: 0,
  id: 'JC8'
})
// tp_3v3.tp
const JTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.521, 1.589), rotate: 0,
  id: 'JTP4'
})
// prot_3v3.diode
const JD1 = board.add(D_SOD_323, {
  translate: pt(1.769, 1.589), rotate: 0,
  id: 'JD1'
})
// fake_ntc.div.top_res
const JR1 = board.add(R_0603_1608Metric, {
  translate: pt(1.819, 1.151), rotate: 0,
  id: 'JR1'
})
// fake_ntc.div.bottom_res
const JR2 = board.add(R_0603_1608Metric, {
  translate: pt(1.819, 1.248), rotate: 0,
  id: 'JR2'
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
// mcu.ic.device
const JU3 = board.add(ESP_WROOM_02, {
  translate: pt(0.561, 0.281), rotate: 0,
  id: 'JU3'
})
// mcu.vcc_cap0.cap
const JC9 = board.add(C_0805_2012Metric, {
  translate: pt(1.228, 0.413), rotate: 0,
  id: 'JC9'
})
// mcu.vcc_cap1.cap
const JC10 = board.add(C_0603_1608Metric, {
  translate: pt(1.393, 0.403), rotate: 0,
  id: 'JC10'
})
// mcu.en_pull.rc.r
const JR3 = board.add(R_0603_1608Metric, {
  translate: pt(1.220, 0.519), rotate: 0,
  id: 'JR3'
})
// mcu.en_pull.rc.c
const JC11 = board.add(C_0603_1608Metric, {
  translate: pt(1.376, 0.519), rotate: 0,
  id: 'JC11'
})
// stick.conn.ext
const JJ4 = board.add(Hirose_FH12_6S_0_5SH_1x06_1MP_P0_50mm_Horizontal, {
  translate: pt(0.179, 1.315), rotate: 0,
  id: 'JJ4'
})
// ax1_div.div.top_res
const JR4 = board.add(R_0603_1608Metric, {
  translate: pt(2.054, 1.151), rotate: 0,
  id: 'JR4'
})
// ax1_div.div.bottom_res
const JR5 = board.add(R_0603_1608Metric, {
  translate: pt(2.054, 1.248), rotate: 0,
  id: 'JR5'
})
// ax2_div.div.top_res
const JR6 = board.add(R_0603_1608Metric, {
  translate: pt(2.288, 1.151), rotate: 0,
  id: 'JR6'
})
// ax2_div.div.bottom_res
const JR7 = board.add(R_0603_1608Metric, {
  translate: pt(2.288, 1.248), rotate: 0,
  id: 'JR7'
})
// trig.ic
const JU5 = board.add(SOT_23, {
  translate: pt(0.943, 1.189), rotate: 0,
  id: 'JU5'
})
// trig.cbyp.cap
const JC12 = board.add(C_0603_1608Metric, {
  translate: pt(0.925, 1.324), rotate: 0,
  id: 'JC12'
})
// trig_div.div.top_res
const JR8 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.580), rotate: 0,
  id: 'JR8'
})
// trig_div.div.bottom_res
const JR9 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.677), rotate: 0,
  id: 'JR9'
})
// sw[0].package
const JSW2 = board.add(MembraneSwitch_4mm, {
  translate: pt(2.107, 1.551), rotate: 0,
  id: 'JSW2'
})
// sw[1].package
const JSW3 = board.add(MembraneSwitch_4mm, {
  translate: pt(2.226, 1.551), rotate: 0,
  id: 'JSW3'
})
// sw[2].package
const JSW4 = board.add(MembraneSwitch_4mm, {
  translate: pt(2.344, 1.551), rotate: 0,
  id: 'JSW4'
})
// ledr.package
const JD2 = board.add(LED_0603_1608Metric, {
  translate: pt(1.584, 1.151), rotate: 0,
  id: 'JD2'
})
// ledr.res
const JR10 = board.add(R_0603_1608Metric, {
  translate: pt(1.584, 1.248), rotate: 0,
  id: 'JR10'
})
// vbat_sense.div.top_res
const JR11 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 1.580), rotate: 0,
  id: 'JR11'
})
// vbat_sense.div.bottom_res
const JR12 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 1.677), rotate: 0,
  id: 'JR12'
})
// i2c_pull.scl_res.res
const JR13 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 1.580), rotate: 0,
  id: 'JR13'
})
// i2c_pull.sda_res.res
const JR14 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 1.677), rotate: 0,
  id: 'JR14'
})

board.setNetlist([
  {name: "Jvbat", pads: [["JJ1", "2"], ["JTP1", "1"], ["JU1", "12"], ["JU1", "14"], ["JC3", "1"], ["JR11", "1"]]},
  {name: "Jvusb", pads: [["JJ2", "A4"], ["JJ2", "A9"], ["JJ2", "B4"], ["JJ2", "B9"], ["JTP2", "1"], ["JU1", "2"], ["JC5", "1"]]},
  {name: "Jgnd", pads: [["JJ1", "1"], ["JJ2", "A1"], ["JJ2", "A12"], ["JJ2", "B1"], ["JJ2", "B12"], ["JJ2", "S1"], ["JTP3", "1"], ["JU1", "18"], ["JU1", "5"], ["JC2", "2"], ["JC3", "2"], ["JC4", "2"], ["JC5", "2"], ["JC6", "2"], ["JU2", "1"], ["JC7", "2"], ["JC8", "2"], ["JD1", "2"], ["JR2", "2"], ["JJ3", "5"], ["JSW1", "2"], ["JU3", "19"], ["JU3", "9"], ["JC9", "2"], ["JC10", "2"], ["JC11", "2"], ["JJ4", "1"], ["JR5", "2"], ["JR7", "2"], ["JU5", "3"], ["JC12", "2"], ["JR9", "2"], ["JSW2", "2"], ["JSW3", "2"], ["JSW4", "2"], ["JR12", "2"]]},
  {name: "Jv3v3", pads: [["JU2", "3"], ["JC8", "1"], ["JTP4", "1"], ["JD1", "1"], ["JJ3", "1"], ["JU3", "1"], ["JU3", "16"], ["JU3", "7"], ["JC9", "1"], ["JC10", "1"], ["JR3", "1"], ["JJ4", "2"], ["JU5", "1"], ["JC12", "1"], ["JD2", "2"], ["JR13", "1"], ["JR14", "1"]]},
  {name: "Jusb.usb.dp", pads: [["JJ2", "A6"], ["JJ2", "B6"]]},
  {name: "Jusb.usb.dm", pads: [["JJ2", "A7"], ["JJ2", "B7"]]},
  {name: "Jusb.cc.cc1", pads: [["JJ2", "A5"], ["JU1", "1"]]},
  {name: "Jusb.cc.cc2", pads: [["JJ2", "B5"], ["JU1", "22"]]},
  {name: "Jmp2722.pwr_out", pads: [["JU1", "13"], ["JL1", "2"], ["JC6", "1"], ["JU2", "2"], ["JC7", "1"]]},
  {name: "Jmp2722.vrntc", pads: [["JU1", "7"], ["JR1", "1"]]},
  {name: "Jmp2722.ntc1", pads: [["JU1", "10"], ["JR1", "2"], ["JR2", "1"]]},
  {name: "Jmp2722.rst", pads: [["JU1", "17"], ["JU3", "5"], ["JJ4", "4"]]},
  {name: "Jmp2722.int", pads: [["JU1", "8"]]},
  {name: "Jmp2722.stat", pads: [["JU1", "11"]]},
  {name: "Jmp2722.pg", pads: [["JU1", "9"]]},
  {name: "Jmp2722.i2c.scl", pads: [["JU1", "16"], ["JU3", "4"], ["JR13", "2"]]},
  {name: "Jmp2722.i2c.sda", pads: [["JU1", "15"], ["JU3", "14"], ["JR14", "2"]]},
  {name: "Jmp2722.usb.dp", pads: [["JU1", "21"]]},
  {name: "Jmp2722.usb.dm", pads: [["JU1", "20"]]},
  {name: "Jmp2722.ic.sw", pads: [["JU1", "4"], ["JC1", "2"], ["JL1", "1"]]},
  {name: "Jmp2722.ic.pmid", pads: [["JU1", "3"], ["JC2", "1"]]},
  {name: "Jmp2722.ic.bst", pads: [["JU1", "6"], ["JC1", "1"]]},
  {name: "Jmp2722.ic.vcc", pads: [["JU1", "19"], ["JC4", "1"]]},
  {name: "Jmcu.program_uart_node.a_tx", pads: [["JJ3", "4"], ["JU3", "11"]]},
  {name: "Jmcu.program_uart_node.b_tx", pads: [["JJ3", "3"], ["JU3", "12"]]},
  {name: "Jmcu.program_en_node", pads: [["JJ3", "6"], ["JU3", "2"], ["JR3", "2"], ["JC11", "1"]]},
  {name: "Jmcu.program_boot_node", pads: [["JJ3", "2"], ["JSW1", "1"], ["JU3", "8"], ["JR10", "2"]]},
  {name: "Jstick.ax1", pads: [["JJ4", "5"], ["JR4", "1"]]},
  {name: "Jstick.ax2", pads: [["JJ4", "6"], ["JR6", "1"]]},
  {name: "Jax1_div.output", pads: [["JU3", "3"], ["JR4", "2"], ["JR5", "1"]]},
  {name: "Jax2_div.output", pads: [["JU3", "15"], ["JR6", "2"], ["JR7", "1"]]},
  {name: "Jtrig.out", pads: [["JU5", "2"], ["JR8", "1"]]},
  {name: "Jtrig_div.output", pads: [["JU3", "17"], ["JR8", "2"], ["JR9", "1"]]},
  {name: "Jsw[0].out", pads: [["JU3", "10"], ["JSW2", "1"]]},
  {name: "Jsw[1].out", pads: [["JU3", "13"], ["JSW3", "1"]]},
  {name: "Jsw[2].out", pads: [["JU3", "6"], ["JSW4", "1"]]},
  {name: "Jledr.package.k", pads: [["JD2", "1"], ["JR10", "1"]]},
  {name: "Jvbat_sense.output", pads: [["JU3", "18"], ["JR11", "2"], ["JR12", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.464763779527559, 1.8236220472440945);
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


