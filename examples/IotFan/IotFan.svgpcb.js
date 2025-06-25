const board = new PCB();

// jlc_th.th1
const FH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.751, 1.742), rotate: 0,
  id: 'FH1'
})
// jlc_th.th2
const FH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.791, 1.742), rotate: 0,
  id: 'FH2'
})
// jlc_th.th3
const FH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.751, 1.781), rotate: 0,
  id: 'FH3'
})
// pwr
const FJ1 = board.add(BarrelJack_CUI_PJ_036AH_SMT_Horizontal, {
  translate: pt(1.256, 0.413), rotate: 0,
  id: 'FJ1'
})
// tp_pwr.tp
const FTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 1.779), rotate: 0,
  id: 'FTP1'
})
// tp_gnd.tp
const FTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 1.779), rotate: 0,
  id: 'FTP2'
})
// reg_5v.ic
const FU1 = board.add(SOT_23_6, {
  translate: pt(0.301, 0.874), rotate: 0,
  id: 'FU1'
})
// reg_5v.fb.div.top_res
const FR1 = board.add(R_0603_1608Metric, {
  translate: pt(0.452, 1.053), rotate: 0,
  id: 'FR1'
})
// reg_5v.fb.div.bottom_res
const FR2 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.183), rotate: 0,
  id: 'FR2'
})
// reg_5v.hf_in_cap.cap
const FC1 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.183), rotate: 0,
  id: 'FC1'
})
// reg_5v.boot_cap
const FC2 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 1.183), rotate: 0,
  id: 'FC2'
})
// reg_5v.power_path.inductor
const FL1 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(0.091, 0.896), rotate: 0,
  id: 'FL1'
})
// reg_5v.power_path.in_cap.cap
const FC3 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 1.070), rotate: 0,
  id: 'FC3'
})
// reg_5v.power_path.out_cap.cap
const FC4 = board.add(C_0805_2012Metric, {
  translate: pt(0.287, 1.063), rotate: 0,
  id: 'FC4'
})
// reg_5v.en_res
const FR3 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.280), rotate: 0,
  id: 'FR3'
})
// tp_5v.tp
const FTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.567, 1.779), rotate: 0,
  id: 'FTP3'
})
// prot_5v.diode
const FD1 = board.add(D_SOD_323, {
  translate: pt(2.519, 1.464), rotate: 0,
  id: 'FD1'
})
// reg_3v3.ic
const FU2 = board.add(SOT_89_3, {
  translate: pt(2.260, 0.906), rotate: 0,
  id: 'FU2'
})
// reg_3v3.in_cap.cap
const FC5 = board.add(C_0603_1608Metric, {
  translate: pt(2.206, 1.072), rotate: 0,
  id: 'FC5'
})
// reg_3v3.out_cap.cap
const FC6 = board.add(C_0603_1608Metric, {
  translate: pt(2.362, 1.072), rotate: 0,
  id: 'FC6'
})
// tp_3v3.tp
const FTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.271, 1.464), rotate: 0,
  id: 'FTP4'
})
// prot_3v3.diode
const FD2 = board.add(D_SOD_323, {
  translate: pt(2.024, 1.464), rotate: 0,
  id: 'FD2'
})
// mcu.ic
const FU3 = board.add(QFN_32_1EP_5x5mm_P0_5mm_EP3_65x3_65mm, {
  translate: pt(1.768, 0.122), rotate: 0,
  id: 'FU3'
})
// mcu.vdd_bulk_cap.cap
const FC7 = board.add(C_0805_2012Metric, {
  translate: pt(1.932, 0.322), rotate: 0,
  id: 'FC7'
})
// mcu.vdda_cap0.cap
const FC8 = board.add(C_0603_1608Metric, {
  translate: pt(2.096, 0.312), rotate: 0,
  id: 'FC8'
})
// mcu.vdda_cap1.cap
const FC9 = board.add(C_0603_1608Metric, {
  translate: pt(2.252, 0.312), rotate: 0,
  id: 'FC9'
})
// mcu.vddrtc_cap.cap
const FC10 = board.add(C_0603_1608Metric, {
  translate: pt(2.408, 0.312), rotate: 0,
  id: 'FC10'
})
// mcu.vddcpu_cap.cap
const FC11 = board.add(C_0603_1608Metric, {
  translate: pt(1.704, 0.441), rotate: 0,
  id: 'FC11'
})
// mcu.vddspi_cap.cap
const FC12 = board.add(C_0603_1608Metric, {
  translate: pt(1.860, 0.441), rotate: 0,
  id: 'FC12'
})
// mcu.ant
const FANT1 = board.add(D_1206_3216Metric, {
  translate: pt(1.736, 0.328), rotate: 0,
  id: 'FANT1'
})
// mcu.pi.c1
const FC13 = board.add(C_0603_1608Metric, {
  translate: pt(2.016, 0.441), rotate: 0,
  id: 'FC13'
})
// mcu.pi.c2
const FC14 = board.add(C_0603_1608Metric, {
  translate: pt(2.172, 0.441), rotate: 0,
  id: 'FC14'
})
// mcu.pi.l
const FL2 = board.add(L_0603_1608Metric, {
  translate: pt(2.328, 0.441), rotate: 0,
  id: 'FL2'
})
// mcu.vdd3p3_l_cap.cap
const FC15 = board.add(C_0603_1608Metric, {
  translate: pt(1.704, 0.538), rotate: 0,
  id: 'FC15'
})
// mcu.vdd3p3_cap.cap
const FC16 = board.add(C_0603_1608Metric, {
  translate: pt(1.860, 0.538), rotate: 0,
  id: 'FC16'
})
// mcu.vdd3p3_l.ind
const FL3 = board.add(L_0603_1608Metric, {
  translate: pt(2.016, 0.538), rotate: 0,
  id: 'FL3'
})
// mcu.crystal.package
const FX1 = board.add(Crystal_SMD_2520_4Pin_2_5x2_0mm, {
  translate: pt(2.311, 0.059), rotate: 0,
  id: 'FX1'
})
// mcu.crystal.cap_a
const FC17 = board.add(C_0603_1608Metric, {
  translate: pt(2.172, 0.538), rotate: 0,
  id: 'FC17'
})
// mcu.crystal.cap_b
const FC18 = board.add(C_0603_1608Metric, {
  translate: pt(2.328, 0.538), rotate: 0,
  id: 'FC18'
})
// mcu.prog.conn
const FJ2 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(2.067, 0.079), rotate: 0,
  id: 'FJ2'
})
// mcu.en_pull.rc.r
const FR4 = board.add(R_0603_1608Metric, {
  translate: pt(1.704, 0.635), rotate: 0,
  id: 'FR4'
})
// mcu.en_pull.rc.c
const FC19 = board.add(C_0603_1608Metric, {
  translate: pt(1.860, 0.635), rotate: 0,
  id: 'FC19'
})
// ledr.package
const FD3 = board.add(LED_0603_1608Metric, {
  translate: pt(1.011, 1.456), rotate: 0,
  id: 'FD3'
})
// ledr.res
const FR5 = board.add(R_0603_1608Metric, {
  translate: pt(1.011, 1.553), rotate: 0,
  id: 'FR5'
})
// enc.package
const FSW1 = board.add(RotaryEncoder_Alps_EC11J15_Switch, {
  translate: pt(0.394, 0.344), rotate: 0,
  id: 'FSW1'
})
// v12_sense.div.top_res
const FR6 = board.add(R_0603_1608Metric, {
  translate: pt(1.246, 1.456), rotate: 0,
  id: 'FR6'
})
// v12_sense.div.bottom_res
const FR7 = board.add(R_0603_1608Metric, {
  translate: pt(1.246, 1.552), rotate: 0,
  id: 'FR7'
})
// rgb_ring.led[0]
const FD4 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.668, 0.846), rotate: 0,
  id: 'FD4'
})
// rgb_ring.led[1]
const FD5 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.786, 0.846), rotate: 0,
  id: 'FD5'
})
// rgb_ring.led[2]
const FD6 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.904, 0.846), rotate: 0,
  id: 'FD6'
})
// rgb_ring.led[3]
const FD7 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.022, 0.846), rotate: 0,
  id: 'FD7'
})
// rgb_ring.led[4]
const FD8 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.140, 0.846), rotate: 0,
  id: 'FD8'
})
// rgb_ring.led[5]
const FD9 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.668, 0.965), rotate: 0,
  id: 'FD9'
})
// rgb_ring.led[6]
const FD10 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.786, 0.965), rotate: 0,
  id: 'FD10'
})
// rgb_ring.led[7]
const FD11 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.904, 0.965), rotate: 0,
  id: 'FD11'
})
// rgb_ring.led[8]
const FD12 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.022, 0.965), rotate: 0,
  id: 'FD12'
})
// rgb_ring.led[9]
const FD13 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.140, 0.965), rotate: 0,
  id: 'FD13'
})
// rgb_ring.led[10]
const FD14 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.668, 1.083), rotate: 0,
  id: 'FD14'
})
// rgb_ring.led[11]
const FD15 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.786, 1.083), rotate: 0,
  id: 'FD15'
})
// rgb_ring.led[12]
const FD16 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.904, 1.083), rotate: 0,
  id: 'FD16'
})
// rgb_ring.led[13]
const FD17 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.022, 1.083), rotate: 0,
  id: 'FD17'
})
// rgb_ring.led[14]
const FD18 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.140, 1.083), rotate: 0,
  id: 'FD18'
})
// rgb_ring.led[15]
const FD19 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.668, 1.201), rotate: 0,
  id: 'FD19'
})
// rgb_ring.led[16]
const FD20 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.786, 1.201), rotate: 0,
  id: 'FD20'
})
// rgb_ring.led[17]
const FD21 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.904, 1.201), rotate: 0,
  id: 'FD21'
})
// fan[0]
const FJ3 = board.add(FanPinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.069, 1.576), rotate: 0,
  id: 'FJ3'
})
// fan_drv[0].pre
const FQ1 = board.add(SOT_23, {
  translate: pt(1.373, 1.126), rotate: 0,
  id: 'FQ1'
})
// fan_drv[0].pull
const FR8 = board.add(R_0603_1608Metric, {
  translate: pt(1.546, 1.088), rotate: 0,
  id: 'FR8'
})
// fan_drv[0].drv
const FQ2 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.443, 0.913), rotate: 0,
  id: 'FQ2'
})
// fan_ctl[0].drv
const FQ3 = board.add(SOT_23, {
  translate: pt(1.498, 1.494), rotate: 0,
  id: 'FQ3'
})
// fan[1]
const FJ4 = board.add(FanPinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.545, 1.576), rotate: 0,
  id: 'FJ4'
})
// fan_drv[1].pre
const FQ4 = board.add(SOT_23, {
  translate: pt(1.798, 1.126), rotate: 0,
  id: 'FQ4'
})
// fan_drv[1].pull
const FR9 = board.add(R_0603_1608Metric, {
  translate: pt(1.972, 1.088), rotate: 0,
  id: 'FR9'
})
// fan_drv[1].drv
const FQ5 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.869, 0.913), rotate: 0,
  id: 'FQ5'
})
// fan_ctl[1].drv
const FQ6 = board.add(SOT_23, {
  translate: pt(1.767, 1.494), rotate: 0,
  id: 'FQ6'
})

board.setNetlist([
  {name: "Fv12", pads: [["FJ1", "1"], ["FTP1", "1"], ["FU1", "3"], ["FR8", "1"], ["FQ2", "1"], ["FQ2", "2"], ["FQ2", "3"], ["FR9", "1"], ["FQ5", "1"], ["FQ5", "2"], ["FQ5", "3"], ["FR6", "1"], ["FR3", "1"], ["FC1", "1"], ["FC3", "1"]]},
  {name: "Fgnd", pads: [["FJ1", "2"], ["FJ3", "1"], ["FJ4", "1"], ["FTP2", "1"], ["FU1", "1"], ["FD1", "2"], ["FU2", "1"], ["FD2", "2"], ["FU3", "33"], ["FSW1", "C"], ["FSW1", "S2"], ["FD4", "4"], ["FD5", "4"], ["FD6", "4"], ["FD7", "4"], ["FD8", "4"], ["FD9", "4"], ["FD10", "4"], ["FD11", "4"], ["FD12", "4"], ["FD13", "4"], ["FD14", "4"], ["FD15", "4"], ["FD16", "4"], ["FD17", "4"], ["FD18", "4"], ["FD19", "4"], ["FD20", "4"], ["FD21", "4"], ["FQ1", "2"], ["FQ3", "2"], ["FQ4", "2"], ["FQ6", "2"], ["FR7", "2"], ["FC1", "2"], ["FC5", "2"], ["FC6", "2"], ["FC7", "2"], ["FC8", "2"], ["FC9", "2"], ["FC10", "2"], ["FC11", "2"], ["FC12", "2"], ["FC15", "2"], ["FC16", "2"], ["FX1", "2"], ["FX1", "4"], ["FJ2", "5"], ["FR2", "2"], ["FC19", "2"], ["FC13", "2"], ["FC14", "2"], ["FC17", "2"], ["FC18", "2"], ["FC3", "2"], ["FC4", "2"]]},
  {name: "Fv5", pads: [["FTP3", "1"], ["FD1", "1"], ["FU2", "2"], ["FD4", "2"], ["FD5", "2"], ["FD6", "2"], ["FD7", "2"], ["FD8", "2"], ["FD9", "2"], ["FD10", "2"], ["FD11", "2"], ["FD12", "2"], ["FD13", "2"], ["FD14", "2"], ["FD15", "2"], ["FD16", "2"], ["FD17", "2"], ["FD18", "2"], ["FD19", "2"], ["FD20", "2"], ["FD21", "2"], ["FR1", "1"], ["FC5", "1"], ["FL1", "2"], ["FC4", "1"]]},
  {name: "Fv3v3", pads: [["FU2", "3"], ["FTP4", "1"], ["FD2", "1"], ["FU3", "31"], ["FU3", "32"], ["FU3", "11"], ["FU3", "17"], ["FU3", "18"], ["FD3", "2"], ["FC6", "1"], ["FU3", "14"], ["FC7", "1"], ["FC8", "1"], ["FC9", "1"], ["FC10", "1"], ["FC11", "1"], ["FC12", "1"], ["FC15", "1"], ["FL3", "1"], ["FJ2", "1"], ["FR4", "1"]]},
  {name: "Fmcu.program_boot_node", pads: [["FR5", "2"], ["FU3", "15"], ["FJ2", "2"]]},
  {name: "Fenc.a", pads: [["FU3", "26"], ["FSW1", "A"]]},
  {name: "Fenc.b", pads: [["FU3", "16"], ["FSW1", "B"]]},
  {name: "Fenc.sw", pads: [["FU3", "25"], ["FSW1", "S1"]]},
  {name: "Fv12_sense.output", pads: [["FU3", "4"], ["FR6", "2"], ["FR7", "1"]]},
  {name: "Frgb_ring.din", pads: [["FU3", "6"], ["FD4", "1"]]},
  {name: "Ffan[0].pwr", pads: [["FJ3", "2"], ["FQ2", "5"], ["FQ2", "6"], ["FQ2", "7"], ["FQ2", "8"]]},
  {name: "Ffan_drv[0].control", pads: [["FU3", "5"], ["FQ1", "1"]]},
  {name: "Ffan[0].sense", pads: [["FJ3", "3"], ["FU3", "9"]]},
  {name: "Ffan_ctl[0].control", pads: [["FU3", "8"], ["FQ3", "1"]]},
  {name: "Ffan_ctl[0].output", pads: [["FJ3", "4"], ["FQ3", "3"]]},
  {name: "Ffan[1].pwr", pads: [["FJ4", "2"], ["FQ5", "5"], ["FQ5", "6"], ["FQ5", "7"], ["FQ5", "8"]]},
  {name: "Ffan_drv[1].control", pads: [["FU3", "10"], ["FQ4", "1"]]},
  {name: "Ffan[1].sense", pads: [["FJ4", "3"], ["FU3", "12"]]},
  {name: "Ffan_ctl[1].control", pads: [["FU3", "13"], ["FQ6", "1"]]},
  {name: "Ffan_ctl[1].output", pads: [["FJ4", "4"], ["FQ6", "3"]]},
  {name: "Freg_5v.fb.output", pads: [["FU1", "4"], ["FR1", "2"], ["FR2", "1"]]},
  {name: "Freg_5v.boot_cap.neg", pads: [["FC2", "2"], ["FU1", "2"], ["FL1", "1"]]},
  {name: "Freg_5v.boot_cap.pos", pads: [["FC2", "1"], ["FU1", "6"]]},
  {name: "Freg_5v.en_res.b", pads: [["FR3", "2"], ["FU1", "5"]]},
  {name: "Fmcu.xtal_node.xi", pads: [["FU3", "30"], ["FX1", "1"], ["FC17", "1"]]},
  {name: "Fmcu.xtal_node.xo", pads: [["FU3", "29"], ["FX1", "3"], ["FC18", "1"]]},
  {name: "Fmcu.program_uart_node.a_tx", pads: [["FU3", "28"], ["FJ2", "3"]]},
  {name: "Fmcu.program_uart_node.b_tx", pads: [["FU3", "27"], ["FJ2", "4"]]},
  {name: "Fmcu.program_en_node", pads: [["FU3", "7"], ["FJ2", "6"], ["FR4", "2"], ["FC19", "1"]]},
  {name: "Fmcu.ic.lna_in", pads: [["FU3", "1"], ["FC13", "1"], ["FL2", "1"]]},
  {name: "Fmcu.pi.output", pads: [["FANT1", "1"], ["FL2", "2"], ["FC14", "1"]]},
  {name: "Fmcu.ic.vdd3p3", pads: [["FU3", "2"], ["FU3", "3"], ["FL3", "2"], ["FC16", "1"]]},
  {name: "Fledr.res.a", pads: [["FR5", "1"], ["FD3", "1"]]},
  {name: "Frgb_ring.led[0].dout", pads: [["FD4", "3"], ["FD5", "1"]]},
  {name: "Frgb_ring.led[1].dout", pads: [["FD5", "3"], ["FD6", "1"]]},
  {name: "Frgb_ring.led[2].dout", pads: [["FD6", "3"], ["FD7", "1"]]},
  {name: "Frgb_ring.led[3].dout", pads: [["FD7", "3"], ["FD8", "1"]]},
  {name: "Frgb_ring.led[4].dout", pads: [["FD8", "3"], ["FD9", "1"]]},
  {name: "Frgb_ring.led[5].dout", pads: [["FD9", "3"], ["FD10", "1"]]},
  {name: "Frgb_ring.led[6].dout", pads: [["FD10", "3"], ["FD11", "1"]]},
  {name: "Frgb_ring.led[7].dout", pads: [["FD11", "3"], ["FD12", "1"]]},
  {name: "Frgb_ring.led[8].dout", pads: [["FD12", "3"], ["FD13", "1"]]},
  {name: "Frgb_ring.led[9].dout", pads: [["FD13", "3"], ["FD14", "1"]]},
  {name: "Frgb_ring.led[10].dout", pads: [["FD14", "3"], ["FD15", "1"]]},
  {name: "Frgb_ring.led[11].dout", pads: [["FD15", "3"], ["FD16", "1"]]},
  {name: "Frgb_ring.led[12].dout", pads: [["FD16", "3"], ["FD17", "1"]]},
  {name: "Frgb_ring.led[13].dout", pads: [["FD17", "3"], ["FD18", "1"]]},
  {name: "Frgb_ring.led[14].dout", pads: [["FD18", "3"], ["FD19", "1"]]},
  {name: "Frgb_ring.led[15].dout", pads: [["FD19", "3"], ["FD20", "1"]]},
  {name: "Frgb_ring.led[16].dout", pads: [["FD20", "3"], ["FD21", "1"]]},
  {name: "Frgb_ring.dout", pads: [["FD21", "3"]]},
  {name: "Ffan_drv[0].pre.drain", pads: [["FQ1", "3"], ["FR8", "2"], ["FQ2", "4"]]},
  {name: "Ffan_drv[1].pre.drain", pads: [["FQ4", "3"], ["FR9", "2"], ["FQ5", "4"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.7001968503937013, 1.9346456692913387);
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


