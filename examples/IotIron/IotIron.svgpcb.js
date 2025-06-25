const board = new PCB();

// jlc_th.th1
const IH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.408, 3.059), rotate: 0,
  id: 'IH1'
})
// jlc_th.th2
const IH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.448, 3.059), rotate: 0,
  id: 'IH2'
})
// jlc_th.th3
const IH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.408, 3.099), rotate: 0,
  id: 'IH3'
})
// usb.conn
const IJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(3.321, 1.905), rotate: 0,
  id: 'IJ1'
})
// tp_pwr.tp
const ITP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.314, 3.097), rotate: 0,
  id: 'ITP1'
})
// tp_gnd.tp
const ITP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.063, 3.097), rotate: 0,
  id: 'ITP2'
})
// reg_3v3.ic
const IU1 = board.add(SOT_23_6, {
  translate: pt(2.331, 1.807), rotate: 0,
  id: 'IU1'
})
// reg_3v3.fb.div.top_res
const IR1 = board.add(R_0603_1608Metric, {
  translate: pt(2.049, 2.156), rotate: 0,
  id: 'IR1'
})
// reg_3v3.fb.div.bottom_res
const IR2 = board.add(R_0603_1608Metric, {
  translate: pt(2.205, 2.156), rotate: 0,
  id: 'IR2'
})
// reg_3v3.hf_in_cap.cap
const IC1 = board.add(C_0603_1608Metric, {
  translate: pt(2.361, 2.156), rotate: 0,
  id: 'IC1'
})
// reg_3v3.boot_cap
const IC2 = board.add(C_0603_1608Metric, {
  translate: pt(2.517, 2.156), rotate: 0,
  id: 'IC2'
})
// reg_3v3.power_path.inductor
const IL1 = board.add(L_Sunlord_SWPA5040S, {
  translate: pt(2.101, 1.849), rotate: 0,
  id: 'IL1'
})
// reg_3v3.power_path.in_cap.cap.c[0]
const IC3 = board.add(C_1206_3216Metric, {
  translate: pt(2.081, 2.042), rotate: 0,
  id: 'IC3'
})
// reg_3v3.power_path.in_cap.cap.c[1]
const IC4 = board.add(C_1206_3216Metric, {
  translate: pt(2.302, 2.042), rotate: 0,
  id: 'IC4'
})
// reg_3v3.power_path.out_cap.cap
const IC5 = board.add(C_0805_2012Metric, {
  translate: pt(2.498, 2.035), rotate: 0,
  id: 'IC5'
})
// reg_3v3.en_res
const IR3 = board.add(R_0603_1608Metric, {
  translate: pt(2.049, 2.252), rotate: 0,
  id: 'IR3'
})
// tp_3v3.tp
const ITP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.564, 3.097), rotate: 0,
  id: 'ITP3'
})
// prot_3v3.diode
const ID1 = board.add(D_SOD_323, {
  translate: pt(0.063, 3.097), rotate: 0,
  id: 'ID1'
})
// reg_gate.ic
const IU2 = board.add(SOT_89_3, {
  translate: pt(3.761, 1.839), rotate: 0,
  id: 'IU2'
})
// reg_gate.in_cap.cap
const IC6 = board.add(C_0805_2012Metric, {
  translate: pt(3.716, 2.015), rotate: 0,
  id: 'IC6'
})
// reg_gate.out_cap.cap
const IC7 = board.add(C_0603_1608Metric, {
  translate: pt(3.880, 2.005), rotate: 0,
  id: 'IC7'
})
// tp_gate.tp
const ITP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.311, 3.097), rotate: 0,
  id: 'ITP4'
})
// mcu.ic
const IU3 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'IU3'
})
// mcu.vcc_cap0.cap
const IC8 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.242), rotate: 0,
  id: 'IC8'
})
// mcu.vcc_cap1.cap
const IC9 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.226), rotate: 0,
  id: 'IC9'
})
// mcu.prog.conn
const IJ2 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(2.067, 0.079), rotate: 0,
  id: 'IJ2'
})
// mcu.en_pull.rc.r
const IR4 = board.add(R_0603_1608Metric, {
  translate: pt(1.987, 0.356), rotate: 0,
  id: 'IR4'
})
// mcu.en_pull.rc.c
const IC10 = board.add(C_0603_1608Metric, {
  translate: pt(2.143, 0.356), rotate: 0,
  id: 'IC10'
})
// i2c_pull.scl_res.res
const IR5 = board.add(R_0603_1608Metric, {
  translate: pt(3.270, 2.661), rotate: 0,
  id: 'IR5'
})
// i2c_pull.sda_res.res
const IR6 = board.add(R_0603_1608Metric, {
  translate: pt(3.270, 2.757), rotate: 0,
  id: 'IR6'
})
// pd.ic
const IU4 = board.add(WQFN_14_1EP_2_5x2_5mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(0.890, 2.705), rotate: 0,
  id: 'IU4'
})
// pd.vdd_cap[0].cap
const IC11 = board.add(C_0603_1608Metric, {
  translate: pt(1.049, 2.846), rotate: 0,
  id: 'IC11'
})
// pd.vdd_cap[1].cap
const IC12 = board.add(C_0805_2012Metric, {
  translate: pt(0.884, 2.856), rotate: 0,
  id: 'IC12'
})
// usb_esd
const IU5 = board.add(SOT_23, {
  translate: pt(3.293, 3.126), rotate: 0,
  id: 'IU5'
})
// vusb_sense.div.top_res
const IR7 = board.add(R_0603_1608Metric, {
  translate: pt(3.505, 2.661), rotate: 0,
  id: 'IR7'
})
// vusb_sense.div.bottom_res
const IR8 = board.add(R_0603_1608Metric, {
  translate: pt(3.505, 2.757), rotate: 0,
  id: 'IR8'
})
// temp.ic
const IU6 = board.add(WSON_6_1EP_3x3mm_P0_95mm, {
  translate: pt(1.300, 2.705), rotate: 0,
  id: 'IU6'
})
// temp.vdd_cap.cap
const IC13 = board.add(C_0603_1608Metric, {
  translate: pt(1.283, 2.846), rotate: 0,
  id: 'IC13'
})
// enc.package
const ISW1 = board.add(RotaryEncoder_Alps_EC11J15_Switch, {
  translate: pt(1.479, 2.085), rotate: 0,
  id: 'ISW1'
})
// oled.device.conn
const IJ3 = board.add(Hirose_FH12_30S_0_5SH_1x30_1MP_P0_50mm_Horizontal, {
  translate: pt(2.800, 1.054), rotate: 0,
  id: 'IJ3'
})
// oled.lcd
const IU7 = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(2.910, 0.516), rotate: 0,
  id: 'IU7'
})
// oled.c1_cap
const IC14 = board.add(C_0603_1608Metric, {
  translate: pt(3.659, 0.889), rotate: 0,
  id: 'IC14'
})
// oled.c2_cap
const IC15 = board.add(C_0603_1608Metric, {
  translate: pt(3.815, 0.889), rotate: 0,
  id: 'IC15'
})
// oled.iref_res
const IR9 = board.add(R_0603_1608Metric, {
  translate: pt(3.313, 1.006), rotate: 0,
  id: 'IR9'
})
// oled.vcomh_cap.cap
const IC16 = board.add(C_0805_2012Metric, {
  translate: pt(3.321, 0.899), rotate: 0,
  id: 'IC16'
})
// oled.vdd_cap1.cap
const IC17 = board.add(C_0603_1608Metric, {
  translate: pt(3.469, 1.006), rotate: 0,
  id: 'IC17'
})
// oled.vbat_cap.cap
const IC18 = board.add(C_0603_1608Metric, {
  translate: pt(3.624, 1.006), rotate: 0,
  id: 'IC18'
})
// oled.vcc_cap.cap
const IC19 = board.add(C_0805_2012Metric, {
  translate: pt(3.494, 0.899), rotate: 0,
  id: 'IC19'
})
// spk_drv.ic
const IU8 = board.add(QFN_16_1EP_3x3mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(0.493, 2.716), rotate: 0,
  id: 'IU8'
})
// spk_drv.pwr_cap0.cap
const IC20 = board.add(C_0603_1608Metric, {
  translate: pt(0.641, 2.868), rotate: 0,
  id: 'IC20'
})
// spk_drv.pwr_cap1.cap
const IC21 = board.add(C_0805_2012Metric, {
  translate: pt(0.476, 2.878), rotate: 0,
  id: 'IC21'
})
// spk.conn
const IJ4 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.589, 2.762), rotate: 0,
  id: 'IJ4'
})
// ledr.package
const ID2 = board.add(LED_0603_1608Metric, {
  translate: pt(1.941, 2.661), rotate: 0,
  id: 'ID2'
})
// ledr.res
const IR10 = board.add(R_0603_1608Metric, {
  translate: pt(1.941, 2.758), rotate: 0,
  id: 'IR10'
})
// conv.power_path.inductor
const IL2 = board.add(L_TDK_SLF12575, {
  translate: pt(0.280, 1.996), rotate: 0,
  id: 'IL2'
})
// conv.power_path.in_cap.cap.c[0]
const IC22 = board.add(C_0805_2012Metric, {
  translate: pt(0.398, 2.340), rotate: 0,
  id: 'IC22'
})
// conv.power_path.in_cap.cap.c[1]
const IC23 = board.add(C_0805_2012Metric, {
  translate: pt(0.571, 2.340), rotate: 0,
  id: 'IC23'
})
// conv.power_path.out_cap.cap
const IC24 = board.add(C_0805_2012Metric, {
  translate: pt(0.744, 2.340), rotate: 0,
  id: 'IC24'
})
// conv.sw.driver.ic
const IU9 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.744, 1.846), rotate: 0,
  id: 'IU9'
})
// conv.sw.driver.cap.cap
const IC25 = board.add(C_0603_1608Metric, {
  translate: pt(0.909, 2.330), rotate: 0,
  id: 'IC25'
})
// conv.sw.driver.boot_cap.cap
const IC26 = board.add(C_0603_1608Metric, {
  translate: pt(0.389, 2.446), rotate: 0,
  id: 'IC26'
})
// conv.sw.low_fet
const IQ1 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.744, 2.098), rotate: 0,
  id: 'IQ1'
})
// conv.sw.low_gate_res
const IR11 = board.add(R_0603_1608Metric, {
  translate: pt(0.545, 2.446), rotate: 0,
  id: 'IR11'
})
// conv.sw.high_fet
const IQ2 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.146, 2.407), rotate: 0,
  id: 'IQ2'
})
// conv.sw.high_gate_res
const IR12 = board.add(R_0603_1608Metric, {
  translate: pt(0.701, 2.446), rotate: 0,
  id: 'IR12'
})
// tp_conv.tp
const ITP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.813, 3.097), rotate: 0,
  id: 'ITP5'
})
// low_pull.res
const IR13 = board.add(R_0603_1608Metric, {
  translate: pt(2.807, 3.088), rotate: 0,
  id: 'IR13'
})
// low_rc.rc.r
const IR14 = board.add(R_0603_1608Metric, {
  translate: pt(3.974, 2.661), rotate: 0,
  id: 'IR14'
})
// low_rc.rc.c
const IC27 = board.add(C_0603_1608Metric, {
  translate: pt(3.974, 2.757), rotate: 0,
  id: 'IC27'
})
// high_pull.res
const IR15 = board.add(R_0603_1608Metric, {
  translate: pt(3.041, 3.088), rotate: 0,
  id: 'IR15'
})
// high_rc.rc.r
const IR16 = board.add(R_0603_1608Metric, {
  translate: pt(2.176, 2.661), rotate: 0,
  id: 'IR16'
})
// high_rc.rc.c
const IC28 = board.add(C_0603_1608Metric, {
  translate: pt(2.176, 2.757), rotate: 0,
  id: 'IC28'
})
// tp_pwm_l.tp
const ITP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.062, 3.097), rotate: 0,
  id: 'ITP6'
})
// tp_pwm_h.tp
const ITP7 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.312, 3.097), rotate: 0,
  id: 'ITP7'
})
// touch_sink
const IU10 = board.add(Symbol_DucklingSolid, {
  translate: pt(3.566, 3.059), rotate: 0,
  id: 'IU10'
})
// iron.conn
const IJ5 = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(2.764, 2.010), rotate: 0,
  id: 'IJ5'
})
// iron.isense_res.res.res
const IR17 = board.add(R_2512_6332Metric, {
  translate: pt(2.843, 2.196), rotate: 0,
  id: 'IR17'
})
// vsense.div.top_res
const IR18 = board.add(R_0603_1608Metric, {
  translate: pt(4.209, 2.661), rotate: 0,
  id: 'IR18'
})
// vsense.div.bottom_res
const IR19 = board.add(R_0603_1608Metric, {
  translate: pt(4.209, 2.757), rotate: 0,
  id: 'IR19'
})
// tp_v.tp
const ITP8 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.563, 3.097), rotate: 0,
  id: 'ITP8'
})
// vfilt.rc.r
const IR20 = board.add(R_0603_1608Metric, {
  translate: pt(3.740, 2.661), rotate: 0,
  id: 'IR20'
})
// vfilt.rc.c
const IC29 = board.add(C_0603_1608Metric, {
  translate: pt(3.740, 2.757), rotate: 0,
  id: 'IC29'
})
// ifilt.r1
const IR21 = board.add(R_0603_1608Metric, {
  translate: pt(2.410, 2.661), rotate: 0,
  id: 'IR21'
})
// ifilt.r2
const IR22 = board.add(R_0603_1608Metric, {
  translate: pt(2.410, 2.757), rotate: 0,
  id: 'IR22'
})
// tp_i.rc.r
const IR23 = board.add(R_0603_1608Metric, {
  translate: pt(2.645, 2.661), rotate: 0,
  id: 'IR23'
})
// tp_i.rc.c
const IC30 = board.add(C_0603_1608Metric, {
  translate: pt(2.645, 2.757), rotate: 0,
  id: 'IC30'
})
// iamp.tp
const ITP9 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.561, 3.097), rotate: 0,
  id: 'ITP9'
})
// tamp.r1
const IR24 = board.add(R_0603_1608Metric, {
  translate: pt(2.880, 2.661), rotate: 0,
  id: 'IR24'
})
// tamp.r2
const IR25 = board.add(R_0603_1608Metric, {
  translate: pt(3.036, 2.661), rotate: 0,
  id: 'IR25'
})
// tamp.rf
const IR26 = board.add(R_0603_1608Metric, {
  translate: pt(2.880, 2.757), rotate: 0,
  id: 'IR26'
})
// tamp.rg
const IR27 = board.add(R_0603_1608Metric, {
  translate: pt(3.036, 2.757), rotate: 0,
  id: 'IR27'
})
// tp_t.tp
const ITP10 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.811, 3.097), rotate: 0,
  id: 'ITP10'
})
// packed_opamp.ic
const IU11 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.146, 2.738), rotate: 0,
  id: 'IU11'
})
// packed_opamp.vdd_cap.cap
const IC31 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.913), rotate: 0,
  id: 'IC31'
})

board.setNetlist([
  {name: "Ivusb", pads: [["IJ1", "A4"], ["IJ1", "B9"], ["IJ1", "B4"], ["IJ1", "A9"], ["IU4", "2"], ["ITP1", "1"], ["IU1", "3"], ["IU2", "3"], ["IR7", "1"], ["IR3", "1"], ["IC1", "1"], ["IC6", "1"], ["IC3", "1"], ["IC4", "1"], ["IQ2", "5"], ["IQ2", "6"], ["IQ2", "7"], ["IQ2", "8"], ["IC22", "1"], ["IC23", "1"]]},
  {name: "Ignd", pads: [["IU5", "3"], ["IJ1", "A1"], ["IJ1", "B12"], ["IJ1", "B1"], ["IJ1", "A12"], ["ITP2", "1"], ["IU1", "1"], ["ID1", "2"], ["IU2", "2"], ["IU3", "1"], ["IU3", "40"], ["IU3", "41"], ["IU4", "8"], ["IU4", "9"], ["IU4", "15"], ["IU6", "2"], ["ISW1", "C"], ["ISW1", "S2"], ["IU8", "3"], ["IU8", "11"], ["IU8", "15"], ["IU8", "17"], ["IR13", "1"], ["IR15", "1"], ["IR8", "2"], ["IC27", "2"], ["IC28", "2"], ["IR19", "2"], ["IC29", "2"], ["IC30", "2"], ["IJ1", "S1"], ["IR9", "2"], ["IR22", "2"], ["IC1", "2"], ["IC6", "2"], ["IC7", "2"], ["IC8", "2"], ["IC9", "2"], ["IJ2", "5"], ["IC11", "2"], ["IC12", "2"], ["IC13", "2"], ["IC16", "2"], ["IC17", "2"], ["IC18", "2"], ["IC19", "2"], ["IC20", "2"], ["IC21", "2"], ["IU11", "4"], ["IR2", "2"], ["IC10", "2"], ["IR17", "1"], ["IR27", "1"], ["IJ3", "8"], ["IJ3", "1"], ["IJ3", "30"], ["IJ3", "29"], ["IJ3", "17"], ["IJ3", "16"], ["IJ3", "21"], ["IJ3", "22"], ["IJ3", "23"], ["IJ3", "24"], ["IJ3", "25"], ["IJ3", "12"], ["IJ3", "10"], ["IJ3", "15"], ["IJ3", "13"], ["IQ1", "1"], ["IQ1", "2"], ["IQ1", "3"], ["IC5", "2"], ["IC24", "2"], ["IU9", "7"], ["IC31", "2"], ["IC3", "2"], ["IC4", "2"], ["IC22", "2"], ["IC23", "2"], ["IC25", "2"]]},
  {name: "Iv3v3", pads: [["ITP3", "1"], ["ID1", "1"], ["IU3", "2"], ["IU4", "3"], ["IU4", "4"], ["IU6", "5"], ["IU8", "4"], ["IU8", "7"], ["IU8", "8"], ["ID2", "2"], ["IU11", "8"], ["IR1", "1"], ["IC8", "1"], ["IC9", "1"], ["IJ2", "1"], ["IR5", "1"], ["IR6", "1"], ["IC11", "1"], ["IC12", "1"], ["IC13", "1"], ["IJ3", "9"], ["IJ3", "6"], ["IC17", "1"], ["IC18", "1"], ["IC20", "1"], ["IC21", "1"], ["IR4", "1"], ["IC31", "1"], ["IJ3", "11"], ["IL1", "2"], ["IC5", "1"]]},
  {name: "Ivgate", pads: [["IU2", "1"], ["ITP4", "1"], ["IU9", "1"], ["IC7", "1"], ["IC25", "1"]]},
  {name: "Iconv_out", pads: [["ITP5", "1"], ["IJ5", "2"], ["IR18", "1"], ["IL2", "2"], ["IC24", "1"]]},
  {name: "Ii2c_pull.i2c.scl", pads: [["IU3", "35"], ["IU4", "6"], ["IU6", "6"], ["IR5", "2"], ["IJ3", "18"]]},
  {name: "Ii2c_pull.i2c.sda", pads: [["IU3", "34"], ["IU4", "7"], ["IU6", "1"], ["IR6", "2"], ["IJ3", "19"], ["IJ3", "20"]]},
  {name: "Iusb.cc.cc1", pads: [["IJ1", "A5"], ["IU4", "10"], ["IU4", "11"]]},
  {name: "Iusb.cc.cc2", pads: [["IJ1", "B5"], ["IU4", "1"], ["IU4", "14"]]},
  {name: "Ipd.int", pads: [["IU3", "38"], ["IU4", "5"]]},
  {name: "Iusb_chain_0.d_P", pads: [["IJ1", "A6"], ["IJ1", "B6"], ["IU5", "2"], ["IU3", "14"]]},
  {name: "Iusb_chain_0.d_N", pads: [["IJ1", "A7"], ["IJ1", "B7"], ["IU5", "1"], ["IU3", "13"]]},
  {name: "Ivusb_sense.output", pads: [["IU3", "39"], ["IR7", "2"], ["IR8", "1"]]},
  {name: "Ienc.a", pads: [["IU3", "10"], ["ISW1", "A"]]},
  {name: "Ienc.b", pads: [["IU3", "9"], ["ISW1", "B"]]},
  {name: "Ienc.sw", pads: [["IU3", "8"], ["ISW1", "S1"]]},
  {name: "Ioled.reset", pads: [["IU3", "11"], ["IJ3", "14"]]},
  {name: "Ispk_drv.i2s.sck", pads: [["IU3", "32"], ["IU8", "16"]]},
  {name: "Ispk_drv.i2s.ws", pads: [["IU3", "31"], ["IU8", "14"]]},
  {name: "Ispk_drv.i2s.sd", pads: [["IU3", "33"], ["IU8", "1"]]},
  {name: "Ispk_drv.out.a", pads: [["IU8", "9"], ["IJ4", "1"]]},
  {name: "Ispk_drv.out.b", pads: [["IU8", "10"], ["IJ4", "2"]]},
  {name: "Imcu.program_boot_node", pads: [["IR10", "2"], ["IU3", "27"], ["IJ2", "2"]]},
  {name: "Ilow_pull.io", pads: [["IU3", "4"], ["IR13", "2"], ["IR14", "1"]]},
  {name: "Ilow_rc.output", pads: [["IU9", "6"], ["ITP6", "1"], ["IR14", "2"], ["IC27", "1"]]},
  {name: "Ihigh_pull.io", pads: [["IU3", "5"], ["IR15", "2"], ["IR16", "1"]]},
  {name: "Ihigh_rc.output", pads: [["IU9", "5"], ["ITP7", "1"], ["IR16", "2"], ["IC28", "1"]]},
  {name: "Itouch_sink.pad", pads: [["IU3", "15"], ["IU10", "1"]]},
  {name: "Ivsense.output", pads: [["ITP8", "1"], ["IR20", "1"], ["IR18", "2"], ["IR19", "1"]]},
  {name: "Ivfilt.output", pads: [["IU3", "6"], ["IR20", "2"], ["IC29", "1"]]},
  {name: "Iiron.isense", pads: [["IU11", "3"], ["IR24", "1"], ["IR17", "2"], ["IJ5", "1"]]},
  {name: "Iifilt.output", pads: [["IR23", "1"], ["IR21", "1"], ["IU11", "1"]]},
  {name: "Itp_i.output", pads: [["IU3", "7"], ["ITP9", "1"], ["IR23", "2"], ["IC30", "1"]]},
  {name: "Itamp.input_positive", pads: [["IR25", "1"], ["IJ5", "3"], ["ITP10", "1"]]},
  {name: "Itamp.output", pads: [["IU3", "12"], ["IR26", "1"], ["IU11", "7"]]},
  {name: "Ipacked_opamp.inn.0", pads: [["IU11", "2"], ["IR21", "2"], ["IR22", "1"]]},
  {name: "Ipacked_opamp.inp.1", pads: [["IU11", "5"], ["IR25", "2"], ["IR27", "2"]]},
  {name: "Ipacked_opamp.inn.1", pads: [["IU11", "6"], ["IR24", "2"], ["IR26", "2"]]},
  {name: "Ireg_3v3.fb.output", pads: [["IU1", "4"], ["IR1", "2"], ["IR2", "1"]]},
  {name: "Ireg_3v3.boot_cap.neg", pads: [["IC2", "2"], ["IU1", "2"], ["IL1", "1"]]},
  {name: "Ireg_3v3.boot_cap.pos", pads: [["IC2", "1"], ["IU1", "6"]]},
  {name: "Ireg_3v3.en_res.b", pads: [["IR3", "2"], ["IU1", "5"]]},
  {name: "Imcu.program_uart_node.a_tx", pads: [["IU3", "37"], ["IJ2", "3"]]},
  {name: "Imcu.program_uart_node.b_tx", pads: [["IU3", "36"], ["IJ2", "4"]]},
  {name: "Imcu.program_en_node", pads: [["IU3", "3"], ["IJ2", "6"], ["IR4", "2"], ["IC10", "1"]]},
  {name: "Ipd.ic.vconn", pads: [["IU4", "12"], ["IU4", "13"]]},
  {name: "Ioled.c1_cap.pos", pads: [["IC14", "1"], ["IJ3", "4"]]},
  {name: "Ioled.c1_cap.neg", pads: [["IC14", "2"], ["IJ3", "5"]]},
  {name: "Ioled.c2_cap.pos", pads: [["IC15", "1"], ["IJ3", "2"]]},
  {name: "Ioled.c2_cap.neg", pads: [["IC15", "2"], ["IJ3", "3"]]},
  {name: "Ioled.iref_res.a", pads: [["IR9", "1"], ["IJ3", "26"]]},
  {name: "Ioled.device.vcomh", pads: [["IJ3", "27"], ["IC16", "1"]]},
  {name: "Ioled.device.vcc", pads: [["IJ3", "28"], ["IC19", "1"]]},
  {name: "Iledr.res.a", pads: [["IR10", "1"], ["ID2", "1"]]},
  {name: "Iconv.sw_out_force", pads: [["IQ1", "5"], ["IQ1", "6"], ["IQ1", "7"], ["IQ1", "8"], ["IQ2", "1"], ["IQ2", "2"], ["IQ2", "3"], ["IL2", "1"], ["IU9", "4"], ["IC26", "2"]]},
  {name: "Iconv.sw.low_gate_res.a", pads: [["IR11", "1"], ["IU9", "8"]]},
  {name: "Iconv.sw.low_gate_res.b", pads: [["IR11", "2"], ["IQ1", "4"]]},
  {name: "Iconv.sw.high_gate_res.a", pads: [["IR12", "1"], ["IU9", "3"]]},
  {name: "Iconv.sw.high_gate_res.b", pads: [["IR12", "2"], ["IQ2", "4"]]},
  {name: "Iconv.sw.driver.ic.hb", pads: [["IU9", "2"], ["IC26", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.385236220472439, 3.2523622047244096);
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


