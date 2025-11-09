const board = new PCB();

const rgb_knob = NeopixelArrayCircular_4_rgb_knob(pt(1.039, 1.039))
const rgb_ring = NeopixelArrayCircular_24_rgb_ring(pt(3.157, 1.039))
const rgb_sw = NeopixelArrayCircular_6_rgb_sw(pt(5.276, 1.039))
// jlc_th.th1
const KH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.922, 3.858), rotate: 0,
  id: 'KH1'
})
// jlc_th.th2
const KH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.961, 3.858), rotate: 0,
  id: 'KH2'
})
// jlc_th.th3
const KH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.922, 3.898), rotate: 0,
  id: 'KH3'
})
// usb.conn
const KJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(5.262, 2.283), rotate: 0,
  id: 'KJ1'
})
// usb.cc_pull.cc1.res
const KR1 = board.add(R_0603_1608Metric, {
  translate: pt(5.111, 2.538), rotate: 0,
  id: 'KR1'
})
// usb.cc_pull.cc2.res
const KR2 = board.add(R_0603_1608Metric, {
  translate: pt(5.267, 2.538), rotate: 0,
  id: 'KR2'
})
// tp_pwr.tp
const KTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 3.896), rotate: 0,
  id: 'KTP1'
})
// tp_gnd.tp
const KTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 3.896), rotate: 0,
  id: 'KTP2'
})
// reg_3v3.ic
const KU1 = board.add(SOT_223_3_TabPin2, {
  translate: pt(5.763, 2.260), rotate: 0,
  id: 'KU1'
})
// reg_3v3.in_cap.cap
const KC1 = board.add(C_0603_1608Metric, {
  translate: pt(5.821, 2.470), rotate: 0,
  id: 'KC1'
})
// reg_3v3.out_cap.cap
const KC2 = board.add(C_0805_2012Metric, {
  translate: pt(5.657, 2.480), rotate: 0,
  id: 'KC2'
})
// tp_3v3.tp
const KTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.567, 3.896), rotate: 0,
  id: 'KTP3'
})
// prot_3v3.diode
const KD1 = board.add(D_SOD_323, {
  translate: pt(0.815, 3.896), rotate: 0,
  id: 'KD1'
})
// mcu.ic
const KU2 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 2.648), rotate: 0,
  id: 'KU2'
})
// mcu.vcc_cap0.cap
const KC3 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 2.537), rotate: 0,
  id: 'KC3'
})
// mcu.vcc_cap1.cap
const KC4 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 2.521), rotate: 0,
  id: 'KC4'
})
// mcu.prog.conn
const KJ2 = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(2.096, 2.285), rotate: 0,
  id: 'KJ2'
})
// mcu.en_pull.rc.r
const KR3 = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 2.521), rotate: 0,
  id: 'KR3'
})
// mcu.en_pull.rc.c
const KC5 = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 2.651), rotate: 0,
  id: 'KC5'
})
// i2c_pull.scl_res.res
const KR4 = board.add(R_0603_1608Metric, {
  translate: pt(5.713, 3.437), rotate: 0,
  id: 'KR4'
})
// i2c_pull.sda_res.res
const KR5 = board.add(R_0603_1608Metric, {
  translate: pt(5.713, 3.533), rotate: 0,
  id: 'KR5'
})
// i2c_tp.tp_scl.tp
const KTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.589, 3.445), rotate: 0,
  id: 'KTP4'
})
// i2c_tp.tp_sda.tp
const KTP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.589, 3.559), rotate: 0,
  id: 'KTP5'
})
// usb_esd
const KU3 = board.add(SOT_23, {
  translate: pt(1.807, 3.925), rotate: 0,
  id: 'KU3'
})
// ledr.package
const KD2 = board.add(LED_0603_1608Metric, {
  translate: pt(5.244, 3.437), rotate: 0,
  id: 'KD2'
})
// ledr.res
const KR6 = board.add(R_0603_1608Metric, {
  translate: pt(5.243, 3.534), rotate: 0,
  id: 'KR6'
})
// ledy.package
const KD3 = board.add(LED_0603_1608Metric, {
  translate: pt(5.478, 3.437), rotate: 0,
  id: 'KD3'
})
// ledy.res
const KR7 = board.add(R_0603_1608Metric, {
  translate: pt(5.478, 3.534), rotate: 0,
  id: 'KR7'
})
// enc.package
const KSW1 = board.add(RotaryEncoder_Alps_EC11J15_Switch, {
  translate: pt(4.541, 2.463), rotate: 0,
  id: 'KSW1'
})
// sw[0].package
const KSW2 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(5.002, 3.037), rotate: 0,
  id: 'KSW2'
})
// sw[1].package
const KSW3 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(5.455, 3.037), rotate: 0,
  id: 'KSW3'
})
// sw[2].package
const KSW4 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(5.907, 3.037), rotate: 0,
  id: 'KSW4'
})
// sw[3].package
const KSW5 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.707, 3.520), rotate: 0,
  id: 'KSW5'
})
// sw[4].package
const KSW6 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(3.160, 3.520), rotate: 0,
  id: 'KSW6'
})
// sw[5].package
const KSW7 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(3.613, 3.520), rotate: 0,
  id: 'KSW7'
})
// als.ic
const KU4 = board.add(HVSOF6, {
  translate: pt(4.842, 3.449), rotate: 0,
  id: 'KU4'
})
// als.vcc_cap.cap
const KC6 = board.add(C_0603_1608Metric, {
  translate: pt(5.009, 3.437), rotate: 0,
  id: 'KC6'
})
// als.dvi_res
const KR8 = board.add(R_0603_1608Metric, {
  translate: pt(4.831, 3.559), rotate: 0,
  id: 'KR8'
})
// als.dvi_cap
const KC7 = board.add(C_0603_1608Metric, {
  translate: pt(4.987, 3.559), rotate: 0,
  id: 'KC7'
})
// dist.ic
const KU5 = board.add(ST_VL53L0X, {
  translate: pt(4.244, 2.983), rotate: 0,
  id: 'KU5'
})
// dist.vdd_cap[0].cap
const KC8 = board.add(C_0603_1608Metric, {
  translate: pt(4.379, 3.107), rotate: 0,
  id: 'KC8'
})
// dist.vdd_cap[1].cap
const KC9 = board.add(C_0805_2012Metric, {
  translate: pt(4.214, 3.117), rotate: 0,
  id: 'KC9'
})
// env.ic
const KU6 = board.add(Sensirion_DFN_4_1EP_2x2mm_P1mm_EP0_7x1_6mm, {
  translate: pt(4.345, 3.457), rotate: 0,
  id: 'KU6'
})
// env.vdd_cap.cap
const KC10 = board.add(C_0603_1608Metric, {
  translate: pt(4.346, 3.574), rotate: 0,
  id: 'KC10'
})
// oled.device.conn
const KJ3 = board.add(Hirose_FH12_30S_0_5SH_1x30_1MP_P0_50mm_Horizontal, {
  translate: pt(2.956, 3.172), rotate: 0,
  id: 'KJ3'
})
// oled.lcd
const KU7 = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(3.066, 2.634), rotate: 0,
  id: 'KU7'
})
// oled.c1_cap
const KC11 = board.add(C_0603_1608Metric, {
  translate: pt(3.815, 3.007), rotate: 0,
  id: 'KC11'
})
// oled.c2_cap
const KC12 = board.add(C_0603_1608Metric, {
  translate: pt(3.971, 3.007), rotate: 0,
  id: 'KC12'
})
// oled.iref_res
const KR9 = board.add(R_0603_1608Metric, {
  translate: pt(3.469, 3.124), rotate: 0,
  id: 'KR9'
})
// oled.vcomh_cap.cap
const KC13 = board.add(C_0805_2012Metric, {
  translate: pt(3.477, 3.017), rotate: 0,
  id: 'KC13'
})
// oled.vdd_cap1.cap
const KC14 = board.add(C_0603_1608Metric, {
  translate: pt(3.624, 3.124), rotate: 0,
  id: 'KC14'
})
// oled.vbat_cap.cap
const KC15 = board.add(C_0603_1608Metric, {
  translate: pt(3.780, 3.124), rotate: 0,
  id: 'KC15'
})
// oled.vcc_cap.cap
const KC16 = board.add(C_0805_2012Metric, {
  translate: pt(3.650, 3.017), rotate: 0,
  id: 'KC16'
})
// rgb_shift.ic
const KU8 = board.add(SOT_23_5, {
  translate: pt(4.636, 2.992), rotate: 0,
  id: 'KU8'
})
// rgb_shift.vdd_cap.cap
const KC17 = board.add(C_0603_1608Metric, {
  translate: pt(4.613, 3.127), rotate: 0,
  id: 'KC17'
})
// rgb_tp.tp
const KTP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.062, 3.896), rotate: 0,
  id: 'KTP6'
})
// io8_pur.res
const KR10 = board.add(R_0603_1608Metric, {
  translate: pt(1.555, 3.887), rotate: 0,
  id: 'KR10'
})
// spk_dac.rc.r
const KR11 = board.add(R_0603_1608Metric, {
  translate: pt(5.948, 3.437), rotate: 0,
  id: 'KR11'
})
// spk_dac.rc.c
const KC52 = board.add(C_0603_1608Metric, {
  translate: pt(5.948, 3.533), rotate: 0,
  id: 'KC52'
})
// spk_tp.tp
const KTP7 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.312, 3.896), rotate: 0,
  id: 'KTP7'
})
// spk_drv.ic
const KU9 = board.add(MSOP_8_3x3mm_P0_65mm, {
  translate: pt(6.180, 2.187), rotate: 0,
  id: 'KU9'
})
// spk_drv.pwr_cap0.cap
const KC53 = board.add(C_0603_1608Metric, {
  translate: pt(6.286, 2.324), rotate: 0,
  id: 'KC53'
})
// spk_drv.pwr_cap1.cap
const KC54 = board.add(C_0805_2012Metric, {
  translate: pt(6.121, 2.334), rotate: 0,
  id: 'KC54'
})
// spk_drv.inp_cap
const KC55 = board.add(C_0603_1608Metric, {
  translate: pt(6.113, 2.441), rotate: 0,
  id: 'KC55'
})
// spk_drv.inn_cap
const KC56 = board.add(C_0603_1608Metric, {
  translate: pt(6.269, 2.441), rotate: 0,
  id: 'KC56'
})
// spk.conn
const KJ4 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(3.995, 3.538), rotate: 0,
  id: 'KJ4'
})
// v5v_sense.div.top_res
const KR12 = board.add(R_0603_1608Metric, {
  translate: pt(6.182, 3.437), rotate: 0,
  id: 'KR12'
})
// v5v_sense.div.bottom_res
const KR13 = board.add(R_0603_1608Metric, {
  translate: pt(6.182, 3.533), rotate: 0,
  id: 'KR13'
})

board.setNetlist([
  {name: "Kvusb", pads: [["KJ1", "A4"], ["KJ1", "B9"], ["KJ1", "B4"], ["KJ1", "A9"], ["KTP1", "1"], ["KU1", "3"], ["KU8", "5"], ["KU9", "1"], ["KU9", "6"], ["KR12", "1"], ["KC1", "1"], ["KC17", "1"], ["KD4", "2"], ["KD5", "2"], ["KD6", "2"], ["KD7", "2"], ["KD8", "2"], ["KD9", "2"], ["KD10", "2"], ["KD11", "2"], ["KD12", "2"], ["KD13", "2"], ["KD14", "2"], ["KD15", "2"], ["KD16", "2"], ["KD17", "2"], ["KD18", "2"], ["KD19", "2"], ["KD20", "2"], ["KD21", "2"], ["KD22", "2"], ["KD23", "2"], ["KD24", "2"], ["KD25", "2"], ["KD26", "2"], ["KD27", "2"], ["KD28", "2"], ["KD29", "2"], ["KD30", "2"], ["KD31", "2"], ["KD32", "2"], ["KD33", "2"], ["KD34", "2"], ["KD35", "2"], ["KD36", "2"], ["KD37", "2"], ["KC53", "1"], ["KC54", "1"], ["KC18", "1"], ["KC19", "1"], ["KC20", "1"], ["KC21", "1"], ["KC22", "1"], ["KC23", "1"], ["KC24", "1"], ["KC25", "1"], ["KC26", "1"], ["KC27", "1"], ["KC28", "1"], ["KC29", "1"], ["KC30", "1"], ["KC31", "1"], ["KC32", "1"], ["KC33", "1"], ["KC34", "1"], ["KC35", "1"], ["KC36", "1"], ["KC37", "1"], ["KC38", "1"], ["KC39", "1"], ["KC40", "1"], ["KC41", "1"], ["KC42", "1"], ["KC43", "1"], ["KC44", "1"], ["KC45", "1"], ["KC46", "1"], ["KC47", "1"], ["KC48", "1"], ["KC49", "1"], ["KC50", "1"], ["KC51", "1"]]},
  {name: "Kgnd", pads: [["KU3", "3"], ["KJ1", "A1"], ["KJ1", "B12"], ["KJ1", "B1"], ["KJ1", "A12"], ["KTP2", "1"], ["KU1", "1"], ["KD1", "2"], ["KU2", "1"], ["KU2", "40"], ["KU2", "41"], ["KR6", "2"], ["KR7", "2"], ["KSW1", "C"], ["KSW1", "S2"], ["KSW2", "2"], ["KSW3", "2"], ["KSW4", "2"], ["KSW5", "2"], ["KSW6", "2"], ["KSW7", "2"], ["KU4", "2"], ["KU4", "3"], ["KU5", "2"], ["KU5", "3"], ["KU5", "4"], ["KU5", "6"], ["KU5", "12"], ["KU6", "4"], ["KU6", "5"], ["KU8", "1"], ["KU8", "3"], ["KU9", "7"], ["KC52", "2"], ["KR13", "2"], ["KJ1", "S1"], ["KC7", "2"], ["KR9", "2"], ["KC56", "2"], ["KC1", "2"], ["KC2", "2"], ["KC3", "2"], ["KC4", "2"], ["KJ2", "5"], ["KC6", "2"], ["KC8", "2"], ["KC9", "2"], ["KC10", "2"], ["KC13", "2"], ["KC14", "2"], ["KC15", "2"], ["KC16", "2"], ["KC17", "2"], ["KD4", "4"], ["KD5", "4"], ["KD6", "4"], ["KD7", "4"], ["KD8", "4"], ["KD9", "4"], ["KD10", "4"], ["KD11", "4"], ["KD12", "4"], ["KD13", "4"], ["KD14", "4"], ["KD15", "4"], ["KD16", "4"], ["KD17", "4"], ["KD18", "4"], ["KD19", "4"], ["KD20", "4"], ["KD21", "4"], ["KD22", "4"], ["KD23", "4"], ["KD24", "4"], ["KD25", "4"], ["KD26", "4"], ["KD27", "4"], ["KD28", "4"], ["KD29", "4"], ["KD30", "4"], ["KD31", "4"], ["KD32", "4"], ["KD33", "4"], ["KD34", "4"], ["KD35", "4"], ["KD36", "4"], ["KD37", "4"], ["KC53", "2"], ["KC54", "2"], ["KC5", "2"], ["KR1", "1"], ["KR2", "1"], ["KJ3", "8"], ["KJ3", "1"], ["KJ3", "30"], ["KJ3", "29"], ["KJ3", "17"], ["KJ3", "16"], ["KJ3", "21"], ["KJ3", "22"], ["KJ3", "23"], ["KJ3", "24"], ["KJ3", "25"], ["KJ3", "12"], ["KJ3", "10"], ["KJ3", "15"], ["KJ3", "13"], ["KC18", "2"], ["KC19", "2"], ["KC20", "2"], ["KC21", "2"], ["KC22", "2"], ["KC23", "2"], ["KC24", "2"], ["KC25", "2"], ["KC26", "2"], ["KC27", "2"], ["KC28", "2"], ["KC29", "2"], ["KC30", "2"], ["KC31", "2"], ["KC32", "2"], ["KC33", "2"], ["KC34", "2"], ["KC35", "2"], ["KC36", "2"], ["KC37", "2"], ["KC38", "2"], ["KC39", "2"], ["KC40", "2"], ["KC41", "2"], ["KC42", "2"], ["KC43", "2"], ["KC44", "2"], ["KC45", "2"], ["KC46", "2"], ["KC47", "2"], ["KC48", "2"], ["KC49", "2"], ["KC50", "2"], ["KC51", "2"]]},
  {name: "Kv3v3", pads: [["KU1", "2"], ["KTP3", "1"], ["KD1", "1"], ["KU2", "2"], ["KU4", "1"], ["KU5", "1"], ["KU5", "11"], ["KU6", "1"], ["KR10", "1"], ["KC2", "1"], ["KR8", "1"], ["KU5", "5"], ["KC3", "1"], ["KC4", "1"], ["KJ2", "1"], ["KR4", "1"], ["KR5", "1"], ["KC6", "1"], ["KC8", "1"], ["KC9", "1"], ["KC10", "1"], ["KJ3", "9"], ["KJ3", "6"], ["KC14", "1"], ["KC15", "1"], ["KR3", "1"], ["KJ3", "11"]]},
  {name: "Ki2c_chain_0.scl", pads: [["KU2", "33"], ["KU4", "6"], ["KU5", "10"], ["KU6", "2"], ["KR4", "2"], ["KTP4", "1"], ["KJ3", "18"]]},
  {name: "Ki2c_chain_0.sda", pads: [["KU2", "32"], ["KU4", "4"], ["KU5", "9"], ["KU6", "3"], ["KR5", "2"], ["KTP5", "1"], ["KJ3", "19"], ["KJ3", "20"]]},
  {name: "Kusb_chain_0.d_P", pads: [["KJ1", "A6"], ["KJ1", "B6"], ["KU3", "2"], ["KU2", "14"]]},
  {name: "Kusb_chain_0.d_N", pads: [["KJ1", "A7"], ["KJ1", "B7"], ["KU3", "1"], ["KU2", "13"]]},
  {name: "Kledr.signal", pads: [["KU2", "25"], ["KD2", "2"]]},
  {name: "Kledy.signal", pads: [["KU2", "24"], ["KD3", "2"]]},
  {name: "Kenc.a", pads: [["KU2", "12"], ["KSW1", "A"]]},
  {name: "Kenc.b", pads: [["KU2", "11"], ["KSW1", "B"]]},
  {name: "Kenc.sw", pads: [["KU2", "31"], ["KSW1", "S1"]]},
  {name: "Ksw[0].out", pads: [["KU2", "4"], ["KSW2", "1"]]},
  {name: "Ksw[1].out", pads: [["KU2", "6"], ["KSW3", "1"]]},
  {name: "Ksw[2].out", pads: [["KU2", "7"], ["KSW4", "1"]]},
  {name: "Ksw[3].out", pads: [["KU2", "35"], ["KSW5", "1"]]},
  {name: "Ksw[4].out", pads: [["KU2", "38"], ["KSW6", "1"]]},
  {name: "Ksw[5].out", pads: [["KU2", "39"], ["KSW7", "1"]]},
  {name: "Koled.reset", pads: [["KU2", "8"], ["KJ3", "14"]]},
  {name: "Kio8_pur.io", pads: [["KU2", "10"], ["KU8", "2"], ["KR10", "2"]]},
  {name: "Krgb_shift.output", pads: [["KU8", "4"], ["KD4", "1"], ["KTP6", "1"]]},
  {name: "Krgb_knob.dout", pads: [["KD7", "3"], ["KD8", "1"]]},
  {name: "Krgb_ring.dout", pads: [["KD31", "3"], ["KD32", "1"]]},
  {name: "Kspk_dac.input", pads: [["KU2", "9"], ["KR11", "1"]]},
  {name: "Kspk_dac.output", pads: [["KTP7", "1"], ["KC55", "2"], ["KR11", "2"], ["KC52", "1"]]},
  {name: "Kspk_drv.spk.a", pads: [["KU9", "5"], ["KJ4", "1"]]},
  {name: "Kspk_drv.spk.b", pads: [["KU9", "8"], ["KJ4", "2"]]},
  {name: "Kv5v_sense.output", pads: [["KU2", "5"], ["KR12", "2"], ["KR13", "1"]]},
  {name: "Kusb.conn.cc.cc1", pads: [["KJ1", "A5"], ["KR1", "2"]]},
  {name: "Kusb.conn.cc.cc2", pads: [["KJ1", "B5"], ["KR2", "2"]]},
  {name: "Kmcu.program_uart_node.a_tx", pads: [["KU2", "37"], ["KJ2", "3"]]},
  {name: "Kmcu.program_uart_node.b_tx", pads: [["KU2", "36"], ["KJ2", "4"]]},
  {name: "Kmcu.program_en_node", pads: [["KU2", "3"], ["KJ2", "6"], ["KR3", "2"], ["KC5", "1"]]},
  {name: "Kmcu.program_boot_node", pads: [["KU2", "27"], ["KJ2", "2"]]},
  {name: "Kledr.res.a", pads: [["KR6", "1"], ["KD2", "1"]]},
  {name: "Kledy.res.a", pads: [["KR7", "1"], ["KD3", "1"]]},
  {name: "Kals.dvi_res.b", pads: [["KR8", "2"], ["KU4", "5"], ["KC7", "1"]]},
  {name: "Kdist.ic.gpio1", pads: [["KU5", "7"]]},
  {name: "Koled.c1_cap.pos", pads: [["KC11", "1"], ["KJ3", "4"]]},
  {name: "Koled.c1_cap.neg", pads: [["KC11", "2"], ["KJ3", "5"]]},
  {name: "Koled.c2_cap.pos", pads: [["KC12", "1"], ["KJ3", "2"]]},
  {name: "Koled.c2_cap.neg", pads: [["KC12", "2"], ["KJ3", "3"]]},
  {name: "Koled.iref_res.a", pads: [["KR9", "1"], ["KJ3", "26"]]},
  {name: "Koled.device.vcomh", pads: [["KJ3", "27"], ["KC13", "1"]]},
  {name: "Koled.device.vcc", pads: [["KJ3", "28"], ["KC16", "1"]]},
  {name: "Krgb_knob.led[0].dout", pads: [["KD4", "3"], ["KD5", "1"]]},
  {name: "Krgb_knob.led[1].dout", pads: [["KD5", "3"], ["KD6", "1"]]},
  {name: "Krgb_knob.led[2].dout", pads: [["KD6", "3"], ["KD7", "1"]]},
  {name: "Krgb_ring.led[0].dout", pads: [["KD8", "3"], ["KD9", "1"]]},
  {name: "Krgb_ring.led[1].dout", pads: [["KD9", "3"], ["KD10", "1"]]},
  {name: "Krgb_ring.led[2].dout", pads: [["KD10", "3"], ["KD11", "1"]]},
  {name: "Krgb_ring.led[3].dout", pads: [["KD11", "3"], ["KD12", "1"]]},
  {name: "Krgb_ring.led[4].dout", pads: [["KD12", "3"], ["KD13", "1"]]},
  {name: "Krgb_ring.led[5].dout", pads: [["KD13", "3"], ["KD14", "1"]]},
  {name: "Krgb_ring.led[6].dout", pads: [["KD14", "3"], ["KD15", "1"]]},
  {name: "Krgb_ring.led[7].dout", pads: [["KD15", "3"], ["KD16", "1"]]},
  {name: "Krgb_ring.led[8].dout", pads: [["KD16", "3"], ["KD17", "1"]]},
  {name: "Krgb_ring.led[9].dout", pads: [["KD17", "3"], ["KD18", "1"]]},
  {name: "Krgb_ring.led[10].dout", pads: [["KD18", "3"], ["KD19", "1"]]},
  {name: "Krgb_ring.led[11].dout", pads: [["KD19", "3"], ["KD20", "1"]]},
  {name: "Krgb_ring.led[12].dout", pads: [["KD20", "3"], ["KD21", "1"]]},
  {name: "Krgb_ring.led[13].dout", pads: [["KD21", "3"], ["KD22", "1"]]},
  {name: "Krgb_ring.led[14].dout", pads: [["KD22", "3"], ["KD23", "1"]]},
  {name: "Krgb_ring.led[15].dout", pads: [["KD23", "3"], ["KD24", "1"]]},
  {name: "Krgb_ring.led[16].dout", pads: [["KD24", "3"], ["KD25", "1"]]},
  {name: "Krgb_ring.led[17].dout", pads: [["KD25", "3"], ["KD26", "1"]]},
  {name: "Krgb_ring.led[18].dout", pads: [["KD26", "3"], ["KD27", "1"]]},
  {name: "Krgb_ring.led[19].dout", pads: [["KD27", "3"], ["KD28", "1"]]},
  {name: "Krgb_ring.led[20].dout", pads: [["KD28", "3"], ["KD29", "1"]]},
  {name: "Krgb_ring.led[21].dout", pads: [["KD29", "3"], ["KD30", "1"]]},
  {name: "Krgb_ring.led[22].dout", pads: [["KD30", "3"], ["KD31", "1"]]},
  {name: "Krgb_sw.led[0].dout", pads: [["KD32", "3"], ["KD33", "1"]]},
  {name: "Krgb_sw.led[1].dout", pads: [["KD33", "3"], ["KD34", "1"]]},
  {name: "Krgb_sw.led[2].dout", pads: [["KD34", "3"], ["KD35", "1"]]},
  {name: "Krgb_sw.led[3].dout", pads: [["KD35", "3"], ["KD36", "1"]]},
  {name: "Krgb_sw.led[4].dout", pads: [["KD36", "3"], ["KD37", "1"]]},
  {name: "Krgb_sw.dout", pads: [["KD37", "3"]]},
  {name: "Kspk_drv.inp_cap.pos", pads: [["KC55", "1"], ["KU9", "3"]]},
  {name: "Kspk_drv.inn_cap.pos", pads: [["KC56", "1"], ["KU9", "4"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(6.4622047244094505, 4.0511811023622055);
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

function NeopixelArrayCircular_4_rgb_knob(xy, rot=270, radius=1, startAngle=0, endAngle=360, powerRadiusOffset=0.2) {
  const kCount = 4

  // Global params
  const traceWidth = 0.015
  const powerWidth = 0.05
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {
    footprints: {},
    pts: {}
  }

  // Helper functions
  const degToRad = Math.PI / 180  // multiply by degrees to get radians
  function pAdd(pt1, delta) {  // adds two points
    return pt1.map((e,i) => e + delta[i])
  }
  function pDiff(pos, neg) {  // return the difference between two points
    return pos.map((e,i) => e - neg[i])
  }
  function pCenter(pt1, pt2) {  // returns the midpoint
    return pt1.map((e,i) => (e + pt2[i]) / 2)
  }
  function vRotate(v, deg) {  // returns a vector rotated by some amount
    return [
      Math.cos(deg * degToRad) * v[0] - Math.sin(deg * degToRad) * v[1],
      Math.sin(deg * degToRad) * v[0] + Math.cos(deg * degToRad) * v[1],
    ]
  }
  function vScale(v, scale) {  // returns a vector scaled by some factor
    return v.map((e,i) => (e  * scale))
  }
  function vProject(v, ref) {  // returns the projection of v onto a reference vector
    const aDotb = v[0]*ref[0] + v[1]*ref[1]
    const bDotb = ref[0]*ref[0] + ref[1]*ref[1]
    return vScale(ref, aDotb / bDotb)
  }
  function smoothPath(pt1, pt2, pt1Angle, pt2Angle=null) {  // return the path(...) components for a curve between two points, with entry and exit slope
    function degToVector(deg, len=1) {  // given a slope in degrees, convert it to a vector
      return [Math.cos(deg * Math.PI / 180) * len, Math.sin(deg * Math.PI / 180) * len]
    }
    if (pt2Angle == null) {
      pt2Angle = pt1Angle
    }
    const pt1Projection = vProject(pDiff(pt2, pt1), degToVector(pt1Angle))
    const pt2Projection = vProject(pDiff(pt2, pt1), degToVector(pt2Angle))
    return [
      pt1,
      ["cubic",
       pAdd(pt1, vScale(pt1Projection, 0.33)),
       pCenter(pAdd(pt1, vScale(pt1Projection, 0.33)), pDiff(pt2, vScale(pt2Projection, 0.33))),
       pDiff(pt2, vScale(pt2Projection, 0.33)),
      ],
      pt2
    ]
  }

  const incrAngle = (endAngle - startAngle) / (kCount)

  var prevAngle = null
  var prevLed = null
  var prevGndOrigin = null
  var prevVinOrigin = null

  for (i=0; i<kCount; i++) {
    const angle = startAngle + incrAngle * i
    const origin = pAdd(xy, vRotate([radius, 0], angle))
    obj.footprints[`KD${4 + i}`] = led = board.add(LED_SK6812_EC15_1_5x1_5mm, {
      translate: origin,
      rotate: angle + rot,
      id: `KD${4 + i}`
    })

    const gndOrigin = pAdd(xy, vRotate([radius - powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(gndOrigin, led.pad(4),
                    angle)
      ), powerWidth)

    const vinOrigin = pAdd(xy, vRotate([radius + powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(vinOrigin, led.pad(2),
                    angle)
      ), powerWidth)

    if (prevLed != null) {
      board.wire(path(
        ...smoothPath(prevLed.pad(3), led.pad(1),
                      prevAngle + 90, angle + 90)
        ), traceWidth)
      board.wire(path(
        ...smoothPath(prevGndOrigin, gndOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
      board.wire(path(
        ...smoothPath(prevVinOrigin, vinOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
    }

    prevAngle = angle
    prevLed = led
    prevVinOrigin = vinOrigin
    prevGndOrigin = gndOrigin
  }

  return obj
}

function NeopixelArrayCircular_24_rgb_ring(xy, rot=270, radius=1, startAngle=0, endAngle=360, powerRadiusOffset=0.2) {
  const kCount = 24

  // Global params
  const traceWidth = 0.015
  const powerWidth = 0.05
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {
    footprints: {},
    pts: {}
  }

  // Helper functions
  const degToRad = Math.PI / 180  // multiply by degrees to get radians
  function pAdd(pt1, delta) {  // adds two points
    return pt1.map((e,i) => e + delta[i])
  }
  function pDiff(pos, neg) {  // return the difference between two points
    return pos.map((e,i) => e - neg[i])
  }
  function pCenter(pt1, pt2) {  // returns the midpoint
    return pt1.map((e,i) => (e + pt2[i]) / 2)
  }
  function vRotate(v, deg) {  // returns a vector rotated by some amount
    return [
      Math.cos(deg * degToRad) * v[0] - Math.sin(deg * degToRad) * v[1],
      Math.sin(deg * degToRad) * v[0] + Math.cos(deg * degToRad) * v[1],
    ]
  }
  function vScale(v, scale) {  // returns a vector scaled by some factor
    return v.map((e,i) => (e  * scale))
  }
  function vProject(v, ref) {  // returns the projection of v onto a reference vector
    const aDotb = v[0]*ref[0] + v[1]*ref[1]
    const bDotb = ref[0]*ref[0] + ref[1]*ref[1]
    return vScale(ref, aDotb / bDotb)
  }
  function smoothPath(pt1, pt2, pt1Angle, pt2Angle=null) {  // return the path(...) components for a curve between two points, with entry and exit slope
    function degToVector(deg, len=1) {  // given a slope in degrees, convert it to a vector
      return [Math.cos(deg * Math.PI / 180) * len, Math.sin(deg * Math.PI / 180) * len]
    }
    if (pt2Angle == null) {
      pt2Angle = pt1Angle
    }
    const pt1Projection = vProject(pDiff(pt2, pt1), degToVector(pt1Angle))
    const pt2Projection = vProject(pDiff(pt2, pt1), degToVector(pt2Angle))
    return [
      pt1,
      ["cubic",
       pAdd(pt1, vScale(pt1Projection, 0.33)),
       pCenter(pAdd(pt1, vScale(pt1Projection, 0.33)), pDiff(pt2, vScale(pt2Projection, 0.33))),
       pDiff(pt2, vScale(pt2Projection, 0.33)),
      ],
      pt2
    ]
  }

  const incrAngle = (endAngle - startAngle) / (kCount)

  var prevAngle = null
  var prevLed = null
  var prevGndOrigin = null
  var prevVinOrigin = null

  for (i=0; i<kCount; i++) {
    const angle = startAngle + incrAngle * i
    const origin = pAdd(xy, vRotate([radius, 0], angle))
    obj.footprints[`KD${8 + i}`] = led = board.add(LED_SK6812_EC15_1_5x1_5mm, {
      translate: origin,
      rotate: angle + rot,
      id: `KD${8 + i}`
    })

    const gndOrigin = pAdd(xy, vRotate([radius - powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(gndOrigin, led.pad(4),
                    angle)
      ), powerWidth)

    const vinOrigin = pAdd(xy, vRotate([radius + powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(vinOrigin, led.pad(2),
                    angle)
      ), powerWidth)

    if (prevLed != null) {
      board.wire(path(
        ...smoothPath(prevLed.pad(3), led.pad(1),
                      prevAngle + 90, angle + 90)
        ), traceWidth)
      board.wire(path(
        ...smoothPath(prevGndOrigin, gndOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
      board.wire(path(
        ...smoothPath(prevVinOrigin, vinOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
    }

    prevAngle = angle
    prevLed = led
    prevVinOrigin = vinOrigin
    prevGndOrigin = gndOrigin
  }

  return obj
}

function NeopixelArrayCircular_6_rgb_sw(xy, rot=270, radius=1, startAngle=0, endAngle=360, powerRadiusOffset=0.2) {
  const kCount = 6

  // Global params
  const traceWidth = 0.015
  const powerWidth = 0.05
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {
    footprints: {},
    pts: {}
  }

  // Helper functions
  const degToRad = Math.PI / 180  // multiply by degrees to get radians
  function pAdd(pt1, delta) {  // adds two points
    return pt1.map((e,i) => e + delta[i])
  }
  function pDiff(pos, neg) {  // return the difference between two points
    return pos.map((e,i) => e - neg[i])
  }
  function pCenter(pt1, pt2) {  // returns the midpoint
    return pt1.map((e,i) => (e + pt2[i]) / 2)
  }
  function vRotate(v, deg) {  // returns a vector rotated by some amount
    return [
      Math.cos(deg * degToRad) * v[0] - Math.sin(deg * degToRad) * v[1],
      Math.sin(deg * degToRad) * v[0] + Math.cos(deg * degToRad) * v[1],
    ]
  }
  function vScale(v, scale) {  // returns a vector scaled by some factor
    return v.map((e,i) => (e  * scale))
  }
  function vProject(v, ref) {  // returns the projection of v onto a reference vector
    const aDotb = v[0]*ref[0] + v[1]*ref[1]
    const bDotb = ref[0]*ref[0] + ref[1]*ref[1]
    return vScale(ref, aDotb / bDotb)
  }
  function smoothPath(pt1, pt2, pt1Angle, pt2Angle=null) {  // return the path(...) components for a curve between two points, with entry and exit slope
    function degToVector(deg, len=1) {  // given a slope in degrees, convert it to a vector
      return [Math.cos(deg * Math.PI / 180) * len, Math.sin(deg * Math.PI / 180) * len]
    }
    if (pt2Angle == null) {
      pt2Angle = pt1Angle
    }
    const pt1Projection = vProject(pDiff(pt2, pt1), degToVector(pt1Angle))
    const pt2Projection = vProject(pDiff(pt2, pt1), degToVector(pt2Angle))
    return [
      pt1,
      ["cubic",
       pAdd(pt1, vScale(pt1Projection, 0.33)),
       pCenter(pAdd(pt1, vScale(pt1Projection, 0.33)), pDiff(pt2, vScale(pt2Projection, 0.33))),
       pDiff(pt2, vScale(pt2Projection, 0.33)),
      ],
      pt2
    ]
  }

  const incrAngle = (endAngle - startAngle) / (kCount)

  var prevAngle = null
  var prevLed = null
  var prevGndOrigin = null
  var prevVinOrigin = null

  for (i=0; i<kCount; i++) {
    const angle = startAngle + incrAngle * i
    const origin = pAdd(xy, vRotate([radius, 0], angle))
    obj.footprints[`KD${32 + i}`] = led = board.add(LED_SK6812_EC15_1_5x1_5mm, {
      translate: origin,
      rotate: angle + rot,
      id: `KD${32 + i}`
    })

    const gndOrigin = pAdd(xy, vRotate([radius - powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(gndOrigin, led.pad(4),
                    angle)
      ), powerWidth)

    const vinOrigin = pAdd(xy, vRotate([radius + powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(vinOrigin, led.pad(2),
                    angle)
      ), powerWidth)

    if (prevLed != null) {
      board.wire(path(
        ...smoothPath(prevLed.pad(3), led.pad(1),
                      prevAngle + 90, angle + 90)
        ), traceWidth)
      board.wire(path(
        ...smoothPath(prevGndOrigin, gndOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
      board.wire(path(
        ...smoothPath(prevVinOrigin, vinOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
    }

    prevAngle = angle
    prevLed = led
    prevVinOrigin = vinOrigin
    prevGndOrigin = gndOrigin
  }

  return obj
}

