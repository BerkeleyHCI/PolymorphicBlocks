const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.327, 3.717), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.366, 3.717), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.327, 3.757), rotate: 0,
  id: 'H3'
})
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(3.766, 1.905), rotate: 0,
  id: 'J1'
})
// usb.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(3.615, 2.160), rotate: 0,
  id: 'R1'
})
// usb.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(3.771, 2.160), rotate: 0,
  id: 'R2'
})
// batt.conn
const J2 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.268, 3.498), rotate: 0,
  id: 'J2'
})
// tp_gnd.tp
const TP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.509, 3.406), rotate: 0,
  id: 'TP1'
})
// fuse.fuse
const F1 = board.add(R_1206_3216Metric, {
  translate: pt(3.235, 3.413), rotate: 0,
  id: 'F1'
})
// gate.pwr_gate.pull_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(2.972, 2.206), rotate: 0,
  id: 'R3'
})
// gate.pwr_gate.pwr_fet
const Q1 = board.add(SOT_23, {
  translate: pt(3.363, 1.807), rotate: 0,
  id: 'Q1'
})
// gate.pwr_gate.amp_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(3.128, 2.206), rotate: 0,
  id: 'R4'
})
// gate.pwr_gate.amp_fet
const Q2 = board.add(SOT_23, {
  translate: pt(2.989, 2.071), rotate: 0,
  id: 'Q2'
})
// gate.pwr_gate.ctl_diode
const D1 = board.add(D_SOD_323, {
  translate: pt(3.167, 2.041), rotate: 0,
  id: 'D1'
})
// gate.pwr_gate.btn_diode
const D2 = board.add(D_SOD_323, {
  translate: pt(3.333, 2.041), rotate: 0,
  id: 'D2'
})
// gate.btn.package
const SW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(3.081, 1.852), rotate: 0,
  id: 'SW1'
})
// prot_batt.diode
const D3 = board.add(D_SMA, {
  translate: pt(2.889, 3.437), rotate: 0,
  id: 'D3'
})
// tp_batt.tp
const TP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.254, 3.406), rotate: 0,
  id: 'TP2'
})
// pwr_or.pdr
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(3.977, 3.044), rotate: 0,
  id: 'R5'
})
// pwr_or.diode
const D4 = board.add(D_SOD_323, {
  translate: pt(3.816, 3.053), rotate: 0,
  id: 'D4'
})
// pwr_or.fet
const Q3 = board.add(SOT_23, {
  translate: pt(3.828, 2.909), rotate: 0,
  id: 'Q3'
})
// reg_3v3.ic
const U1 = board.add(SOT_223_3_TabPin2, {
  translate: pt(1.004, 2.984), rotate: 0,
  id: 'U1'
})
// reg_3v3.in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(1.062, 3.194), rotate: 0,
  id: 'C1'
})
// reg_3v3.out_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(0.898, 3.204), rotate: 0,
  id: 'C2'
})
// prot_3v3.diode
const D5 = board.add(D_SOD_323, {
  translate: pt(3.756, 3.406), rotate: 0,
  id: 'D5'
})
// tp_3v3.tp
const TP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.004, 3.406), rotate: 0,
  id: 'TP3'
})
// charger.ic
const U2 = board.add(SOT_23_5, {
  translate: pt(3.381, 2.909), rotate: 0,
  id: 'U2'
})
// charger.vdd_cap.cap
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(3.568, 2.881), rotate: 0,
  id: 'C3'
})
// charger.vbat_cap.cap
const C4 = board.add(C_0805_2012Metric, {
  translate: pt(3.367, 3.054), rotate: 0,
  id: 'C4'
})
// charger.prog_res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(3.531, 3.044), rotate: 0,
  id: 'R6'
})
// charge_led.package
const D6 = board.add(LED_0603_1608Metric, {
  translate: pt(2.105, 3.397), rotate: 0,
  id: 'D6'
})
// charge_led.res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(2.105, 3.494), rotate: 0,
  id: 'R7'
})
// mcu.ic
const U3 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'U3'
})
// mcu.vcc_cap0.cap
const C5 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.789), rotate: 0,
  id: 'C5'
})
// mcu.vcc_cap1.cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.773), rotate: 0,
  id: 'C6'
})
// mcu.prog.conn
const J3 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.000, 0.370), rotate: 0,
  id: 'J3'
})
// mcu.boot.package
const SW2 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.096, 0.593), rotate: 0,
  id: 'SW2'
})
// mcu.en_pull.rc.r
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.773), rotate: 0,
  id: 'R8'
})
// mcu.en_pull.rc.c
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.903), rotate: 0,
  id: 'C7'
})
// usb_esd
const U4 = board.add(SOT_23, {
  translate: pt(4.514, 3.435), rotate: 0,
  id: 'U4'
})
// led.package
const D7 = board.add(LED_0603_1608Metric, {
  translate: pt(1.870, 3.397), rotate: 0,
  id: 'D7'
})
// led.res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(1.870, 3.494), rotate: 0,
  id: 'R9'
})
// tof.elt[0]
const J4 = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(1.457, 2.309), rotate: 0,
  id: 'J4'
})
// tof.elt[1]
const J5 = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(1.636, 2.309), rotate: 0,
  id: 'J5'
})
// tof.elt[2]
const J6 = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(1.815, 2.309), rotate: 0,
  id: 'J6'
})
// tof.elt[3]
const J7 = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(1.994, 2.309), rotate: 0,
  id: 'J7'
})
// i2c_pull.scl_res.res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(2.574, 3.397), rotate: 0,
  id: 'R10'
})
// i2c_pull.sda_res.res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(2.574, 3.494), rotate: 0,
  id: 'R11'
})
// i2c_tp.tp_scl.tp
const TP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.628, 3.406), rotate: 0,
  id: 'TP4'
})
// i2c_tp.tp_sda.tp
const TP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.628, 3.520), rotate: 0,
  id: 'TP5'
})
// imu.ic
const U5 = board.add(Bosch_LGA_14_3x2_5mm_P0_5mm, {
  translate: pt(0.854, 3.431), rotate: 0,
  id: 'U5'
})
// imu.vdd_cap.cap
const C8 = board.add(C_0603_1608Metric, {
  translate: pt(0.839, 3.563), rotate: 0,
  id: 'C8'
})
// imu.vddio_cap.cap
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(0.995, 3.563), rotate: 0,
  id: 'C9'
})
// mag.ic
const U6 = board.add(LGA_16_3x3mm_P0_5mm, {
  translate: pt(4.222, 2.911), rotate: 0,
  id: 'U6'
})
// mag.vdd_cap.cap
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(4.211, 3.048), rotate: 0,
  id: 'C10'
})
// mag.set_cap
const C11 = board.add(C_0603_1608Metric, {
  translate: pt(4.367, 3.048), rotate: 0,
  id: 'C11'
})
// mag.c1
const C12 = board.add(C_0805_2012Metric, {
  translate: pt(4.397, 2.881), rotate: 0,
  id: 'C12'
})
// expander.ic
const U7 = board.add(TSSOP_16_4_4x5mm_P0_65mm, {
  translate: pt(2.486, 2.951), rotate: 0,
  id: 'U7'
})
// expander.vdd_cap.cap
const C13 = board.add(C_0603_1608Metric, {
  translate: pt(2.393, 3.127), rotate: 0,
  id: 'C13'
})
// rgb.package
const D8 = board.add(LED_D5_0mm_4_RGB_Staggered_Pins, {
  translate: pt(2.796, 3.000), rotate: 0,
  id: 'D8'
})
// rgb.red_res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(3.124, 2.871), rotate: 0,
  id: 'R12'
})
// rgb.green_res
const R13 = board.add(R_0603_1608Metric, {
  translate: pt(3.124, 2.968), rotate: 0,
  id: 'R13'
})
// rgb.blue_res
const R14 = board.add(R_0603_1608Metric, {
  translate: pt(3.124, 3.065), rotate: 0,
  id: 'R14'
})
// oled.device.conn
const J8 = board.add(Hirose_FH12_30S_0_5SH_1x30_1MP_P0_50mm_Horizontal, {
  translate: pt(2.956, 1.054), rotate: 0,
  id: 'J8'
})
// oled.lcd
const U8 = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(3.066, 0.516), rotate: 0,
  id: 'U8'
})
// oled.c1_cap
const C14 = board.add(C_0603_1608Metric, {
  translate: pt(3.815, 0.889), rotate: 0,
  id: 'C14'
})
// oled.c2_cap
const C15 = board.add(C_0603_1608Metric, {
  translate: pt(3.971, 0.889), rotate: 0,
  id: 'C15'
})
// oled.iref_res
const R15 = board.add(R_0603_1608Metric, {
  translate: pt(3.469, 1.006), rotate: 0,
  id: 'R15'
})
// oled.vcomh_cap.cap
const C16 = board.add(C_0805_2012Metric, {
  translate: pt(3.477, 0.899), rotate: 0,
  id: 'C16'
})
// oled.vdd_cap1.cap
const C17 = board.add(C_0603_1608Metric, {
  translate: pt(3.624, 1.006), rotate: 0,
  id: 'C17'
})
// oled.vbat_cap.cap
const C18 = board.add(C_0603_1608Metric, {
  translate: pt(3.780, 1.006), rotate: 0,
  id: 'C18'
})
// oled.vcc_cap.cap
const C19 = board.add(C_0805_2012Metric, {
  translate: pt(3.650, 0.899), rotate: 0,
  id: 'C19'
})
// batt_sense.div.top_res
const R16 = board.add(R_0603_1608Metric, {
  translate: pt(2.340, 3.397), rotate: 0,
  id: 'R16'
})
// batt_sense.div.bottom_res
const R17 = board.add(R_0603_1608Metric, {
  translate: pt(2.340, 3.494), rotate: 0,
  id: 'R17'
})
// servo[0].conn
const J9 = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(2.146, 3.112), rotate: 0,
  id: 'J9'
})
// servo[1].conn
const J10 = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(1.366, 3.112), rotate: 0,
  id: 'J10'
})
// servo[2].conn
const J11 = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(1.886, 3.112), rotate: 0,
  id: 'J11'
})
// servo[3].conn
const J12 = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(1.626, 3.112), rotate: 0,
  id: 'J12'
})
// npx.led[0]
const D9 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 1.848), rotate: 0,
  id: 'D9'
})
// npx.led[1]
const D10 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 1.848), rotate: 0,
  id: 'D10'
})
// npx.led[2]
const D11 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 1.848), rotate: 0,
  id: 'D11'
})
// npx.led[3]
const D12 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 1.848), rotate: 0,
  id: 'D12'
})
// npx.led[4]
const D13 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.104), rotate: 0,
  id: 'D13'
})
// npx.led[5]
const D14 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.104), rotate: 0,
  id: 'D14'
})
// npx.led[6]
const D15 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.104), rotate: 0,
  id: 'D15'
})
// npx.led[7]
const D16 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.104), rotate: 0,
  id: 'D16'
})
// npx.led[8]
const D17 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.360), rotate: 0,
  id: 'D17'
})
// npx.led[9]
const D18 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.360), rotate: 0,
  id: 'D18'
})
// npx.led[10]
const D19 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.360), rotate: 0,
  id: 'D19'
})
// npx.led[11]
const D20 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.360), rotate: 0,
  id: 'D20'
})
// npx.led[12]
const D21 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.616), rotate: 0,
  id: 'D21'
})
// npx.led[13]
const D22 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.616), rotate: 0,
  id: 'D22'
})
// npx.led[14]
const D23 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.616), rotate: 0,
  id: 'D23'
})
// npx.led[15]
const D24 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.616), rotate: 0,
  id: 'D24'
})
// npx_key
const D25 = board.add(LED_SK6812MINI_E, {
  translate: pt(0.144, 3.782), rotate: 0,
  id: 'D25'
})
// reg_2v5.ic
const U9 = board.add(SOT_23, {
  translate: pt(0.466, 3.435), rotate: 0,
  id: 'U9'
})
// reg_2v5.in_cap.cap
const C20 = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 3.570), rotate: 0,
  id: 'C20'
})
// reg_2v5.out_cap.cap
const C21 = board.add(C_0603_1608Metric, {
  translate: pt(0.605, 3.570), rotate: 0,
  id: 'C21'
})
// reg_1v2.ic
const U10 = board.add(SOT_23, {
  translate: pt(0.076, 3.435), rotate: 0,
  id: 'U10'
})
// reg_1v2.in_cap.cap
const C22 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 3.570), rotate: 0,
  id: 'C22'
})
// reg_1v2.out_cap.cap
const C23 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 3.570), rotate: 0,
  id: 'C23'
})
// cam.device.conn
const J13 = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(0.356, 3.035), rotate: 0,
  id: 'J13'
})
// cam.dovdd_cap.cap
const C24 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 3.222), rotate: 0,
  id: 'C24'
})
// cam.reset_cap
const C25 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 3.222), rotate: 0,
  id: 'C25'
})
// cam.pclk_cap
const C26 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 3.222), rotate: 0,
  id: 'C26'
})
// cam.reset_pull.res
const R18 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 3.222), rotate: 0,
  id: 'R18'
})
// switch.package
const SW3 = board.add(SW_Hotswap_Kailh_MX, {
  translate: pt(2.488, 2.026), rotate: 0,
  id: 'SW3'
})

board.setNetlist([
  {name: "vusb", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["R5", "1"], ["D4", "2"], ["Q3", "1"], ["U2", "4"], ["D6", "2"], ["C3", "1"]]},
  {name: "gnd", pads: [["U4", "3"], ["D25", "3"], ["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["J2", "1"], ["TP1", "1"], ["D3", "2"], ["R5", "2"], ["U1", "1"], ["D5", "2"], ["U2", "2"], ["U3", "1"], ["U3", "40"], ["U3", "41"], ["R9", "2"], ["J4", "2"], ["J5", "2"], ["J6", "2"], ["J7", "2"], ["U5", "1"], ["U5", "2"], ["U5", "3"], ["U5", "6"], ["U5", "7"], ["U6", "9"], ["U6", "11"], ["U7", "1"], ["U7", "2"], ["U7", "3"], ["U7", "8"], ["J9", "3"], ["J10", "3"], ["J11", "3"], ["J12", "3"], ["D9", "3"], ["D10", "3"], ["D11", "3"], ["D12", "3"], ["D13", "3"], ["D14", "3"], ["D15", "3"], ["D16", "3"], ["D17", "3"], ["D18", "3"], ["D19", "3"], ["D20", "3"], ["D21", "3"], ["D22", "3"], ["D23", "3"], ["D24", "3"], ["U9", "1"], ["U10", "1"], ["SW3", "2"], ["R17", "2"], ["J1", "S1"], ["R6", "2"], ["C12", "2"], ["R15", "2"], ["C25", "2"], ["C26", "2"], ["R4", "1"], ["Q2", "2"], ["SW1", "2"], ["C1", "2"], ["C2", "2"], ["C3", "2"], ["C4", "2"], ["C5", "2"], ["C6", "2"], ["J3", "4"], ["SW2", "2"], ["C8", "2"], ["C9", "2"], ["C10", "2"], ["C13", "2"], ["C16", "2"], ["C17", "2"], ["C18", "2"], ["C19", "2"], ["C20", "2"], ["C21", "2"], ["C22", "2"], ["C23", "2"], ["J13", "10"], ["J13", "23"], ["C24", "2"], ["C7", "2"], ["R1", "1"], ["R2", "1"], ["J8", "8"], ["J8", "1"], ["J8", "30"], ["J8", "29"], ["J8", "17"], ["J8", "16"], ["J8", "21"], ["J8", "22"], ["J8", "23"], ["J8", "24"], ["J8", "25"], ["J8", "12"], ["J8", "10"], ["J8", "15"], ["J8", "13"], ["J13", "17"]]},
  {name: "vbatt", pads: [["D25", "1"], ["Q1", "3"], ["D3", "1"], ["TP2", "1"], ["Q3", "3"], ["J9", "2"], ["J10", "2"], ["J11", "2"], ["J12", "2"], ["D9", "1"], ["D10", "1"], ["D11", "1"], ["D12", "1"], ["D13", "1"], ["D14", "1"], ["D15", "1"], ["D16", "1"], ["D17", "1"], ["D18", "1"], ["D19", "1"], ["D20", "1"], ["D21", "1"], ["D22", "1"], ["D23", "1"], ["D24", "1"], ["R16", "1"]]},
  {name: "pwr", pads: [["Q3", "2"], ["D4", "1"], ["U1", "3"], ["U9", "3"], ["U10", "3"], ["C1", "1"], ["C20", "1"], ["C22", "1"]]},
  {name: "v3v3", pads: [["U1", "2"], ["D5", "1"], ["TP3", "1"], ["U3", "2"], ["J4", "1"], ["J5", "1"], ["J6", "1"], ["J7", "1"], ["U5", "5"], ["U5", "12"], ["U5", "8"], ["U6", "2"], ["U6", "4"], ["U6", "13"], ["U7", "16"], ["D8", "2"], ["C2", "1"], ["C5", "1"], ["C6", "1"], ["J3", "1"], ["J4", "6"], ["R10", "1"], ["R11", "1"], ["C9", "1"], ["C8", "1"], ["C10", "1"], ["C13", "1"], ["J8", "9"], ["J8", "6"], ["C17", "1"], ["C18", "1"], ["J13", "14"], ["C24", "1"], ["R18", "1"], ["R8", "1"], ["J8", "11"]]},
  {name: "v2v5", pads: [["U9", "2"], ["J13", "21"], ["C21", "1"]]},
  {name: "v1v2", pads: [["U10", "2"], ["J13", "15"], ["C23", "1"]]},
  {name: "batt.pwr", pads: [["J2", "2"], ["F1", "1"], ["U2", "3"], ["C4", "1"]]},
  {name: "fuse.pwr_out", pads: [["F1", "2"], ["R3", "1"], ["Q1", "2"]]},
  {name: "charge_led.signal", pads: [["U2", "1"], ["R7", "2"]]},
  {name: "usb_chain_0.d_P", pads: [["J1", "A6"], ["J1", "B6"], ["U4", "2"], ["U3", "14"]]},
  {name: "usb_chain_0.d_N", pads: [["J1", "A7"], ["J1", "B7"], ["U4", "1"], ["U3", "13"]]},
  {name: "mcu.program_boot_node", pads: [["U3", "27"], ["D7", "2"], ["SW2", "1"]]},
  {name: "touch_0", pads: [["U3", "7"]]},
  {name: "i2c_chain_0.scl", pads: [["U3", "38"], ["U5", "13"], ["U6", "1"], ["U7", "14"], ["R10", "2"], ["TP4", "1"], ["J8", "18"], ["J4", "3"], ["J5", "3"], ["J6", "3"], ["J7", "3"], ["J13", "20"]]},
  {name: "i2c_chain_0.sda", pads: [["U3", "4"], ["U5", "14"], ["U6", "16"], ["U7", "15"], ["R11", "2"], ["J13", "22"], ["J4", "4"], ["J5", "4"], ["J6", "4"], ["J7", "4"], ["TP5", "1"], ["J8", "19"], ["J8", "20"]]},
  {name: "expander.io.tof_reset_1", pads: [["U7", "4"], ["J5", "6"]]},
  {name: "expander.io.tof_reset_2", pads: [["U7", "5"], ["J6", "6"]]},
  {name: "expander.io.tof_reset_3", pads: [["U7", "6"], ["J7", "6"]]},
  {name: "expander.io.rgb_red", pads: [["U7", "7"], ["R12", "2"]]},
  {name: "expander.io.rgb_green", pads: [["U7", "9"], ["R13", "2"]]},
  {name: "expander.io.rgb_blue", pads: [["U7", "10"], ["R14", "2"]]},
  {name: "oled.reset", pads: [["U3", "31"], ["J8", "14"]]},
  {name: "batt_sense.output", pads: [["U3", "39"], ["R16", "2"], ["R17", "1"]]},
  {name: "gate.btn_out", pads: [["U3", "32"], ["D2", "2"]]},
  {name: "gate.control", pads: [["U3", "33"], ["R4", "2"], ["Q2", "1"]]},
  {name: "servo[0].pwm", pads: [["U3", "5"], ["J9", "1"]]},
  {name: "servo[1].pwm", pads: [["U3", "6"], ["J10", "1"]]},
  {name: "servo[2].pwm", pads: [["U3", "8"], ["J11", "1"]]},
  {name: "servo[3].pwm", pads: [["U3", "10"], ["J12", "1"]]},
  {name: "npx.din", pads: [["U3", "9"], ["D9", "4"]]},
  {name: "npx.dout", pads: [["D24", "2"], ["D25", "4"]]},
  {name: "cam.dvp8.xclk", pads: [["U3", "17"], ["J13", "12"]]},
  {name: "cam.dvp8.pclk", pads: [["U3", "20"], ["C26", "1"], ["J13", "8"]]},
  {name: "cam.dvp8.href", pads: [["U3", "12"], ["J13", "16"]]},
  {name: "cam.dvp8.vsync", pads: [["U3", "11"], ["J13", "18"]]},
  {name: "cam.dvp8.y0", pads: [["U3", "22"], ["J13", "6"]]},
  {name: "cam.dvp8.y1", pads: [["U3", "24"], ["J13", "4"]]},
  {name: "cam.dvp8.y2", pads: [["U3", "25"], ["J13", "3"]]},
  {name: "cam.dvp8.y3", pads: [["U3", "23"], ["J13", "5"]]},
  {name: "cam.dvp8.y4", pads: [["U3", "21"], ["J13", "7"]]},
  {name: "cam.dvp8.y5", pads: [["U3", "19"], ["J13", "9"]]},
  {name: "cam.dvp8.y6", pads: [["U3", "18"], ["J13", "11"]]},
  {name: "cam.dvp8.y7", pads: [["U3", "15"], ["J13", "13"]]},
  {name: "switch.out", pads: [["U3", "34"], ["SW3", "1"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "gate.pwr_gate.btn_in", pads: [["D2", "1"], ["D1", "1"], ["SW1", "1"]]},
  {name: "gate.pwr_gate.pull_res.b", pads: [["R3", "2"], ["D1", "2"], ["Q1", "1"], ["Q2", "3"]]},
  {name: "charger.prog_res.a", pads: [["R6", "1"], ["U2", "5"]]},
  {name: "charge_led.res.a", pads: [["R7", "1"], ["D6", "1"]]},
  {name: "mcu.program_uart_node.a_tx", pads: [["U3", "37"], ["J3", "2"]]},
  {name: "mcu.program_uart_node.b_tx", pads: [["U3", "36"], ["J3", "3"]]},
  {name: "mcu.program_en_node", pads: [["U3", "3"], ["R8", "2"], ["C7", "1"]]},
  {name: "led.res.a", pads: [["R9", "1"], ["D7", "1"]]},
  {name: "tof.elt[0].ic.gpio1", pads: [["J4", "5"]]},
  {name: "tof.elt[1].ic.gpio1", pads: [["J5", "5"]]},
  {name: "tof.elt[2].ic.gpio1", pads: [["J6", "5"]]},
  {name: "tof.elt[3].ic.gpio1", pads: [["J7", "5"]]},
  {name: "imu.int1", pads: [["U5", "4"]]},
  {name: "imu.int2", pads: [["U5", "9"]]},
  {name: "mag.drdy", pads: [["U6", "15"]]},
  {name: "mag.set_cap.pos", pads: [["C11", "1"], ["U6", "8"]]},
  {name: "mag.set_cap.neg", pads: [["C11", "2"], ["U6", "12"]]},
  {name: "mag.c1.pos", pads: [["C12", "1"], ["U6", "10"]]},
  {name: "rgb.red_res.a", pads: [["R12", "1"], ["D8", "1"]]},
  {name: "rgb.green_res.a", pads: [["R13", "1"], ["D8", "3"]]},
  {name: "rgb.blue_res.a", pads: [["R14", "1"], ["D8", "4"]]},
  {name: "oled.c1_cap.pos", pads: [["C14", "1"], ["J8", "4"]]},
  {name: "oled.c1_cap.neg", pads: [["C14", "2"], ["J8", "5"]]},
  {name: "oled.c2_cap.pos", pads: [["C15", "1"], ["J8", "2"]]},
  {name: "oled.c2_cap.neg", pads: [["C15", "2"], ["J8", "3"]]},
  {name: "oled.iref_res.a", pads: [["R15", "1"], ["J8", "26"]]},
  {name: "oled.device.vcomh", pads: [["J8", "27"], ["C16", "1"]]},
  {name: "oled.device.vcc", pads: [["J8", "28"], ["C19", "1"]]},
  {name: "npx.led[0].dout", pads: [["D9", "2"], ["D10", "4"]]},
  {name: "npx.led[1].dout", pads: [["D10", "2"], ["D11", "4"]]},
  {name: "npx.led[2].dout", pads: [["D11", "2"], ["D12", "4"]]},
  {name: "npx.led[3].dout", pads: [["D12", "2"], ["D13", "4"]]},
  {name: "npx.led[4].dout", pads: [["D13", "2"], ["D14", "4"]]},
  {name: "npx.led[5].dout", pads: [["D14", "2"], ["D15", "4"]]},
  {name: "npx.led[6].dout", pads: [["D15", "2"], ["D16", "4"]]},
  {name: "npx.led[7].dout", pads: [["D16", "2"], ["D17", "4"]]},
  {name: "npx.led[8].dout", pads: [["D17", "2"], ["D18", "4"]]},
  {name: "npx.led[9].dout", pads: [["D18", "2"], ["D19", "4"]]},
  {name: "npx.led[10].dout", pads: [["D19", "2"], ["D20", "4"]]},
  {name: "npx.led[11].dout", pads: [["D20", "2"], ["D21", "4"]]},
  {name: "npx.led[12].dout", pads: [["D21", "2"], ["D22", "4"]]},
  {name: "npx.led[13].dout", pads: [["D22", "2"], ["D23", "4"]]},
  {name: "npx.led[14].dout", pads: [["D23", "2"], ["D24", "4"]]},
  {name: "npx_key.dout", pads: [["D25", "2"]]},
  {name: "cam.reset_cap.pos", pads: [["C25", "1"], ["R18", "2"], ["J13", "19"]]},
  {name: "cam.device.y.0", pads: [["J13", "1"]]},
  {name: "cam.device.y.1", pads: [["J13", "2"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.6287401574803155, 3.8866141732283466);
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


