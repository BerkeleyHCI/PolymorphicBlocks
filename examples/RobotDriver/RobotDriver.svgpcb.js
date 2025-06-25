const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.673, 3.040), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.713, 3.040), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.673, 3.079), rotate: 0,
  id: 'H3'
})
// batt.conn
const J1 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.615, 2.719), rotate: 0,
  id: 'J1'
})
// isense.sense.res.res
const R1 = board.add(R_2512_6332Metric, {
  translate: pt(2.693, 1.818), rotate: 0,
  id: 'R1'
})
// isense.amp.amp.ic
const U1 = board.add(SOT_23_5, {
  translate: pt(2.963, 1.809), rotate: 0,
  id: 'U1'
})
// isense.amp.amp.vdd_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(2.600, 1.961), rotate: 0,
  id: 'C1'
})
// isense.amp.r1
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(2.756, 1.961), rotate: 0,
  id: 'R2'
})
// isense.amp.r2
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(2.912, 1.961), rotate: 0,
  id: 'R3'
})
// isense.amp.rf
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(2.600, 2.058), rotate: 0,
  id: 'R4'
})
// isense.amp.rg
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(2.756, 2.058), rotate: 0,
  id: 'R5'
})
// tp_vbatt.tp
const TP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.332, 3.077), rotate: 0,
  id: 'TP1'
})
// tp_gnd.tp
const TP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.582, 3.077), rotate: 0,
  id: 'TP2'
})
// reg_3v3.ic
const U2 = board.add(SOT_23_5, {
  translate: pt(2.170, 1.809), rotate: 0,
  id: 'U2'
})
// reg_3v3.fb.div.top_res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(2.321, 1.944), rotate: 0,
  id: 'R6'
})
// reg_3v3.fb.div.bottom_res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(2.148, 2.061), rotate: 0,
  id: 'R7'
})
// reg_3v3.power_path.inductor
const L1 = board.add(L_0603_1608Metric, {
  translate: pt(2.304, 2.061), rotate: 0,
  id: 'L1'
})
// reg_3v3.power_path.in_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(2.357, 1.781), rotate: 0,
  id: 'C2'
})
// reg_3v3.power_path.out_cap.cap
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(2.156, 1.954), rotate: 0,
  id: 'C3'
})
// tp_3v3.tp
const TP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.833, 3.077), rotate: 0,
  id: 'TP3'
})
// prot_3v3.diode
const D1 = board.add(D_SOD_323, {
  translate: pt(2.080, 3.077), rotate: 0,
  id: 'D1'
})
// mcu.ic
const U3 = board.add(ESP32_WROOM_32, {
  translate: pt(0.945, 0.414), rotate: 0,
  id: 'U3'
})
// mcu.vcc_cap0.cap
const C4 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.789), rotate: 0,
  id: 'C4'
})
// mcu.vcc_cap1.cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.773), rotate: 0,
  id: 'C5'
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
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.773), rotate: 0,
  id: 'R8'
})
// mcu.en_pull.rc.c
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.903), rotate: 0,
  id: 'C6'
})
// tof.elt[0]
const J3 = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(0.803, 2.311), rotate: 0,
  id: 'J3'
})
// tof.elt[1]
const J4 = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(0.982, 2.311), rotate: 0,
  id: 'J4'
})
// tof.elt[2]
const J5 = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(1.161, 2.311), rotate: 0,
  id: 'J5'
})
// i2c_pull.scl_res.res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(1.089, 3.069), rotate: 0,
  id: 'R9'
})
// i2c_pull.sda_res.res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(1.089, 3.165), rotate: 0,
  id: 'R10'
})
// i2c_tp.tp_scl.tp
const TP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.456, 3.077), rotate: 0,
  id: 'TP4'
})
// i2c_tp.tp_sda.tp
const TP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.456, 3.191), rotate: 0,
  id: 'TP5'
})
// lcd.device.conn
const J6 = board.add(Hirose_FH12_15S_0_5SH_1x15_1MP_P0_50mm_Horizontal, {
  translate: pt(2.808, 0.685), rotate: 0,
  id: 'J6'
})
// lcd.lcd
const U4 = board.add(Lcd_Er_Oled0_91_3_Outline, {
  translate: pt(3.064, 0.260), rotate: 0,
  id: 'U4'
})
// lcd.c1_cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(3.693, 0.521), rotate: 0,
  id: 'C7'
})
// lcd.c2_cap
const C8 = board.add(C_0603_1608Metric, {
  translate: pt(3.173, 0.637), rotate: 0,
  id: 'C8'
})
// lcd.iref_res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(3.329, 0.637), rotate: 0,
  id: 'R11'
})
// lcd.vcomh_cap.cap
const C9 = board.add(C_0805_2012Metric, {
  translate: pt(3.182, 0.531), rotate: 0,
  id: 'C9'
})
// lcd.vdd_cap1.cap
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(3.485, 0.637), rotate: 0,
  id: 'C10'
})
// lcd.vdd_cap2.cap
const C11 = board.add(C_0805_2012Metric, {
  translate: pt(3.355, 0.531), rotate: 0,
  id: 'C11'
})
// lcd.vcc_cap1.cap
const C12 = board.add(C_0603_1608Metric, {
  translate: pt(3.641, 0.637), rotate: 0,
  id: 'C12'
})
// lcd.vcc_cap2.cap
const C13 = board.add(C_0805_2012Metric, {
  translate: pt(3.528, 0.531), rotate: 0,
  id: 'C13'
})
// imu.ic
const U5 = board.add(Bosch_LGA_14_3x2_5mm_P0_5mm, {
  translate: pt(1.200, 2.652), rotate: 0,
  id: 'U5'
})
// imu.vdd_cap.cap
const C14 = board.add(C_0603_1608Metric, {
  translate: pt(1.186, 2.783), rotate: 0,
  id: 'C14'
})
// imu.vddio_cap.cap
const C15 = board.add(C_0603_1608Metric, {
  translate: pt(1.342, 2.783), rotate: 0,
  id: 'C15'
})
// expander.ic
const U6 = board.add(SOIC_16W_7_5x10_3mm_P1_27mm, {
  translate: pt(1.582, 1.955), rotate: 0,
  id: 'U6'
})
// expander.vdd_cap.cap
const C16 = board.add(C_0603_1608Metric, {
  translate: pt(1.913, 1.771), rotate: 0,
  id: 'C16'
})
// leds.led[0].package
const D2 = board.add(LED_0603_1608Metric, {
  translate: pt(0.699, 3.069), rotate: 0,
  id: 'D2'
})
// leds.led[1].package
const D3 = board.add(LED_0603_1608Metric, {
  translate: pt(0.855, 3.069), rotate: 0,
  id: 'D3'
})
// leds.led[2].package
const D4 = board.add(LED_0603_1608Metric, {
  translate: pt(0.699, 3.166), rotate: 0,
  id: 'D4'
})
// leds.led[3].package
const D5 = board.add(LED_0603_1608Metric, {
  translate: pt(0.855, 3.166), rotate: 0,
  id: 'D5'
})
// spk_tp.tp
const TP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.328, 3.077), rotate: 0,
  id: 'TP6'
})
// spk_drv.ic
const U7 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(0.704, 2.657), rotate: 0,
  id: 'U7'
})
// spk_drv.pwr_cap.cap
const C17 = board.add(C_0603_1608Metric, {
  translate: pt(0.639, 2.794), rotate: 0,
  id: 'C17'
})
// spk_drv.bulk_cap.cap
const C18 = board.add(C_0805_2012Metric, {
  translate: pt(0.933, 2.627), rotate: 0,
  id: 'C18'
})
// spk_drv.inp_res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(0.795, 2.794), rotate: 0,
  id: 'R12'
})
// spk_drv.inp_cap
const C19 = board.add(C_0603_1608Metric, {
  translate: pt(0.951, 2.794), rotate: 0,
  id: 'C19'
})
// spk_drv.inn_res
const R13 = board.add(R_0603_1608Metric, {
  translate: pt(0.639, 2.891), rotate: 0,
  id: 'R13'
})
// spk_drv.inn_cap
const C20 = board.add(C_0603_1608Metric, {
  translate: pt(0.795, 2.891), rotate: 0,
  id: 'C20'
})
// spk.conn
const J7 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.004, 2.719), rotate: 0,
  id: 'J7'
})
// ws2812bArray.led[0]
const D6 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 1.850), rotate: 0,
  id: 'D6'
})
// ws2812bArray.led[1]
const D7 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 1.850), rotate: 0,
  id: 'D7'
})
// ws2812bArray.led[2]
const D8 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.106), rotate: 0,
  id: 'D8'
})
// ws2812bArray.led[3]
const D9 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.106), rotate: 0,
  id: 'D9'
})
// ws2812bArray.led[4]
const D10 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.362), rotate: 0,
  id: 'D10'
})
// led_pixel.conn
const J8 = board.add(JST_PH_B3B_PH_K_1x03_P2_00mm_Vertical, {
  translate: pt(2.394, 2.719), rotate: 0,
  id: 'J8'
})
// motor_driver1.ic
const U8 = board.add(TSSOP_16_1EP_4_4x5mm_P0_65mm_EP3x3mm_ThermalVias, {
  translate: pt(3.575, 1.850), rotate: 0,
  id: 'U8'
})
// motor_driver1.vm_cap.cap
const C21 = board.add(C_0805_2012Metric, {
  translate: pt(3.489, 2.037), rotate: 0,
  id: 'C21'
})
// motor_driver1.vint_cap.cap
const C22 = board.add(C_0805_2012Metric, {
  translate: pt(3.662, 2.037), rotate: 0,
  id: 'C22'
})
// motor_driver1.vcp_cap
const C23 = board.add(C_0603_1608Metric, {
  translate: pt(3.826, 2.027), rotate: 0,
  id: 'C23'
})
// m1_a.conn
const J9 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.863, 2.719), rotate: 0,
  id: 'J9'
})
// m1_b.conn
const J10 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(3.252, 2.719), rotate: 0,
  id: 'J10'
})
// motor_driver2.ic
const U9 = board.add(TSSOP_16_1EP_4_4x5mm_P0_65mm_EP3x3mm_ThermalVias, {
  translate: pt(0.154, 2.697), rotate: 0,
  id: 'U9'
})
// motor_driver2.vm_cap.cap
const C24 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 2.883), rotate: 0,
  id: 'C24'
})
// motor_driver2.vint_cap.cap
const C25 = board.add(C_0805_2012Metric, {
  translate: pt(0.240, 2.883), rotate: 0,
  id: 'C25'
})
// motor_driver2.vcp_cap
const C26 = board.add(C_0603_1608Metric, {
  translate: pt(0.405, 2.873), rotate: 0,
  id: 'C26'
})
// m2_a.conn
const J11 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(3.642, 2.719), rotate: 0,
  id: 'J11'
})
// m2_b.conn
const J12 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.096, 3.170), rotate: 0,
  id: 'J12'
})
// servo.conn
const J13 = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(3.233, 2.012), rotate: 0,
  id: 'J13'
})
// led_res
const RN1 = board.add(R_Array_Concave_4x0603, {
  translate: pt(2.573, 3.113), rotate: 0,
  id: 'RN1'
})

board.setNetlist([
  {name: "vbatt", pads: [["TP1", "1"], ["U2", "4"], ["U7", "1"], ["U7", "6"], ["D6", "1"], ["D7", "1"], ["D8", "1"], ["D9", "1"], ["D10", "1"], ["J8", "1"], ["U8", "12"], ["U9", "12"], ["U8", "1"], ["U9", "1"], ["J13", "2"], ["R1", "2"], ["U2", "1"], ["C23", "2"], ["C26", "2"], ["C17", "1"], ["C18", "1"], ["C21", "1"], ["C24", "1"], ["C2", "1"], ["R2", "1"]]},
  {name: "gnd", pads: [["J1", "1"], ["TP2", "1"], ["U2", "2"], ["D1", "2"], ["U3", "1"], ["U3", "15"], ["U3", "38"], ["U3", "39"], ["J3", "2"], ["J4", "2"], ["J5", "2"], ["U5", "1"], ["U5", "2"], ["U5", "3"], ["U5", "6"], ["U5", "7"], ["U6", "1"], ["U6", "2"], ["U6", "3"], ["U6", "8"], ["U7", "7"], ["U7", "9"], ["D6", "3"], ["D7", "3"], ["D8", "3"], ["D9", "3"], ["D10", "3"], ["J8", "3"], ["U8", "3"], ["U8", "6"], ["U8", "13"], ["U8", "17"], ["U9", "3"], ["U9", "6"], ["U9", "13"], ["U9", "17"], ["J13", "3"], ["U1", "2"], ["R11", "2"], ["C20", "2"], ["C4", "2"], ["C5", "2"], ["J2", "4"], ["SW1", "2"], ["J6", "6"], ["C9", "2"], ["C10", "2"], ["C11", "2"], ["C12", "2"], ["C13", "2"], ["C14", "2"], ["C15", "2"], ["R5", "1"], ["C16", "2"], ["C17", "2"], ["C18", "2"], ["C21", "2"], ["C22", "2"], ["C24", "2"], ["C25", "2"], ["R7", "2"], ["C6", "2"], ["C1", "2"], ["C2", "2"], ["C3", "2"]]},
  {name: "v3v3", pads: [["TP3", "1"], ["D1", "1"], ["U3", "2"], ["J3", "1"], ["J4", "1"], ["J5", "1"], ["U5", "5"], ["U5", "12"], ["U5", "8"], ["U6", "16"], ["U1", "5"], ["R6", "1"], ["C4", "1"], ["C5", "1"], ["J2", "1"], ["R9", "1"], ["R10", "1"], ["J6", "7"], ["J6", "5"], ["C10", "1"], ["C11", "1"], ["C15", "1"], ["C14", "1"], ["C16", "1"], ["D2", "2"], ["D3", "2"], ["D4", "2"], ["D5", "2"], ["R8", "1"], ["C1", "1"], ["L1", "2"], ["C3", "1"]]},
  {name: "isense.pwr_in", pads: [["J1", "2"], ["R1", "1"], ["R3", "1"]]},
  {name: "i2c_chain_0.scl", pads: [["U3", "16"], ["U5", "13"], ["U6", "14"], ["R9", "2"], ["TP4", "1"], ["J3", "3"], ["J4", "3"], ["J5", "3"]]},
  {name: "i2c_chain_0.sda", pads: [["U3", "14"], ["U5", "14"], ["U6", "15"], ["R10", "2"], ["J3", "4"], ["J4", "4"], ["J5", "4"], ["TP5", "1"]]},
  {name: "lcd.spi.sck", pads: [["U3", "9"], ["J6", "11"]]},
  {name: "lcd.spi.mosi", pads: [["U3", "8"], ["J6", "12"]]},
  {name: "lcd.cs", pads: [["U3", "13"], ["J6", "8"]]},
  {name: "lcd.reset", pads: [["U3", "12"], ["J6", "9"]]},
  {name: "lcd.dc", pads: [["U3", "10"], ["J6", "10"]]},
  {name: "isense.out", pads: [["U3", "4"], ["R4", "1"], ["U1", "4"]]},
  {name: "expander.io.tof_reset_0", pads: [["U6", "10"], ["J3", "6"]]},
  {name: "expander.io.tof_reset_1", pads: [["U6", "11"], ["J4", "6"]]},
  {name: "expander.io.tof_reset_2", pads: [["U6", "12"], ["J5", "6"]]},
  {name: "expander.io.led_0", pads: [["U6", "4"], ["RN1", "8"]]},
  {name: "expander.io.led_1", pads: [["U6", "5"], ["RN1", "7"]]},
  {name: "expander.io.led_2", pads: [["U6", "6"], ["RN1", "6"]]},
  {name: "expander.io.led_3", pads: [["U6", "7"], ["RN1", "5"]]},
  {name: "spk_chain_0", pads: [["U3", "11"], ["TP6", "1"], ["C19", "2"]]},
  {name: "spk_chain_1.a", pads: [["U7", "8"], ["J7", "1"]]},
  {name: "spk_chain_1.b", pads: [["U7", "5"], ["J7", "2"]]},
  {name: "ws2812bArray.din", pads: [["U3", "23"], ["D6", "4"]]},
  {name: "ws2812bArray.dout", pads: [["D10", "2"], ["J8", "2"]]},
  {name: "motor_driver1.ain1", pads: [["U3", "30"], ["U8", "16"]]},
  {name: "motor_driver1.ain2", pads: [["U3", "31"], ["U8", "15"]]},
  {name: "motor_driver1.bin1", pads: [["U3", "36"], ["U8", "9"]]},
  {name: "motor_driver1.bin2", pads: [["U3", "33"], ["U8", "10"]]},
  {name: "m1_a.a", pads: [["U8", "2"], ["J9", "2"]]},
  {name: "m1_a.b", pads: [["U8", "4"], ["J9", "1"]]},
  {name: "m1_b.a", pads: [["U8", "7"], ["J10", "2"]]},
  {name: "m1_b.b", pads: [["U8", "5"], ["J10", "1"]]},
  {name: "motor_driver2.ain1", pads: [["U3", "26"], ["U9", "16"]]},
  {name: "motor_driver2.ain2", pads: [["U3", "27"], ["U9", "15"]]},
  {name: "motor_driver2.bin1", pads: [["U3", "29"], ["U9", "9"]]},
  {name: "motor_driver2.bin2", pads: [["U3", "28"], ["U9", "10"]]},
  {name: "m2_a.a", pads: [["U9", "2"], ["J11", "2"]]},
  {name: "m2_a.b", pads: [["U9", "4"], ["J11", "1"]]},
  {name: "m2_b.a", pads: [["U9", "7"], ["J12", "2"]]},
  {name: "m2_b.b", pads: [["U9", "5"], ["J12", "1"]]},
  {name: "servo.pwm", pads: [["U3", "37"], ["J13", "1"]]},
  {name: "led_res.a.0", pads: [["RN1", "1"], ["D2", "1"]]},
  {name: "led_res.a.1", pads: [["RN1", "2"], ["D3", "1"]]},
  {name: "led_res.a.2", pads: [["RN1", "3"], ["D4", "1"]]},
  {name: "led_res.a.3", pads: [["RN1", "4"], ["D5", "1"]]},
  {name: "isense.amp.r2.b", pads: [["R3", "2"], ["U1", "1"], ["R5", "2"]]},
  {name: "isense.amp.r1.b", pads: [["R2", "2"], ["U1", "3"], ["R4", "2"]]},
  {name: "reg_3v3.fb.output", pads: [["U2", "5"], ["R6", "2"], ["R7", "1"]]},
  {name: "reg_3v3.power_path.switch", pads: [["U2", "3"], ["L1", "1"]]},
  {name: "mcu.program_uart_node.a_tx", pads: [["U3", "35"], ["J2", "2"]]},
  {name: "mcu.program_uart_node.b_tx", pads: [["U3", "34"], ["J2", "3"]]},
  {name: "mcu.program_en_node", pads: [["U3", "3"], ["R8", "2"], ["C6", "1"]]},
  {name: "mcu.program_boot_node", pads: [["U3", "25"], ["SW1", "1"]]},
  {name: "mcu.ic.io2", pads: [["U3", "24"]]},
  {name: "tof.elt[0].ic.gpio1", pads: [["J3", "5"]]},
  {name: "tof.elt[1].ic.gpio1", pads: [["J4", "5"]]},
  {name: "tof.elt[2].ic.gpio1", pads: [["J5", "5"]]},
  {name: "lcd.c1_cap.pos", pads: [["C7", "1"], ["J6", "3"]]},
  {name: "lcd.c1_cap.neg", pads: [["C7", "2"], ["J6", "4"]]},
  {name: "lcd.c2_cap.pos", pads: [["C8", "1"], ["J6", "1"]]},
  {name: "lcd.c2_cap.neg", pads: [["C8", "2"], ["J6", "2"]]},
  {name: "lcd.iref_res.a", pads: [["R11", "1"], ["J6", "13"]]},
  {name: "lcd.device.vcomh", pads: [["J6", "14"], ["C9", "1"]]},
  {name: "lcd.device.vcc", pads: [["J6", "15"], ["C12", "1"], ["C13", "1"]]},
  {name: "imu.int1", pads: [["U5", "4"]]},
  {name: "imu.int2", pads: [["U5", "9"]]},
  {name: "spk_drv.inp_cap.pos", pads: [["C19", "1"], ["R12", "1"]]},
  {name: "spk_drv.inp_res.b", pads: [["R12", "2"], ["U7", "4"]]},
  {name: "spk_drv.inn_cap.pos", pads: [["C20", "1"], ["R13", "1"]]},
  {name: "spk_drv.inn_res.b", pads: [["R13", "2"], ["U7", "3"]]},
  {name: "ws2812bArray.led[0].dout", pads: [["D6", "2"], ["D7", "4"]]},
  {name: "ws2812bArray.led[1].dout", pads: [["D7", "2"], ["D8", "4"]]},
  {name: "ws2812bArray.led[2].dout", pads: [["D8", "2"], ["D9", "4"]]},
  {name: "ws2812bArray.led[3].dout", pads: [["D9", "2"], ["D10", "4"]]},
  {name: "motor_driver1.ic.vint", pads: [["U8", "14"], ["C22", "1"]]},
  {name: "motor_driver1.vcp_cap.pos", pads: [["C23", "1"], ["U8", "11"]]},
  {name: "motor_driver2.ic.vint", pads: [["U9", "14"], ["C25", "1"]]},
  {name: "motor_driver2.vcp_cap.pos", pads: [["C26", "1"], ["U9", "11"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.002755905511811, 3.374409448818898);
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


