const board = new PCB();

// batt.conn
const RJ1 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.487, 3.263), rotate: 0,
  id: 'RJ1'
})
// servos[0].conn
const RJ2 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.591, 2.944), rotate: 0,
  id: 'RJ2'
})
// servos[1].conn
const RJ3 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.045, 2.110), rotate: 0,
  id: 'RJ3'
})
// servos[2].conn
const RJ4 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.071, 2.944), rotate: 0,
  id: 'RJ4'
})
// servos[3].conn
const RJ5 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.331, 2.944), rotate: 0,
  id: 'RJ5'
})
// servos[4].conn
const RJ6 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(3.864, 2.110), rotate: 0,
  id: 'RJ6'
})
// servos[5].conn
const RJ7 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(4.124, 2.110), rotate: 0,
  id: 'RJ7'
})
// servos[6].conn
const RJ8 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.305, 2.110), rotate: 0,
  id: 'RJ8'
})
// servos[7].conn
const RJ9 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(3.344, 2.110), rotate: 0,
  id: 'RJ9'
})
// servos[8].conn
const RJ10 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.565, 2.110), rotate: 0,
  id: 'RJ10'
})
// servos[9].conn
const RJ11 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.850, 2.944), rotate: 0,
  id: 'RJ11'
})
// servos[10].conn
const RJ12 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(3.084, 2.110), rotate: 0,
  id: 'RJ12'
})
// servos[11].conn
const RJ13 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.785, 2.110), rotate: 0,
  id: 'RJ13'
})
// imu.ic
const RU1 = board.add(Bosch_LGA_14_3x2_5mm_P0_5mm, {
  translate: pt(0.073, 3.196), rotate: 0,
  id: 'RU1'
})
// imu.vdd_cap.cap
const RC1 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 3.327), rotate: 0,
  id: 'RC1'
})
// imu.vddio_cap.cap
const RC2 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 3.327), rotate: 0,
  id: 'RC2'
})
// servos_cam[0].conn
const RJ14 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.824, 2.110), rotate: 0,
  id: 'RJ14'
})
// servos_cam[1].conn
const RJ15 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(3.604, 2.110), rotate: 0,
  id: 'RJ15'
})
// jlc_th.th1
const RH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.737, 3.133), rotate: 0,
  id: 'RH1'
})
// jlc_th.th2
const RH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.776, 3.133), rotate: 0,
  id: 'RH2'
})
// jlc_th.th3
const RH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.737, 3.172), rotate: 0,
  id: 'RH3'
})
// tp_vbatt.tp
const RTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.552, 3.170), rotate: 0,
  id: 'RTP1'
})
// tp_gnd.tp
const RTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.801, 3.170), rotate: 0,
  id: 'RTP2'
})
// reg_3v3.ic
const RU2 = board.add(SOT_89_3, {
  translate: pt(3.500, 2.672), rotate: 0,
  id: 'RU2'
})
// reg_3v3.in_cap.cap
const RC3 = board.add(C_0603_1608Metric, {
  translate: pt(3.446, 2.839), rotate: 0,
  id: 'RC3'
})
// reg_3v3.out_cap.cap
const RC4 = board.add(C_0603_1608Metric, {
  translate: pt(3.602, 2.839), rotate: 0,
  id: 'RC4'
})
// tp_3v3.tp
const RTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.302, 3.170), rotate: 0,
  id: 'RTP3'
})
// reg_14v.ic
const RU3 = board.add(SOT_23_5, {
  translate: pt(1.951, 2.641), rotate: 0,
  id: 'RU3'
})
// reg_14v.fb.div.top_res
const RR1 = board.add(R_0603_1608Metric, {
  translate: pt(1.928, 2.906), rotate: 0,
  id: 'RR1'
})
// reg_14v.fb.div.bottom_res
const RR2 = board.add(R_0603_1608Metric, {
  translate: pt(2.084, 2.906), rotate: 0,
  id: 'RR2'
})
// reg_14v.cff
const RC5 = board.add(C_0603_1608Metric, {
  translate: pt(2.240, 2.906), rotate: 0,
  id: 'RC5'
})
// reg_14v.inductor
const RL1 = board.add(L_1210_3225Metric, {
  translate: pt(2.161, 2.636), rotate: 0,
  id: 'RL1'
})
// reg_14v.rect
const RD1 = board.add(D_SOD_323, {
  translate: pt(2.327, 2.785), rotate: 0,
  id: 'RD1'
})
// reg_14v.in_cap.cap
const RC6 = board.add(C_0805_2012Metric, {
  translate: pt(2.157, 2.786), rotate: 0,
  id: 'RC6'
})
// reg_14v.out_cap.cap
const RC7 = board.add(C_1206_3216Metric, {
  translate: pt(1.961, 2.793), rotate: 0,
  id: 'RC7'
})
// tp_14v.tp
const RTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.052, 3.170), rotate: 0,
  id: 'RTP4'
})
// reg_2v5.ic
const RU4 = board.add(SOT_23, {
  translate: pt(4.244, 2.641), rotate: 0,
  id: 'RU4'
})
// reg_2v5.in_cap.cap
const RC8 = board.add(C_0603_1608Metric, {
  translate: pt(4.227, 2.776), rotate: 0,
  id: 'RC8'
})
// reg_2v5.out_cap.cap
const RC9 = board.add(C_0603_1608Metric, {
  translate: pt(4.383, 2.776), rotate: 0,
  id: 'RC9'
})
// reg_1v2.ic
const RU5 = board.add(SOT_23, {
  translate: pt(3.854, 2.641), rotate: 0,
  id: 'RU5'
})
// reg_1v2.in_cap.cap
const RC10 = board.add(C_0603_1608Metric, {
  translate: pt(3.836, 2.776), rotate: 0,
  id: 'RC10'
})
// reg_1v2.out_cap.cap
const RC11 = board.add(C_0603_1608Metric, {
  translate: pt(3.992, 2.776), rotate: 0,
  id: 'RC11'
})
// mcu.ic
const RU6 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'RU6'
})
// mcu.vcc_cap0.cap
const RC12 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.419), rotate: 0,
  id: 'RC12'
})
// mcu.vcc_cap1.cap
const RC13 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.403), rotate: 0,
  id: 'RC13'
})
// mcu.prog.conn
const RJ16 = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(2.096, 0.167), rotate: 0,
  id: 'RJ16'
})
// mcu.en_pull.rc.r
const RR3 = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.403), rotate: 0,
  id: 'RR3'
})
// mcu.en_pull.rc.c
const RC14 = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.533), rotate: 0,
  id: 'RC14'
})
// mcu_servo.swd.conn
const RJ17 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(1.444, 1.819), rotate: 0,
  id: 'RJ17'
})
// mcu_servo.ic
const RU7 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(1.064, 1.943), rotate: 0,
  id: 'RU7'
})
// mcu_servo.pwr_cap[0].cap
const RC15 = board.add(C_0805_2012Metric, {
  translate: pt(1.373, 1.976), rotate: 0,
  id: 'RC15'
})
// mcu_servo.pwr_cap[1].cap
const RC16 = board.add(C_0603_1608Metric, {
  translate: pt(1.538, 1.966), rotate: 0,
  id: 'RC16'
})
// mcu_servo.pwr_cap[2].cap
const RC17 = board.add(C_0603_1608Metric, {
  translate: pt(1.365, 2.082), rotate: 0,
  id: 'RC17'
})
// mcu_servo.pwr_cap[3].cap
const RC18 = board.add(C_0603_1608Metric, {
  translate: pt(1.520, 2.082), rotate: 0,
  id: 'RC18'
})
// mcu_servo.vdda_cap_0.cap
const RC19 = board.add(C_0603_1608Metric, {
  translate: pt(0.920, 2.214), rotate: 0,
  id: 'RC19'
})
// mcu_servo.vdda_cap_1.cap
const RC20 = board.add(C_0603_1608Metric, {
  translate: pt(1.076, 2.214), rotate: 0,
  id: 'RC20'
})
// mcu_test.swd.conn
const RJ18 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(0.138, 2.183), rotate: 0,
  id: 'RJ18'
})
// mcu_test.ic
const RU8 = board.add(QFN_56_1EP_7x7mm_P0_4mm_EP3_2x3_2mm, {
  translate: pt(0.163, 1.903), rotate: 0,
  id: 'RU8'
})
// mcu_test.iovdd_cap[0].cap
const RC21 = board.add(C_0603_1608Metric, {
  translate: pt(0.373, 2.133), rotate: 0,
  id: 'RC21'
})
// mcu_test.iovdd_cap[1].cap
const RC22 = board.add(C_0603_1608Metric, {
  translate: pt(0.529, 2.133), rotate: 0,
  id: 'RC22'
})
// mcu_test.iovdd_cap[2].cap
const RC23 = board.add(C_0603_1608Metric, {
  translate: pt(0.685, 2.133), rotate: 0,
  id: 'RC23'
})
// mcu_test.iovdd_cap[3].cap
const RC24 = board.add(C_0603_1608Metric, {
  translate: pt(0.373, 2.230), rotate: 0,
  id: 'RC24'
})
// mcu_test.iovdd_cap[4].cap
const RC25 = board.add(C_0603_1608Metric, {
  translate: pt(0.529, 2.230), rotate: 0,
  id: 'RC25'
})
// mcu_test.iovdd_cap[5].cap
const RC26 = board.add(C_0603_1608Metric, {
  translate: pt(0.685, 2.230), rotate: 0,
  id: 'RC26'
})
// mcu_test.avdd_cap.cap
const RC27 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.330), rotate: 0,
  id: 'RC27'
})
// mcu_test.vreg_in_cap.cap
const RC28 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 2.330), rotate: 0,
  id: 'RC28'
})
// mcu_test.mem.ic
const RU9 = board.add(SOIC_8_5_23x5_23mm_P1_27mm, {
  translate: pt(0.548, 1.853), rotate: 0,
  id: 'RU9'
})
// mcu_test.mem.vcc_cap.cap
const RC29 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 2.330), rotate: 0,
  id: 'RC29'
})
// mcu_test.dvdd_cap[0].cap
const RC30 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 2.330), rotate: 0,
  id: 'RC30'
})
// mcu_test.dvdd_cap[1].cap
const RC31 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 2.330), rotate: 0,
  id: 'RC31'
})
// mcu_test.vreg_out_cap.cap
const RC32 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.427), rotate: 0,
  id: 'RC32'
})
// i2c_pull.scl_res.res
const RR4 = board.add(R_0603_1608Metric, {
  translate: pt(1.559, 3.162), rotate: 0,
  id: 'RR4'
})
// i2c_pull.sda_res.res
const RR5 = board.add(R_0603_1608Metric, {
  translate: pt(1.559, 3.259), rotate: 0,
  id: 'RR5'
})
// i2c_tp.tp_scl.tp
const RTP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.846, 3.170), rotate: 0,
  id: 'RTP5'
})
// i2c_tp.tp_sda.tp
const RTP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.846, 3.285), rotate: 0,
  id: 'RTP6'
})
// led.package
const RD2 = board.add(LED_0603_1608Metric, {
  translate: pt(1.089, 3.162), rotate: 0,
  id: 'RD2'
})
// led.res
const RR6 = board.add(R_0603_1608Metric, {
  translate: pt(1.089, 3.259), rotate: 0,
  id: 'RR6'
})
// servo_led.package
const RD3 = board.add(LED_0603_1608Metric, {
  translate: pt(1.324, 3.162), rotate: 0,
  id: 'RD3'
})
// servo_led.res
const RR7 = board.add(R_0603_1608Metric, {
  translate: pt(1.324, 3.259), rotate: 0,
  id: 'RR7'
})
// test_led.led[0].package
const RD4 = board.add(LED_0603_1608Metric, {
  translate: pt(3.055, 2.603), rotate: 0,
  id: 'RD4'
})
// test_led.led[0].res
const RR8 = board.add(R_0603_1608Metric, {
  translate: pt(3.055, 2.797), rotate: 0,
  id: 'RR8'
})
// test_led.led[1].package
const RD5 = board.add(LED_0603_1608Metric, {
  translate: pt(3.211, 2.603), rotate: 0,
  id: 'RD5'
})
// test_led.led[1].res
const RR9 = board.add(R_0603_1608Metric, {
  translate: pt(3.211, 2.797), rotate: 0,
  id: 'RR9'
})
// test_led.led[2].package
const RD6 = board.add(LED_0603_1608Metric, {
  translate: pt(3.055, 2.700), rotate: 0,
  id: 'RD6'
})
// test_led.led[2].res
const RR10 = board.add(R_0603_1608Metric, {
  translate: pt(3.055, 2.894), rotate: 0,
  id: 'RR10'
})
// test_led.led[3].package
const RD7 = board.add(LED_0603_1608Metric, {
  translate: pt(3.211, 2.700), rotate: 0,
  id: 'RD7'
})
// test_led.led[3].res
const RR11 = board.add(R_0603_1608Metric, {
  translate: pt(3.211, 2.894), rotate: 0,
  id: 'RR11'
})
// oled.device.conn
const RJ19 = board.add(Hirose_FH35C_31S_0_3SHW_1x31_1MP_P0_30mm_Horizontal, {
  translate: pt(2.631, 0.865), rotate: 0,
  id: 'RJ19'
})
// oled.lcd
const RU10 = board.add(Lcd_Er_Oled0_96_1c_Outline, {
  translate: pt(3.254, 0.293), rotate: 0,
  id: 'RU10'
})
// oled.iref_res
const RR12 = board.add(R_0603_1608Metric, {
  translate: pt(3.571, 0.653), rotate: 0,
  id: 'RR12'
})
// oled.vcomh_cap.cap
const RC33 = board.add(C_0805_2012Metric, {
  translate: pt(3.075, 0.663), rotate: 0,
  id: 'RC33'
})
// oled.vp_cap.cap
const RC34 = board.add(C_0603_1608Metric, {
  translate: pt(3.727, 0.653), rotate: 0,
  id: 'RC34'
})
// oled.vdd_cap.cap
const RC35 = board.add(C_0603_1608Metric, {
  translate: pt(2.846, 0.783), rotate: 0,
  id: 'RC35'
})
// oled.vcc_cap.cap
const RC36 = board.add(C_1206_3216Metric, {
  translate: pt(2.878, 0.670), rotate: 0,
  id: 'RC36'
})
// oled.vsl_res
const RR13 = board.add(R_0603_1608Metric, {
  translate: pt(3.002, 0.783), rotate: 0,
  id: 'RR13'
})
// oled.vsl_d1
const RD8 = board.add(D_SOD_323, {
  translate: pt(3.244, 0.662), rotate: 0,
  id: 'RD8'
})
// oled.vsl_d2
const RD9 = board.add(D_SOD_323, {
  translate: pt(3.410, 0.662), rotate: 0,
  id: 'RD9'
})
// cam.device.conn
const RJ20 = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(1.396, 2.767), rotate: 0,
  id: 'RJ20'
})
// cam.dovdd_cap.cap
const RC37 = board.add(C_0603_1608Metric, {
  translate: pt(1.098, 2.953), rotate: 0,
  id: 'RC37'
})
// cam.reset_cap
const RC38 = board.add(C_0603_1608Metric, {
  translate: pt(1.254, 2.953), rotate: 0,
  id: 'RC38'
})
// cam.pclk_cap
const RC39 = board.add(C_0603_1608Metric, {
  translate: pt(1.409, 2.953), rotate: 0,
  id: 'RC39'
})
// cam.reset_pull.res
const RR14 = board.add(R_0603_1608Metric, {
  translate: pt(1.565, 2.953), rotate: 0,
  id: 'RR14'
})
// rgbs.led[0]
const RD10 = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.591, 2.609), rotate: 0,
  id: 'RD10'
})
// rgbs.led[1]
const RD11 = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.796, 2.609), rotate: 0,
  id: 'RD11'
})
// rgbs.led[2]
const RD12 = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.591, 2.688), rotate: 0,
  id: 'RD12'
})
// rgbs.led[3]
const RD13 = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.796, 2.688), rotate: 0,
  id: 'RD13'
})
// rgbs.led[4]
const RD14 = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.591, 2.767), rotate: 0,
  id: 'RD14'
})
// rgbs.led[5]
const RD15 = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.796, 2.767), rotate: 0,
  id: 'RD15'
})
// rgbs.led[6]
const RD16 = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.591, 2.846), rotate: 0,
  id: 'RD16'
})
// rgbs.led[7]
const RD17 = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.796, 2.846), rotate: 0,
  id: 'RD17'
})
// rgbs.led[8]
const RD18 = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.591, 2.924), rotate: 0,
  id: 'RD18'
})
// rgbs.led[9]
const RD19 = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.796, 2.924), rotate: 0,
  id: 'RD19'
})

board.setNetlist([
  {name: "Rvbatt", pads: [["RJ1", "2"], ["RTP1", "1"], ["RU2", "2"], ["RU3", "5"], ["RU4", "3"], ["RU5", "3"], ["RJ2", "2"], ["RJ3", "2"], ["RJ4", "2"], ["RJ5", "2"], ["RJ6", "2"], ["RJ7", "2"], ["RJ8", "2"], ["RJ9", "2"], ["RJ10", "2"], ["RJ11", "2"], ["RJ12", "2"], ["RJ13", "2"], ["RJ14", "2"], ["RJ15", "2"], ["RD10", "2"], ["RD11", "2"], ["RD12", "2"], ["RD13", "2"], ["RD14", "2"], ["RD15", "2"], ["RD16", "2"], ["RD17", "2"], ["RD18", "2"], ["RD19", "2"], ["RL1", "1"], ["RU3", "4"], ["RC3", "1"], ["RC6", "1"], ["RC8", "1"], ["RC10", "1"]]},
  {name: "Rgnd", pads: [["RJ1", "1"], ["RTP2", "1"], ["RU2", "1"], ["RU3", "2"], ["RU4", "1"], ["RU5", "1"], ["RU6", "1"], ["RU6", "40"], ["RU6", "41"], ["RU7", "8"], ["RU7", "23"], ["RU7", "35"], ["RU7", "47"], ["RU7", "44"], ["RU8", "19"], ["RU8", "57"], ["RU1", "1"], ["RU1", "2"], ["RU1", "3"], ["RU1", "6"], ["RU1", "7"], ["RR6", "2"], ["RR7", "2"], ["RJ2", "3"], ["RJ3", "3"], ["RJ4", "3"], ["RJ5", "3"], ["RJ6", "3"], ["RJ7", "3"], ["RJ8", "3"], ["RJ9", "3"], ["RJ10", "3"], ["RJ11", "3"], ["RJ12", "3"], ["RJ13", "3"], ["RJ14", "3"], ["RJ15", "3"], ["RD10", "4"], ["RD11", "4"], ["RD12", "4"], ["RD13", "4"], ["RD14", "4"], ["RD15", "4"], ["RD16", "4"], ["RD17", "4"], ["RD18", "4"], ["RD19", "4"], ["RR12", "2"], ["RD9", "1"], ["RC38", "2"], ["RC39", "2"], ["RC3", "2"], ["RC4", "2"], ["RC6", "2"], ["RC7", "2"], ["RC8", "2"], ["RC9", "2"], ["RC10", "2"], ["RC11", "2"], ["RC12", "2"], ["RC13", "2"], ["RJ16", "5"], ["RJ17", "5"], ["RC15", "2"], ["RC16", "2"], ["RC17", "2"], ["RC18", "2"], ["RC19", "2"], ["RC20", "2"], ["RJ18", "5"], ["RC21", "2"], ["RC22", "2"], ["RC23", "2"], ["RC24", "2"], ["RC25", "2"], ["RC26", "2"], ["RC27", "2"], ["RC28", "2"], ["RU9", "4"], ["RC30", "2"], ["RC31", "2"], ["RC32", "2"], ["RC1", "2"], ["RC2", "2"], ["RR8", "2"], ["RR9", "2"], ["RR10", "2"], ["RR11", "2"], ["RC33", "2"], ["RC34", "2"], ["RC35", "2"], ["RC36", "2"], ["RJ20", "10"], ["RJ20", "23"], ["RC37", "2"], ["RR2", "2"], ["RC14", "2"], ["RJ19", "7"], ["RJ19", "1"], ["RJ19", "31"], ["RJ19", "26"], ["RJ19", "16"], ["RJ19", "15"], ["RJ19", "21"], ["RJ19", "22"], ["RJ19", "23"], ["RJ19", "24"], ["RJ19", "25"], ["RJ19", "12"], ["RJ19", "14"], ["RJ19", "10"], ["RJ19", "11"], ["RJ20", "17"], ["RC29", "2"]]},
  {name: "Rv3v3", pads: [["RU2", "3"], ["RTP3", "1"], ["RU6", "2"], ["RU7", "1"], ["RU7", "9"], ["RU7", "24"], ["RU7", "36"], ["RU7", "48"], ["RU8", "1"], ["RU8", "10"], ["RU8", "22"], ["RU8", "33"], ["RU8", "42"], ["RU8", "49"], ["RU8", "44"], ["RU8", "43"], ["RU8", "48"], ["RU1", "5"], ["RU1", "12"], ["RU1", "8"], ["RC4", "1"], ["RC12", "1"], ["RC13", "1"], ["RJ16", "1"], ["RJ17", "1"], ["RC15", "1"], ["RC16", "1"], ["RC17", "1"], ["RC18", "1"], ["RC19", "1"], ["RC20", "1"], ["RJ18", "1"], ["RC21", "1"], ["RC22", "1"], ["RC23", "1"], ["RC24", "1"], ["RC25", "1"], ["RC26", "1"], ["RC27", "1"], ["RC28", "1"], ["RU9", "8"], ["RR4", "1"], ["RR5", "1"], ["RC2", "1"], ["RC1", "1"], ["RC35", "1"], ["RJ20", "14"], ["RC37", "1"], ["RR14", "1"], ["RR3", "1"], ["RJ19", "8"], ["RJ19", "17"], ["RJ19", "13"], ["RC29", "1"]]},
  {name: "Rv14", pads: [["RTP4", "1"], ["RD1", "1"], ["RC5", "1"], ["RC7", "1"], ["RR1", "1"], ["RJ19", "5"], ["RJ19", "27"], ["RC36", "1"]]},
  {name: "Rv2v5", pads: [["RU4", "2"], ["RJ20", "21"], ["RC9", "1"]]},
  {name: "Rv1v2", pads: [["RU5", "2"], ["RJ20", "15"], ["RC11", "1"]]},
  {name: "Rmcu_servo.reset_node", pads: [["RU6", "12"], ["RU7", "7"], ["RJ17", "3"]]},
  {name: "Ri2c_chain_0.scl", pads: [["RU6", "10"], ["RU1", "13"], ["RU7", "21"], ["RU8", "37"], ["RR4", "2"], ["RTP5", "1"], ["RJ19", "18"], ["RJ20", "20"]]},
  {name: "Ri2c_chain_0.sda", pads: [["RU6", "9"], ["RU1", "14"], ["RU7", "22"], ["RU8", "36"], ["RR5", "2"], ["RJ20", "22"], ["RTP6", "1"], ["RJ19", "19"], ["RJ19", "20"]]},
  {name: "Rled.signal", pads: [["RU6", "33"], ["RD2", "2"]]},
  {name: "Rservo_led.signal", pads: [["RU7", "33"], ["RD3", "2"]]},
  {name: "Rmcu_test.gpio.led_0", pads: [["RU8", "4"], ["RD4", "2"]]},
  {name: "Rmcu_test.gpio.led_1", pads: [["RU8", "12"], ["RD5", "2"]]},
  {name: "Rmcu_test.gpio.led_2", pads: [["RU8", "14"], ["RD6", "2"]]},
  {name: "Rmcu_test.gpio.led_3", pads: [["RU8", "16"], ["RD7", "2"]]},
  {name: "Roled.reset", pads: [["RU6", "8"], ["RJ19", "9"]]},
  {name: "Rcam.dvp8.xclk", pads: [["RU6", "17"], ["RJ20", "12"]]},
  {name: "Rcam.dvp8.pclk", pads: [["RU6", "20"], ["RC39", "1"], ["RJ20", "8"]]},
  {name: "Rcam.dvp8.href", pads: [["RU6", "14"], ["RJ20", "16"]]},
  {name: "Rcam.dvp8.vsync", pads: [["RU6", "13"], ["RJ20", "18"]]},
  {name: "Rcam.dvp8.y0", pads: [["RU6", "22"], ["RJ20", "6"]]},
  {name: "Rcam.dvp8.y1", pads: [["RU6", "24"], ["RJ20", "4"]]},
  {name: "Rcam.dvp8.y2", pads: [["RU6", "25"], ["RJ20", "3"]]},
  {name: "Rcam.dvp8.y3", pads: [["RU6", "23"], ["RJ20", "5"]]},
  {name: "Rcam.dvp8.y4", pads: [["RU6", "21"], ["RJ20", "7"]]},
  {name: "Rcam.dvp8.y5", pads: [["RU6", "19"], ["RJ20", "9"]]},
  {name: "Rcam.dvp8.y6", pads: [["RU6", "18"], ["RJ20", "11"]]},
  {name: "Rcam.dvp8.y7", pads: [["RU6", "15"], ["RJ20", "13"]]},
  {name: "Rservos[0].pwm", pads: [["RU6", "34"], ["RJ2", "1"]]},
  {name: "Rservos[0].fb", pads: [["RU6", "38"], ["RJ2", "4"]]},
  {name: "Rservos[1].pwm", pads: [["RU6", "35"], ["RJ3", "1"]]},
  {name: "Rservos[1].fb", pads: [["RU6", "39"], ["RJ3", "4"]]},
  {name: "Rservos[2].pwm", pads: [["RU6", "4"], ["RJ4", "1"]]},
  {name: "Rservos[2].fb", pads: [["RU6", "5"], ["RJ4", "4"]]},
  {name: "Rservos[3].pwm", pads: [["RU6", "6"], ["RJ5", "1"]]},
  {name: "Rservos[3].fb", pads: [["RU6", "7"], ["RJ5", "4"]]},
  {name: "Rservos[4].pwm", pads: [["RU7", "41"], ["RJ6", "1"]]},
  {name: "Rservos[4].fb", pads: [["RU7", "10"], ["RJ6", "4"]]},
  {name: "Rservos[5].pwm", pads: [["RU7", "43"], ["RJ7", "1"]]},
  {name: "Rservos[5].fb", pads: [["RU7", "11"], ["RJ7", "4"]]},
  {name: "Rservos[6].pwm", pads: [["RU7", "45"], ["RJ8", "1"]]},
  {name: "Rservos[6].fb", pads: [["RU7", "12"], ["RJ8", "4"]]},
  {name: "Rservos[7].pwm", pads: [["RU7", "26"], ["RJ9", "1"]]},
  {name: "Rservos[7].fb", pads: [["RU7", "14"], ["RJ9", "4"]]},
  {name: "Rservos[8].pwm", pads: [["RU7", "32"], ["RJ10", "1"]]},
  {name: "Rservos[8].fb", pads: [["RU7", "19"], ["RJ10", "4"]]},
  {name: "Rservos[9].pwm", pads: [["RU7", "31"], ["RJ11", "1"]]},
  {name: "Rservos[9].fb", pads: [["RU7", "18"], ["RJ11", "4"]]},
  {name: "Rservos[10].pwm", pads: [["RU7", "30"], ["RJ12", "1"]]},
  {name: "Rservos[10].fb", pads: [["RU7", "17"], ["RJ12", "4"]]},
  {name: "Rservos[11].pwm", pads: [["RU7", "28"], ["RJ13", "1"]]},
  {name: "Rservos[11].fb", pads: [["RU7", "15"], ["RJ13", "4"]]},
  {name: "Rservos_cam[0].pwm", pads: [["RU7", "46"], ["RJ14", "1"]]},
  {name: "Rservos_cam[0].fb", pads: [["RU7", "13"], ["RJ14", "4"]]},
  {name: "Rservos_cam[1].pwm", pads: [["RU7", "29"], ["RJ15", "1"]]},
  {name: "Rservos_cam[1].fb", pads: [["RU7", "16"], ["RJ15", "4"]]},
  {name: "Rrgbs.din", pads: [["RU6", "32"], ["RD10", "1"]]},
  {name: "Rimu.int1", pads: [["RU1", "4"]]},
  {name: "Rimu.int2", pads: [["RU1", "9"]]},
  {name: "Rreg_14v.fb.output", pads: [["RU3", "3"], ["RC5", "2"], ["RR1", "2"], ["RR2", "1"]]},
  {name: "Rreg_14v.inductor.b", pads: [["RL1", "2"], ["RU3", "1"], ["RD1", "2"]]},
  {name: "Rmcu.program_uart_node.a_tx", pads: [["RU6", "37"], ["RJ16", "3"]]},
  {name: "Rmcu.program_uart_node.b_tx", pads: [["RU6", "36"], ["RJ16", "4"]]},
  {name: "Rmcu.program_en_node", pads: [["RU6", "3"], ["RJ16", "6"], ["RR3", "2"], ["RC14", "1"]]},
  {name: "Rmcu.program_boot_node", pads: [["RU6", "27"], ["RJ16", "2"]]},
  {name: "Rmcu_servo.swd_node.swdio", pads: [["RU7", "34"], ["RJ17", "2"]]},
  {name: "Rmcu_servo.swd_node.swclk", pads: [["RU7", "37"], ["RJ17", "4"]]},
  {name: "Rmcu_servo.swd.swo", pads: [["RU7", "42"], ["RJ17", "6"]]},
  {name: "Rmcu_servo.ic.osc.xtal_in", pads: [["RU7", "5"]]},
  {name: "Rmcu_servo.ic.osc.xtal_out", pads: [["RU7", "6"]]},
  {name: "Rmcu_test.swd_node.swdio", pads: [["RU8", "25"], ["RJ18", "2"]]},
  {name: "Rmcu_test.swd_node.swclk", pads: [["RU8", "24"], ["RJ18", "4"]]},
  {name: "Rmcu_test.reset_node", pads: [["RU8", "26"], ["RJ18", "3"]]},
  {name: "Rmcu_test.ic.qspi.sck", pads: [["RU8", "52"], ["RU9", "6"]]},
  {name: "Rmcu_test.ic.qspi.mosi", pads: [["RU8", "53"], ["RU9", "5"]]},
  {name: "Rmcu_test.ic.qspi.miso", pads: [["RU8", "55"], ["RU9", "2"]]},
  {name: "Rmcu_test.ic.qspi_cs", pads: [["RU8", "56"], ["RU9", "1"]]},
  {name: "Rmcu_test.ic.qspi_sd2", pads: [["RU8", "54"], ["RU9", "3"]]},
  {name: "Rmcu_test.ic.qspi_sd3", pads: [["RU8", "51"], ["RU9", "7"]]},
  {name: "Rmcu_test.ic.vreg_vout", pads: [["RU8", "45"], ["RU8", "23"], ["RU8", "50"], ["RC30", "1"], ["RC31", "1"], ["RC32", "1"]]},
  {name: "Rmcu_test.swd.swo", pads: [["RU8", "27"], ["RJ18", "6"]]},
  {name: "Rmcu_test.ic.xosc.xtal_in", pads: [["RU8", "20"]]},
  {name: "Rmcu_test.ic.xosc.xtal_out", pads: [["RU8", "21"]]},
  {name: "Rled.res.a", pads: [["RR6", "1"], ["RD2", "1"]]},
  {name: "Rservo_led.res.a", pads: [["RR7", "1"], ["RD3", "1"]]},
  {name: "Rtest_led.led[0].res.a", pads: [["RR8", "1"], ["RD4", "1"]]},
  {name: "Rtest_led.led[1].res.a", pads: [["RR9", "1"], ["RD5", "1"]]},
  {name: "Rtest_led.led[2].res.a", pads: [["RR10", "1"], ["RD6", "1"]]},
  {name: "Rtest_led.led[3].res.a", pads: [["RR11", "1"], ["RD7", "1"]]},
  {name: "Roled.iref_res.a", pads: [["RR12", "1"], ["RJ19", "6"]]},
  {name: "Roled.device.vcomh", pads: [["RC33", "1"], ["RJ19", "3"], ["RJ19", "29"]]},
  {name: "Roled.device.vp", pads: [["RC34", "1"], ["RJ19", "4"], ["RJ19", "28"]]},
  {name: "Roled.device.vsl", pads: [["RR13", "1"], ["RJ19", "2"], ["RJ19", "30"]]},
  {name: "Roled.vsl_res.b", pads: [["RR13", "2"], ["RD8", "2"]]},
  {name: "Roled.vsl_d1.cathode", pads: [["RD8", "1"], ["RD9", "2"]]},
  {name: "Rcam.reset_cap.pos", pads: [["RC38", "1"], ["RR14", "2"], ["RJ20", "19"]]},
  {name: "Rcam.device.y.0", pads: [["RJ20", "1"]]},
  {name: "Rcam.device.y.1", pads: [["RJ20", "2"]]},
  {name: "Rrgbs.led[0].dout", pads: [["RD10", "3"], ["RD11", "1"]]},
  {name: "Rrgbs.led[1].dout", pads: [["RD11", "3"], ["RD12", "1"]]},
  {name: "Rrgbs.led[2].dout", pads: [["RD12", "3"], ["RD13", "1"]]},
  {name: "Rrgbs.led[3].dout", pads: [["RD13", "3"], ["RD14", "1"]]},
  {name: "Rrgbs.led[4].dout", pads: [["RD14", "3"], ["RD15", "1"]]},
  {name: "Rrgbs.led[5].dout", pads: [["RD15", "3"], ["RD16", "1"]]},
  {name: "Rrgbs.led[6].dout", pads: [["RD16", "3"], ["RD17", "1"]]},
  {name: "Rrgbs.led[7].dout", pads: [["RD17", "3"], ["RD18", "1"]]},
  {name: "Rrgbs.led[8].dout", pads: [["RD18", "3"], ["RD19", "1"]]},
  {name: "Rrgbs.dout", pads: [["RD19", "3"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.559055118110236, 3.474015748031496);
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


