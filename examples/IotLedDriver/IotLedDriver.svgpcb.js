const board = new PCB();

// jlc_th.th1
const LH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.586, 2.406), rotate: 0,
  id: 'LH1'
})
// jlc_th.th2
const LH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.625, 2.406), rotate: 0,
  id: 'LH2'
})
// jlc_th.th3
const LH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.586, 2.446), rotate: 0,
  id: 'LH3'
})
// pwr
const LJ1 = board.add(BarrelJack_CUI_PJ_036AH_SMT_Horizontal, {
  translate: pt(2.735, 1.220), rotate: 0,
  id: 'LJ1'
})
// tp_pwr.tp
const LTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.402, 2.444), rotate: 0,
  id: 'LTP1'
})
// tp_gnd.tp
const LTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.162, 2.444), rotate: 0,
  id: 'LTP2'
})
// reg_5v.ic
const LU1 = board.add(SOT_23_6, {
  translate: pt(1.912, 1.807), rotate: 0,
  id: 'LU1'
})
// reg_5v.fb.div.top_res
const LR1 = board.add(R_0603_1608Metric, {
  translate: pt(2.063, 1.986), rotate: 0,
  id: 'LR1'
})
// reg_5v.fb.div.bottom_res
const LR2 = board.add(R_0603_1608Metric, {
  translate: pt(1.669, 2.116), rotate: 0,
  id: 'LR2'
})
// reg_5v.hf_in_cap.cap
const LC1 = board.add(C_0603_1608Metric, {
  translate: pt(1.825, 2.116), rotate: 0,
  id: 'LC1'
})
// reg_5v.boot_cap
const LC2 = board.add(C_0603_1608Metric, {
  translate: pt(1.981, 2.116), rotate: 0,
  id: 'LC2'
})
// reg_5v.power_path.inductor
const LL1 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(1.702, 1.829), rotate: 0,
  id: 'LL1'
})
// reg_5v.power_path.in_cap.cap
const LC3 = board.add(C_1206_3216Metric, {
  translate: pt(1.702, 2.003), rotate: 0,
  id: 'LC3'
})
// reg_5v.power_path.out_cap.cap
const LC4 = board.add(C_0805_2012Metric, {
  translate: pt(1.898, 1.996), rotate: 0,
  id: 'LC4'
})
// reg_5v.en_res
const LR3 = board.add(R_0603_1608Metric, {
  translate: pt(1.669, 2.213), rotate: 0,
  id: 'LR3'
})
// tp_5v.tp
const LTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.151, 2.444), rotate: 0,
  id: 'LTP3'
})
// prot_5v.diode
const LD1 = board.add(D_SOD_323, {
  translate: pt(1.904, 2.444), rotate: 0,
  id: 'LD1'
})
// reg_3v3.ic
const LU2 = board.add(SOT_223_3_TabPin2, {
  translate: pt(3.082, 1.882), rotate: 0,
  id: 'LU2'
})
// reg_3v3.in_cap.cap
const LC5 = board.add(C_0603_1608Metric, {
  translate: pt(3.140, 2.092), rotate: 0,
  id: 'LC5'
})
// reg_3v3.out_cap.cap
const LC6 = board.add(C_0805_2012Metric, {
  translate: pt(2.976, 2.102), rotate: 0,
  id: 'LC6'
})
// tp_3v3.tp
const LTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.412, 2.444), rotate: 0,
  id: 'LTP4'
})
// prot_3v3.diode
const LD2 = board.add(D_SOD_323, {
  translate: pt(1.660, 2.444), rotate: 0,
  id: 'LD2'
})
// mcu.ic
const LU3 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'LU3'
})
// mcu.vcc_cap0.cap
const LC7 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.242), rotate: 0,
  id: 'LC7'
})
// mcu.vcc_cap1.cap
const LC8 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.226), rotate: 0,
  id: 'LC8'
})
// mcu.prog.conn
const LJ2 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(2.067, 0.079), rotate: 0,
  id: 'LJ2'
})
// mcu.en_pull.rc.r
const LR4 = board.add(R_0603_1608Metric, {
  translate: pt(1.987, 0.356), rotate: 0,
  id: 'LR4'
})
// mcu.en_pull.rc.c
const LC9 = board.add(C_0603_1608Metric, {
  translate: pt(2.143, 0.356), rotate: 0,
  id: 'LC9'
})
// ledr.package
const LD3 = board.add(LED_0603_1608Metric, {
  translate: pt(0.684, 2.435), rotate: 0,
  id: 'LD3'
})
// ledr.res
const LR5 = board.add(R_0603_1608Metric, {
  translate: pt(0.684, 2.532), rotate: 0,
  id: 'LR5'
})
// enc.package
const LSW1 = board.add(RotaryEncoder_Alps_EC11J15_Switch, {
  translate: pt(2.778, 0.344), rotate: 0,
  id: 'LSW1'
})
// v12_sense.div.top_res
const LR6 = board.add(R_0603_1608Metric, {
  translate: pt(0.919, 2.435), rotate: 0,
  id: 'LR6'
})
// v12_sense.div.bottom_res
const LR7 = board.add(R_0603_1608Metric, {
  translate: pt(0.919, 2.532), rotate: 0,
  id: 'LR7'
})
// rgb_ring.led[0]
const LD4 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.279, 1.780), rotate: 0,
  id: 'LD4'
})
// rgb_ring.led[1]
const LD5 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.397, 1.780), rotate: 0,
  id: 'LD5'
})
// rgb_ring.led[2]
const LD6 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.515, 1.780), rotate: 0,
  id: 'LD6'
})
// rgb_ring.led[3]
const LD7 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.633, 1.780), rotate: 0,
  id: 'LD7'
})
// rgb_ring.led[4]
const LD8 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.751, 1.780), rotate: 0,
  id: 'LD8'
})
// rgb_ring.led[5]
const LD9 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.279, 1.898), rotate: 0,
  id: 'LD9'
})
// rgb_ring.led[6]
const LD10 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.397, 1.898), rotate: 0,
  id: 'LD10'
})
// rgb_ring.led[7]
const LD11 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.515, 1.898), rotate: 0,
  id: 'LD11'
})
// rgb_ring.led[8]
const LD12 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.633, 1.898), rotate: 0,
  id: 'LD12'
})
// rgb_ring.led[9]
const LD13 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.751, 1.898), rotate: 0,
  id: 'LD13'
})
// rgb_ring.led[10]
const LD14 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.279, 2.016), rotate: 0,
  id: 'LD14'
})
// rgb_ring.led[11]
const LD15 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.397, 2.016), rotate: 0,
  id: 'LD15'
})
// rgb_ring.led[12]
const LD16 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.515, 2.016), rotate: 0,
  id: 'LD16'
})
// rgb_ring.led[13]
const LD17 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.633, 2.016), rotate: 0,
  id: 'LD17'
})
// rgb_ring.led[14]
const LD18 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.751, 2.016), rotate: 0,
  id: 'LD18'
})
// rgb_ring.led[15]
const LD19 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.279, 2.134), rotate: 0,
  id: 'LD19'
})
// rgb_ring.led[16]
const LD20 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.397, 2.134), rotate: 0,
  id: 'LD20'
})
// rgb_ring.led[17]
const LD21 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.515, 2.134), rotate: 0,
  id: 'LD21'
})
// led_drv[0].ic
const LU4 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(1.197, 2.105), rotate: 0,
  id: 'LU4'
})
// led_drv[0].rsense.res.res
const LR8 = board.add(R_0603_1608Metric, {
  translate: pt(1.298, 2.242), rotate: 0,
  id: 'LR8'
})
// led_drv[0].pwr_cap.cap
const LC10 = board.add(C_0805_2012Metric, {
  translate: pt(1.426, 2.075), rotate: 0,
  id: 'LC10'
})
// led_drv[0].ind
const LL2 = board.add(L_Sunlord_SWPA6045S, {
  translate: pt(1.206, 1.869), rotate: 0,
  id: 'LL2'
})
// led_drv[0].diode
const LD22 = board.add(D_SOD_323, {
  translate: pt(1.137, 2.251), rotate: 0,
  id: 'LD22'
})
// led_drv[1].ic
const LU5 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(3.247, 1.172), rotate: 0,
  id: 'LU5'
})
// led_drv[1].rsense.res.res
const LR9 = board.add(R_0603_1608Metric, {
  translate: pt(3.348, 1.309), rotate: 0,
  id: 'LR9'
})
// led_drv[1].pwr_cap.cap
const LC11 = board.add(C_0805_2012Metric, {
  translate: pt(3.476, 1.142), rotate: 0,
  id: 'LC11'
})
// led_drv[1].ind
const LL3 = board.add(L_Sunlord_SWPA6045S, {
  translate: pt(3.256, 0.935), rotate: 0,
  id: 'LL3'
})
// led_drv[1].diode
const LD23 = board.add(D_SOD_323, {
  translate: pt(3.188, 1.318), rotate: 0,
  id: 'LD23'
})
// led_drv[2].ic
const LU6 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(0.660, 2.105), rotate: 0,
  id: 'LU6'
})
// led_drv[2].rsense.res.res
const LR10 = board.add(R_0603_1608Metric, {
  translate: pt(0.761, 2.242), rotate: 0,
  id: 'LR10'
})
// led_drv[2].pwr_cap.cap
const LC12 = board.add(C_0805_2012Metric, {
  translate: pt(0.889, 2.075), rotate: 0,
  id: 'LC12'
})
// led_drv[2].ind
const LL4 = board.add(L_Sunlord_SWPA6045S, {
  translate: pt(0.669, 1.869), rotate: 0,
  id: 'LL4'
})
// led_drv[2].diode
const LD24 = board.add(D_SOD_323, {
  translate: pt(0.600, 2.251), rotate: 0,
  id: 'LD24'
})
// led_drv[3].ic
const LU7 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(0.123, 2.105), rotate: 0,
  id: 'LU7'
})
// led_drv[3].rsense.res.res
const LR11 = board.add(R_0603_1608Metric, {
  translate: pt(0.224, 2.242), rotate: 0,
  id: 'LR11'
})
// led_drv[3].pwr_cap.cap
const LC13 = board.add(C_0805_2012Metric, {
  translate: pt(0.352, 2.075), rotate: 0,
  id: 'LC13'
})
// led_drv[3].ind
const LL5 = board.add(L_Sunlord_SWPA6045S, {
  translate: pt(0.132, 1.869), rotate: 0,
  id: 'LL5'
})
// led_drv[3].diode
const LD25 = board.add(D_SOD_323, {
  translate: pt(0.063, 2.251), rotate: 0,
  id: 'LD25'
})
// led_conn
const LJ3 = board.add(JST_PH_S2B_PH_K_1x02_P2_00mm_Horizontal, {
  translate: pt(3.470, 2.006), rotate: 0,
  id: 'LJ3'
})
// rgb_conn
const LJ4 = board.add(JST_PH_S6B_PH_K_1x06_P2_00mm_Horizontal, {
  translate: pt(0.096, 2.672), rotate: 0,
  id: 'LJ4'
})

board.setNetlist([
  {name: "Lv12", pads: [["LJ1", "1"], ["LTP1", "1"], ["LU1", "3"], ["LU4", "8"], ["LU5", "8"], ["LU6", "8"], ["LU7", "8"], ["LR6", "1"], ["LR3", "1"], ["LD22", "1"], ["LD23", "1"], ["LD24", "1"], ["LD25", "1"], ["LC1", "1"], ["LC10", "1"], ["LC11", "1"], ["LC12", "1"], ["LC13", "1"], ["LC3", "1"], ["LR8", "1"], ["LR9", "1"], ["LR10", "1"], ["LR11", "1"]]},
  {name: "Lgnd", pads: [["LJ1", "2"], ["LTP2", "1"], ["LU1", "1"], ["LD1", "2"], ["LU2", "1"], ["LD2", "2"], ["LU3", "1"], ["LU3", "40"], ["LU3", "41"], ["LR5", "2"], ["LSW1", "C"], ["LSW1", "S2"], ["LD4", "4"], ["LD5", "4"], ["LD6", "4"], ["LD7", "4"], ["LD8", "4"], ["LD9", "4"], ["LD10", "4"], ["LD11", "4"], ["LD12", "4"], ["LD13", "4"], ["LD14", "4"], ["LD15", "4"], ["LD16", "4"], ["LD17", "4"], ["LD18", "4"], ["LD19", "4"], ["LD20", "4"], ["LD21", "4"], ["LU4", "2"], ["LU4", "3"], ["LU5", "2"], ["LU5", "3"], ["LU6", "2"], ["LU6", "3"], ["LU7", "2"], ["LU7", "3"], ["LR7", "2"], ["LC1", "2"], ["LC5", "2"], ["LC6", "2"], ["LC7", "2"], ["LC8", "2"], ["LJ2", "5"], ["LC10", "2"], ["LC11", "2"], ["LC12", "2"], ["LC13", "2"], ["LR2", "2"], ["LC9", "2"], ["LC3", "2"], ["LC4", "2"]]},
  {name: "Lv5", pads: [["LTP3", "1"], ["LD1", "1"], ["LU2", "3"], ["LD4", "2"], ["LD5", "2"], ["LD6", "2"], ["LD7", "2"], ["LD8", "2"], ["LD9", "2"], ["LD10", "2"], ["LD11", "2"], ["LD12", "2"], ["LD13", "2"], ["LD14", "2"], ["LD15", "2"], ["LD16", "2"], ["LD17", "2"], ["LD18", "2"], ["LD19", "2"], ["LD20", "2"], ["LD21", "2"], ["LR1", "1"], ["LC5", "1"], ["LL1", "2"], ["LC4", "1"]]},
  {name: "Lv3v3", pads: [["LU2", "2"], ["LTP4", "1"], ["LD2", "1"], ["LU3", "2"], ["LC6", "1"], ["LC7", "1"], ["LC8", "1"], ["LJ2", "1"], ["LR4", "1"]]},
  {name: "Lledr.signal", pads: [["LU3", "14"], ["LD3", "2"]]},
  {name: "Lenc.a", pads: [["LU3", "8"], ["LSW1", "A"]]},
  {name: "Lenc.b", pads: [["LU3", "7"], ["LSW1", "B"]]},
  {name: "Lenc.sw", pads: [["LU3", "6"], ["LSW1", "S1"]]},
  {name: "Lv12_sense.output", pads: [["LU3", "4"], ["LR6", "2"], ["LR7", "1"]]},
  {name: "Lrgb_ring.din", pads: [["LU3", "5"], ["LD4", "1"]]},
  {name: "Lled_drv[0].pwm", pads: [["LU3", "39"], ["LU4", "4"]]},
  {name: "Lled_drv[1].pwm", pads: [["LU3", "38"], ["LU5", "4"]]},
  {name: "Lled_drv[2].pwm", pads: [["LU3", "35"], ["LU6", "4"]]},
  {name: "Lled_drv[3].pwm", pads: [["LU3", "33"], ["LU7", "4"]]},
  {name: "Lled_drv[0].leda", pads: [["LJ3", "1"], ["LR8", "2"], ["LU4", "1"]]},
  {name: "Lled_drv[0].ledk", pads: [["LL2", "1"], ["LJ3", "2"]]},
  {name: "Lled_drv[1].leda", pads: [["LJ4", "1"], ["LR9", "2"], ["LU5", "1"]]},
  {name: "Lled_drv[1].ledk", pads: [["LL3", "1"], ["LJ4", "2"]]},
  {name: "Lled_drv[2].leda", pads: [["LJ4", "3"], ["LR10", "2"], ["LU6", "1"]]},
  {name: "Lled_drv[2].ledk", pads: [["LL4", "1"], ["LJ4", "4"]]},
  {name: "Lled_drv[3].leda", pads: [["LJ4", "5"], ["LR11", "2"], ["LU7", "1"]]},
  {name: "Lled_drv[3].ledk", pads: [["LL5", "1"], ["LJ4", "6"]]},
  {name: "Lreg_5v.fb.output", pads: [["LU1", "4"], ["LR1", "2"], ["LR2", "1"]]},
  {name: "Lreg_5v.boot_cap.neg", pads: [["LC2", "2"], ["LU1", "2"], ["LL1", "1"]]},
  {name: "Lreg_5v.boot_cap.pos", pads: [["LC2", "1"], ["LU1", "6"]]},
  {name: "Lreg_5v.en_res.b", pads: [["LR3", "2"], ["LU1", "5"]]},
  {name: "Lmcu.program_uart_node.a_tx", pads: [["LU3", "37"], ["LJ2", "3"]]},
  {name: "Lmcu.program_uart_node.b_tx", pads: [["LU3", "36"], ["LJ2", "4"]]},
  {name: "Lmcu.program_en_node", pads: [["LU3", "3"], ["LJ2", "6"], ["LR4", "2"], ["LC9", "1"]]},
  {name: "Lmcu.program_boot_node", pads: [["LU3", "27"], ["LJ2", "2"]]},
  {name: "Lledr.res.a", pads: [["LR5", "1"], ["LD3", "1"]]},
  {name: "Lrgb_ring.led[0].dout", pads: [["LD4", "3"], ["LD5", "1"]]},
  {name: "Lrgb_ring.led[1].dout", pads: [["LD5", "3"], ["LD6", "1"]]},
  {name: "Lrgb_ring.led[2].dout", pads: [["LD6", "3"], ["LD7", "1"]]},
  {name: "Lrgb_ring.led[3].dout", pads: [["LD7", "3"], ["LD8", "1"]]},
  {name: "Lrgb_ring.led[4].dout", pads: [["LD8", "3"], ["LD9", "1"]]},
  {name: "Lrgb_ring.led[5].dout", pads: [["LD9", "3"], ["LD10", "1"]]},
  {name: "Lrgb_ring.led[6].dout", pads: [["LD10", "3"], ["LD11", "1"]]},
  {name: "Lrgb_ring.led[7].dout", pads: [["LD11", "3"], ["LD12", "1"]]},
  {name: "Lrgb_ring.led[8].dout", pads: [["LD12", "3"], ["LD13", "1"]]},
  {name: "Lrgb_ring.led[9].dout", pads: [["LD13", "3"], ["LD14", "1"]]},
  {name: "Lrgb_ring.led[10].dout", pads: [["LD14", "3"], ["LD15", "1"]]},
  {name: "Lrgb_ring.led[11].dout", pads: [["LD15", "3"], ["LD16", "1"]]},
  {name: "Lrgb_ring.led[12].dout", pads: [["LD16", "3"], ["LD17", "1"]]},
  {name: "Lrgb_ring.led[13].dout", pads: [["LD17", "3"], ["LD18", "1"]]},
  {name: "Lrgb_ring.led[14].dout", pads: [["LD18", "3"], ["LD19", "1"]]},
  {name: "Lrgb_ring.led[15].dout", pads: [["LD19", "3"], ["LD20", "1"]]},
  {name: "Lrgb_ring.led[16].dout", pads: [["LD20", "3"], ["LD21", "1"]]},
  {name: "Lrgb_ring.dout", pads: [["LD21", "3"]]},
  {name: "Lled_drv[0].ind.b", pads: [["LL2", "2"], ["LU4", "5"], ["LU4", "6"], ["LD22", "2"]]},
  {name: "Lled_drv[1].ind.b", pads: [["LL3", "2"], ["LU5", "5"], ["LU5", "6"], ["LD23", "2"]]},
  {name: "Lled_drv[2].ind.b", pads: [["LL4", "2"], ["LU6", "5"], ["LU6", "6"], ["LD24", "2"]]},
  {name: "Lled_drv[3].ind.b", pads: [["LL5", "2"], ["LU7", "5"], ["LU7", "6"], ["LD25", "2"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.684251968503937, 2.7842519685039373);
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


