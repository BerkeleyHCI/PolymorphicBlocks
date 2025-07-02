const board = new PCB();

// jlc_th.th1
const RH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.230, 1.981), rotate: 0,
  id: 'RH1'
})
// jlc_th.th2
const RH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.270, 1.981), rotate: 0,
  id: 'RH2'
})
// jlc_th.th3
const RH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.230, 2.020), rotate: 0,
  id: 'RH3'
})
// pwr.conn
const RJ1 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.652, 1.775), rotate: 0,
  id: 'RJ1'
})
// pwr_out.conn
const RJ2 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.042, 1.775), rotate: 0,
  id: 'RJ2'
})
// tp_gnd.tp
const RTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 2.019), rotate: 0,
  id: 'RTP1'
})
// fuse.fuse
const RF1 = board.add(Fuseholder_Littelfuse_Nano2_154x, {
  translate: pt(0.219, 1.754), rotate: 0,
  id: 'RF1'
})
// ferrite.fb
const RFB1 = board.add(L_0603_1608Metric, {
  translate: pt(1.054, 2.010), rotate: 0,
  id: 'RFB1'
})
// tp_vin.tp
const RTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 2.019), rotate: 0,
  id: 'RTP2'
})
// reg_3v3.ic
const RU1 = board.add(SOT_23_6, {
  translate: pt(0.301, 1.189), rotate: 0,
  id: 'RU1'
})
// reg_3v3.fb.div.top_res
const RR1 = board.add(R_0603_1608Metric, {
  translate: pt(0.452, 1.368), rotate: 0,
  id: 'RR1'
})
// reg_3v3.fb.div.bottom_res
const RR2 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.498), rotate: 0,
  id: 'RR2'
})
// reg_3v3.hf_in_cap.cap
const RC1 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.498), rotate: 0,
  id: 'RC1'
})
// reg_3v3.boot_cap
const RC2 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 1.498), rotate: 0,
  id: 'RC2'
})
// reg_3v3.power_path.inductor
const RL1 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(0.091, 1.211), rotate: 0,
  id: 'RL1'
})
// reg_3v3.power_path.in_cap.cap.c[0]
const RC3 = board.add(C_1206_3216Metric, {
  translate: pt(0.512, 1.167), rotate: 0,
  id: 'RC3'
})
// reg_3v3.power_path.in_cap.cap.c[1]
const RC4 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 1.385), rotate: 0,
  id: 'RC4'
})
// reg_3v3.power_path.out_cap.cap
const RC5 = board.add(C_0805_2012Metric, {
  translate: pt(0.287, 1.378), rotate: 0,
  id: 'RC5'
})
// reg_3v3.en_res
const RR3 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 1.498), rotate: 0,
  id: 'RR3'
})
// tp_3v3.tp
const RTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.567, 2.019), rotate: 0,
  id: 'RTP3'
})
// prot_3v3.diode
const RD1 = board.add(D_SOD_323, {
  translate: pt(0.815, 2.019), rotate: 0,
  id: 'RD1'
})
// mcu.ic
const RU2 = board.add(ESP_WROOM_02, {
  translate: pt(0.561, 0.281), rotate: 0,
  id: 'RU2'
})
// mcu.vcc_cap0.cap
const RC6 = board.add(C_0805_2012Metric, {
  translate: pt(1.228, 0.413), rotate: 0,
  id: 'RC6'
})
// mcu.vcc_cap1.cap
const RC7 = board.add(C_0603_1608Metric, {
  translate: pt(1.393, 0.403), rotate: 0,
  id: 'RC7'
})
// mcu.prog.conn
const RJ3 = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(1.329, 0.167), rotate: 0,
  id: 'RJ3'
})
// mcu.en_pull.rc.r
const RR4 = board.add(R_0603_1608Metric, {
  translate: pt(1.220, 0.519), rotate: 0,
  id: 'RR4'
})
// mcu.en_pull.rc.c
const RC8 = board.add(C_0603_1608Metric, {
  translate: pt(1.376, 0.519), rotate: 0,
  id: 'RC8'
})
// ledr.package
const RD2 = board.add(LED_0603_1608Metric, {
  translate: pt(2.056, 1.674), rotate: 0,
  id: 'RD2'
})
// ledr.res
const RR5 = board.add(R_0603_1608Metric, {
  translate: pt(2.056, 1.771), rotate: 0,
  id: 'RR5'
})
// vin_sense.div.top_res
const RR6 = board.add(R_0603_1608Metric, {
  translate: pt(2.291, 1.674), rotate: 0,
  id: 'RR6'
})
// vin_sense.div.bottom_res
const RR7 = board.add(R_0603_1608Metric, {
  translate: pt(2.291, 1.770), rotate: 0,
  id: 'RR7'
})
// enca.ic
const RU3 = board.add(SOT_23, {
  translate: pt(1.711, 1.189), rotate: 0,
  id: 'RU3'
})
// enca.cin.cap
const RC9 = board.add(C_0603_1608Metric, {
  translate: pt(1.694, 1.324), rotate: 0,
  id: 'RC9'
})
// encb.ic
const RU4 = board.add(SOT_23, {
  translate: pt(1.980, 1.189), rotate: 0,
  id: 'RU4'
})
// encb.cin.cap
const RC10 = board.add(C_0603_1608Metric, {
  translate: pt(1.963, 1.324), rotate: 0,
  id: 'RC10'
})
// i2c_pull.scl_res.res
const RR8 = board.add(R_0603_1608Metric, {
  translate: pt(2.525, 1.674), rotate: 0,
  id: 'RR8'
})
// i2c_pull.sda_res.res
const RR9 = board.add(R_0603_1608Metric, {
  translate: pt(2.525, 1.770), rotate: 0,
  id: 'RR9'
})
// i2c_tp.tp_scl.tp
const RTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.402, 1.682), rotate: 0,
  id: 'RTP4'
})
// i2c_tp.tp_sda.tp
const RTP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.402, 1.796), rotate: 0,
  id: 'RTP5'
})
// als.ic
const RU5 = board.add(HVSOF6, {
  translate: pt(1.655, 1.686), rotate: 0,
  id: 'RU5'
})
// als.vcc_cap.cap
const RC11 = board.add(C_0603_1608Metric, {
  translate: pt(1.821, 1.674), rotate: 0,
  id: 'RC11'
})
// als.dvi_res
const RR10 = board.add(R_0603_1608Metric, {
  translate: pt(1.644, 1.796), rotate: 0,
  id: 'RR10'
})
// als.dvi_cap
const RC12 = board.add(C_0603_1608Metric, {
  translate: pt(1.800, 1.796), rotate: 0,
  id: 'RC12'
})
// sw.package
const RSW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.341, 1.234), rotate: 0,
  id: 'RSW1'
})
// qwiic.conn
const RJ4 = board.add(JST_SH_SM04B_SRSS_TB_1x04_1MP_P1_00mm_Horizontal, {
  translate: pt(0.874, 1.251), rotate: 0,
  id: 'RJ4'
})
// motor.conn
const RJ5 = board.add(Molex_PicoBlade_53398_0271_1x02_1MP_P1_25mm_Vertical, {
  translate: pt(1.331, 1.260), rotate: 0,
  id: 'RJ5'
})
// drv.ic
const RU6 = board.add(HSOP_8_1EP_3_9x4_9mm_P1_27mm_EP2_41x3_1mm, {
  translate: pt(1.740, 0.492), rotate: 0,
  id: 'RU6'
})
// drv.vm_cap0.cap
const RC13 = board.add(C_0603_1608Metric, {
  translate: pt(2.202, 0.415), rotate: 0,
  id: 'RC13'
})
// drv.vm_cap1.cap
const RC14 = board.add(CP_Elec_8x10, {
  translate: pt(1.811, 0.173), rotate: 0,
  id: 'RC14'
})
// drv.isen_res.res
const RR11 = board.add(R_1206_3216Metric, {
  translate: pt(2.015, 0.430), rotate: 0,
  id: 'RR11'
})

board.setNetlist([
  {name: "Rvin_raw", pads: [["RJ1", "2"], ["RJ2", "2"], ["RF1", "1"]]},
  {name: "Rgnd", pads: [["RJ1", "1"], ["RJ2", "1"], ["RTP1", "1"], ["RU1", "1"], ["RD1", "2"], ["RU2", "9"], ["RU2", "19"], ["RU3", "2"], ["RU4", "2"], ["RU5", "2"], ["RU5", "3"], ["RSW1", "2"], ["RJ4", "1"], ["RU6", "1"], ["RU6", "9"], ["RR7", "2"], ["RC12", "2"], ["RC1", "2"], ["RC6", "2"], ["RC7", "2"], ["RJ3", "5"], ["RC9", "2"], ["RC10", "2"], ["RC11", "2"], ["RC13", "2"], ["RC14", "2"], ["RR2", "2"], ["RC8", "2"], ["RR11", "1"], ["RC5", "2"], ["RC3", "2"], ["RC4", "2"]]},
  {name: "Rvin", pads: [["RFB1", "2"], ["RTP2", "1"], ["RU1", "3"], ["RU6", "5"], ["RR6", "1"], ["RR3", "1"], ["RC1", "1"], ["RC13", "1"], ["RC14", "1"], ["RC3", "1"], ["RC4", "1"]]},
  {name: "Rv3v3", pads: [["RU6", "4"], ["RTP3", "1"], ["RD1", "1"], ["RU2", "1"], ["RD2", "2"], ["RU3", "1"], ["RU4", "1"], ["RU5", "1"], ["RJ4", "2"], ["RR1", "1"], ["RU2", "7"], ["RU2", "16"], ["RR10", "1"], ["RC6", "1"], ["RC7", "1"], ["RJ3", "1"], ["RC9", "1"], ["RC10", "1"], ["RR8", "1"], ["RR9", "1"], ["RC11", "1"], ["RR4", "1"], ["RL1", "2"], ["RC5", "1"]]},
  {name: "Rfuse.pwr_out", pads: [["RF1", "2"], ["RFB1", "1"]]},
  {name: "Rmcu.program_boot_node", pads: [["RR5", "2"], ["RU2", "8"], ["RJ3", "2"]]},
  {name: "Rvin_sense.output", pads: [["RU2", "4"], ["RR6", "2"], ["RR7", "1"]]},
  {name: "Renca.out", pads: [["RU3", "3"], ["RU2", "13"]]},
  {name: "Rencb.out", pads: [["RU4", "3"], ["RU2", "10"]]},
  {name: "Ri2c_chain_0.scl", pads: [["RU2", "6"], ["RU5", "6"], ["RR8", "2"], ["RTP4", "1"], ["RJ4", "4"]]},
  {name: "Ri2c_chain_0.sda", pads: [["RU2", "5"], ["RU5", "4"], ["RJ4", "3"], ["RR9", "2"], ["RTP5", "1"]]},
  {name: "Rsw.out", pads: [["RU2", "3"], ["RSW1", "1"]]},
  {name: "Rdrv.in1", pads: [["RU2", "14"], ["RU6", "3"]]},
  {name: "Rdrv.in2", pads: [["RU2", "15"], ["RU6", "2"]]},
  {name: "Rdrv.out1", pads: [["RU6", "6"], ["RJ5", "1"]]},
  {name: "Rdrv.out2", pads: [["RU6", "8"], ["RJ5", "2"]]},
  {name: "Rreg_3v3.fb.output", pads: [["RU1", "4"], ["RR1", "2"], ["RR2", "1"]]},
  {name: "Rreg_3v3.boot_cap.neg", pads: [["RC2", "2"], ["RU1", "2"], ["RL1", "1"]]},
  {name: "Rreg_3v3.boot_cap.pos", pads: [["RC2", "1"], ["RU1", "6"]]},
  {name: "Rreg_3v3.en_res.b", pads: [["RR3", "2"], ["RU1", "5"]]},
  {name: "Rmcu.program_uart_node.a_tx", pads: [["RU2", "12"], ["RJ3", "3"]]},
  {name: "Rmcu.program_uart_node.b_tx", pads: [["RU2", "11"], ["RJ3", "4"]]},
  {name: "Rmcu.program_en_node", pads: [["RU2", "2"], ["RJ3", "6"], ["RR4", "2"], ["RC8", "1"]]},
  {name: "Rledr.res.a", pads: [["RR5", "1"], ["RD2", "1"]]},
  {name: "Rals.dvi_res.b", pads: [["RR10", "2"], ["RU5", "5"], ["RC12", "1"]]},
  {name: "Rdrv.ic.isen", pads: [["RU6", "7"], ["RR11", "2"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.7017716535433074, 2.174015748031496);
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


