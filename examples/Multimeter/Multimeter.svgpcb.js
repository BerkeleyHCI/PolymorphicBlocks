const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.913, 2.557), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.952, 2.557), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.913, 2.597), rotate: 0,
  id: 'H3'
})
// bat
const U1 = board.add(BatteryHolder_Keystone_2460_1xAA, {
  translate: pt(1.063, 0.343), rotate: 0,
  id: 'U1'
})
// data_usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(2.365, 1.237), rotate: 0,
  id: 'J1'
})
// data_usb.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(2.213, 1.492), rotate: 0,
  id: 'R1'
})
// data_usb.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(2.369, 1.492), rotate: 0,
  id: 'R2'
})
// gate.pwr_gate.pull_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(3.316, 0.466), rotate: 0,
  id: 'R3'
})
// gate.pwr_gate.pwr_fet
const Q1 = board.add(SOT_23, {
  translate: pt(3.707, 0.067), rotate: 0,
  id: 'Q1'
})
// gate.pwr_gate.amp_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(3.472, 0.466), rotate: 0,
  id: 'R4'
})
// gate.pwr_gate.amp_fet
const Q2 = board.add(SOT_23, {
  translate: pt(3.333, 0.331), rotate: 0,
  id: 'Q2'
})
// gate.pwr_gate.ctl_diode
const D1 = board.add(D_SOD_323, {
  translate: pt(3.512, 0.301), rotate: 0,
  id: 'D1'
})
// gate.pwr_gate.btn_diode
const D2 = board.add(D_SOD_323, {
  translate: pt(3.677, 0.301), rotate: 0,
  id: 'D2'
})
// gate.btn.package
const SW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(3.425, 0.112), rotate: 0,
  id: 'SW1'
})
// reg_5v.ic
const U2 = board.add(SOT_23_5, {
  translate: pt(2.770, 1.752), rotate: 0,
  id: 'U2'
})
// reg_5v.power_path.inductor
const L1 = board.add(L_0603_1608Metric, {
  translate: pt(2.920, 1.887), rotate: 0,
  id: 'L1'
})
// reg_5v.power_path.in_cap.cap
const C1 = board.add(C_0805_2012Metric, {
  translate: pt(2.957, 1.724), rotate: 0,
  id: 'C1'
})
// reg_5v.power_path.out_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(2.756, 1.897), rotate: 0,
  id: 'C2'
})
// reg_5v.ce_res.res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(2.747, 2.004), rotate: 0,
  id: 'R5'
})
// tp_5v.tp
const TP1 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.554, 2.611), rotate: 0,
  id: 'TP1'
})
// prot_5v.diode
const D3 = board.add(D_MiniMELF, {
  translate: pt(2.011, 2.601), rotate: 0,
  id: 'D3'
})
// reg_3v3.ic
const U3 = board.add(SOT_23_5, {
  translate: pt(0.081, 2.276), rotate: 0,
  id: 'U3'
})
// reg_3v3.in_cap.cap
const C3 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.411), rotate: 0,
  id: 'C3'
})
// reg_3v3.out_cap.cap
const C4 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 2.411), rotate: 0,
  id: 'C4'
})
// tp_3v3.tp
const TP2 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.841, 2.611), rotate: 0,
  id: 'TP2'
})
// prot_3v3.diode
const D4 = board.add(D_SOD_323, {
  translate: pt(2.297, 2.595), rotate: 0,
  id: 'D4'
})
// reg_analog.ic
const U4 = board.add(SOT_23_5, {
  translate: pt(0.471, 2.276), rotate: 0,
  id: 'U4'
})
// reg_analog.in_cap.cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 2.411), rotate: 0,
  id: 'C5'
})
// reg_analog.out_cap.cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(0.605, 2.411), rotate: 0,
  id: 'C6'
})
// tp_analog.tp
const TP3 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(1.129, 2.611), rotate: 0,
  id: 'TP3'
})
// prot_analog.diode
const D5 = board.add(D_SOD_323, {
  translate: pt(2.541, 2.595), rotate: 0,
  id: 'D5'
})
// mcu.ic
const U5 = board.add(Raytac_MDBT50Q, {
  translate: pt(0.226, 0.325), rotate: 0,
  id: 'U5'
})
// mcu.swd.conn
const J2 = board.add(Tag_Connect_TC2050_IDC_NL_2x05_P1_27mm_Vertical, {
  translate: pt(0.245, 0.822), rotate: 0,
  id: 'J2'
})
// mcu.vcc_cap.cap
const C7 = board.add(C_0805_2012Metric, {
  translate: pt(0.596, 0.728), rotate: 0,
  id: 'C7'
})
// mcu.usb_res.res_dp
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(0.588, 0.834), rotate: 0,
  id: 'R6'
})
// mcu.usb_res.res_dm
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(0.744, 0.834), rotate: 0,
  id: 'R7'
})
// mcu.vbus_cap.cap
const C8 = board.add(C_0805_2012Metric, {
  translate: pt(0.770, 0.728), rotate: 0,
  id: 'C8'
})
// vbatsense.div.top_res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(3.628, 2.237), rotate: 0,
  id: 'R8'
})
// vbatsense.div.bottom_res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(3.628, 2.334), rotate: 0,
  id: 'R9'
})
// usb_esd
const U6 = board.add(SOT_23, {
  translate: pt(2.798, 2.624), rotate: 0,
  id: 'U6'
})
// rgb.package
const D6 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(2.677, 2.264), rotate: 0,
  id: 'D6'
})
// rgb.red_res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(2.816, 2.237), rotate: 0,
  id: 'R10'
})
// rgb.green_res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(2.694, 2.387), rotate: 0,
  id: 'R11'
})
// rgb.blue_res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(2.850, 2.387), rotate: 0,
  id: 'R12'
})
// sw1.package
const SW2 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.507, 2.321), rotate: 0,
  id: 'SW2'
})
// sw2.package
const SW3 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.960, 2.321), rotate: 0,
  id: 'SW3'
})
// lcd.device.conn
const J3 = board.add(Hirose_FH12_8S_0_5SH_1x08_1MP_P0_50mm_Horizontal, {
  translate: pt(2.891, 1.265), rotate: 0,
  id: 'J3'
})
// lcd.led_res
const R13 = board.add(R_0603_1608Metric, {
  translate: pt(2.750, 1.452), rotate: 0,
  id: 'R13'
})
// lcd.vdd_cap.cap
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(2.906, 1.452), rotate: 0,
  id: 'C9'
})
// spk_dac.rc.r
const R14 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.586), rotate: 0,
  id: 'R14'
})
// spk_dac.rc.c
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.683), rotate: 0,
  id: 'C10'
})
// spk_tp.tp
const TP4 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(1.416, 2.611), rotate: 0,
  id: 'TP4'
})
// spk_drv.ic
const U7 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(3.265, 1.754), rotate: 0,
  id: 'U7'
})
// spk_drv.pwr_cap.cap
const C11 = board.add(C_0603_1608Metric, {
  translate: pt(3.200, 1.891), rotate: 0,
  id: 'C11'
})
// spk_drv.bulk_cap.cap
const C12 = board.add(C_0805_2012Metric, {
  translate: pt(3.494, 1.724), rotate: 0,
  id: 'C12'
})
// spk_drv.inp_res
const R15 = board.add(R_0603_1608Metric, {
  translate: pt(3.356, 1.891), rotate: 0,
  id: 'R15'
})
// spk_drv.inp_cap
const C13 = board.add(C_0603_1608Metric, {
  translate: pt(3.512, 1.891), rotate: 0,
  id: 'C13'
})
// spk_drv.inn_res
const R16 = board.add(R_0603_1608Metric, {
  translate: pt(3.200, 1.988), rotate: 0,
  id: 'R16'
})
// spk_drv.inn_cap
const C14 = board.add(C_0603_1608Metric, {
  translate: pt(3.356, 1.988), rotate: 0,
  id: 'C14'
})
// spk.conn
const J4 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.342, 2.339), rotate: 0,
  id: 'J4'
})
// ref_div.div.top_res
const R17 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 2.586), rotate: 0,
  id: 'R17'
})
// ref_div.div.bottom_res
const R18 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 2.683), rotate: 0,
  id: 'R18'
})
// ref_buf.amp.ic
const U8 = board.add(SOT_23_6, {
  translate: pt(0.862, 2.276), rotate: 0,
  id: 'U8'
})
// ref_buf.amp.vdd_cap.cap
const C15 = board.add(C_0603_1608Metric, {
  translate: pt(0.839, 2.411), rotate: 0,
  id: 'C15'
})
// inn
const J5 = board.add(CLIFF_FCR7350, {
  translate: pt(1.083, 1.927), rotate: 0,
  id: 'J5'
})
// inn_mux.device.ic
const U9 = board.add(SOT_363_SC_70_6, {
  translate: pt(3.089, 2.264), rotate: 0,
  id: 'U9'
})
// inn_mux.device.vdd_cap.cap
const C16 = board.add(C_0603_1608Metric, {
  translate: pt(3.084, 2.387), rotate: 0,
  id: 'C16'
})
// inp
const J6 = board.add(CLIFF_FCR7350, {
  translate: pt(2.427, 1.927), rotate: 0,
  id: 'J6'
})
// measure.res
const R19 = board.add(R_2512_6332Metric, {
  translate: pt(0.150, 1.148), rotate: 0,
  id: 'R19'
})
// measure.range.switch.sw[0_0].ic
const U10 = board.add(SOT_363_SC_70_6, {
  translate: pt(0.403, 1.128), rotate: 0,
  id: 'U10'
})
// measure.range.switch.sw[0_0].vdd_cap.cap
const C17 = board.add(C_0603_1608Metric, {
  translate: pt(0.389, 1.292), rotate: 0,
  id: 'C17'
})
// measure.range.switch.sw[0_1].ic
const U11 = board.add(SOT_363_SC_70_6, {
  translate: pt(0.063, 1.318), rotate: 0,
  id: 'U11'
})
// measure.range.switch.sw[0_1].vdd_cap.cap
const C18 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.441), rotate: 0,
  id: 'C18'
})
// measure.range.switch.sw[1_0].ic
const U12 = board.add(SOT_363_SC_70_6, {
  translate: pt(0.228, 1.318), rotate: 0,
  id: 'U12'
})
// measure.range.switch.sw[1_0].vdd_cap.cap
const C19 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.441), rotate: 0,
  id: 'C19'
})
// measure.range.res[0]
const R20 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 1.441), rotate: 0,
  id: 'R20'
})
// measure.range.res[1]
const R21 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 1.441), rotate: 0,
  id: 'R21'
})
// measure.range.res[2]
const R22 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.538), rotate: 0,
  id: 'R22'
})
// measure_buffer.amp.ic
const U13 = board.add(SOT_23_6, {
  translate: pt(1.141, 2.276), rotate: 0,
  id: 'U13'
})
// measure_buffer.amp.vdd_cap.cap
const C20 = board.add(C_0603_1608Metric, {
  translate: pt(1.119, 2.411), rotate: 0,
  id: 'C20'
})
// tp_measure.tp
const TP5 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(1.704, 2.611), rotate: 0,
  id: 'TP5'
})
// adc.ic
const U14 = board.add(TSSOP_20_4_4x6_5mm_P0_65mm, {
  translate: pt(1.712, 1.210), rotate: 0,
  id: 'U14'
})
// adc.avdd_res.res
const R23 = board.add(R_0603_1608Metric, {
  translate: pt(1.961, 1.218), rotate: 0,
  id: 'R23'
})
// adc.dvdd_res.res
const R24 = board.add(R_0603_1608Metric, {
  translate: pt(1.961, 1.315), rotate: 0,
  id: 'R24'
})
// adc.avdd_cap_0.cap
const C21 = board.add(C_0603_1608Metric, {
  translate: pt(1.619, 1.416), rotate: 0,
  id: 'C21'
})
// adc.avdd_cap_1.cap
const C22 = board.add(C_0603_1608Metric, {
  translate: pt(1.775, 1.416), rotate: 0,
  id: 'C22'
})
// adc.dvdd_cap_0.cap
const C23 = board.add(C_0603_1608Metric, {
  translate: pt(1.931, 1.416), rotate: 0,
  id: 'C23'
})
// adc.dvdd_cap_1.cap
const C24 = board.add(C_0603_1608Metric, {
  translate: pt(1.619, 1.513), rotate: 0,
  id: 'C24'
})
// adc.vref_cap.cap
const C25 = board.add(C_0805_2012Metric, {
  translate: pt(1.970, 1.111), rotate: 0,
  id: 'C25'
})
// driver.fet
const Q3 = board.add(SOT_23, {
  translate: pt(1.093, 1.139), rotate: 0,
  id: 'Q3'
})
// driver.amp.ic
const U15 = board.add(SOT_23_6, {
  translate: pt(1.289, 1.139), rotate: 0,
  id: 'U15'
})
// driver.amp.vdd_cap.cap
const C26 = board.add(C_0603_1608Metric, {
  translate: pt(0.761, 1.428), rotate: 0,
  id: 'C26'
})
// driver.range.switch.sw[0_0].ic
const U16 = board.add(SOT_363_SC_70_6, {
  translate: pt(0.765, 1.305), rotate: 0,
  id: 'U16'
})
// driver.range.switch.sw[0_0].vdd_cap.cap
const C27 = board.add(C_0603_1608Metric, {
  translate: pt(0.917, 1.428), rotate: 0,
  id: 'C27'
})
// driver.range.switch.sw[0_1].ic
const U17 = board.add(SOT_363_SC_70_6, {
  translate: pt(0.931, 1.305), rotate: 0,
  id: 'U17'
})
// driver.range.switch.sw[0_1].vdd_cap.cap
const C28 = board.add(C_0603_1608Metric, {
  translate: pt(1.072, 1.428), rotate: 0,
  id: 'C28'
})
// driver.range.switch.sw[1_0].ic
const U18 = board.add(SOT_363_SC_70_6, {
  translate: pt(1.096, 1.305), rotate: 0,
  id: 'U18'
})
// driver.range.switch.sw[1_0].vdd_cap.cap
const C29 = board.add(C_0603_1608Metric, {
  translate: pt(1.228, 1.428), rotate: 0,
  id: 'C29'
})
// driver.range.res[0]
const R25 = board.add(R_0603_1608Metric, {
  translate: pt(1.384, 1.428), rotate: 0,
  id: 'R25'
})
// driver.range.res[1]
const R26 = board.add(R_0603_1608Metric, {
  translate: pt(0.761, 1.525), rotate: 0,
  id: 'R26'
})
// driver.range.res[2]
const R27 = board.add(R_0603_1608Metric, {
  translate: pt(0.917, 1.525), rotate: 0,
  id: 'R27'
})
// driver.range.res[3]
const R28 = board.add(R_0603_1608Metric, {
  translate: pt(1.072, 1.525), rotate: 0,
  id: 'R28'
})
// driver.sw.device.ic
const U19 = board.add(SOT_363_SC_70_6, {
  translate: pt(1.261, 1.305), rotate: 0,
  id: 'U19'
})
// driver.sw.device.vdd_cap.cap
const C30 = board.add(C_0603_1608Metric, {
  translate: pt(1.228, 1.525), rotate: 0,
  id: 'C30'
})
// driver.diode
const D7 = board.add(D_SMA, {
  translate: pt(0.841, 1.141), rotate: 0,
  id: 'D7'
})
// driver_dac.rc.r
const R29 = board.add(R_0603_1608Metric, {
  translate: pt(3.328, 2.367), rotate: 0,
  id: 'R29'
})
// driver_dac.rc.c
const C31 = board.add(C_1206_3216Metric, {
  translate: pt(3.361, 2.254), rotate: 0,
  id: 'C31'
})

board.setNetlist([
  {name: "gnd", pads: [["U1", "2"], ["U6", "3"], ["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["U2", "2"], ["D3", "2"], ["U3", "2"], ["D4", "2"], ["U4", "2"], ["D5", "2"], ["U5", "1"], ["U5", "2"], ["U5", "15"], ["U5", "33"], ["U5", "55"], ["SW2", "2"], ["SW3", "2"], ["U7", "7"], ["U7", "9"], ["U14", "2"], ["U14", "3"], ["U14", "19"], ["R9", "2"], ["C10", "2"], ["R18", "2"], ["U8", "2"], ["U9", "2"], ["U13", "2"], ["C31", "2"], ["J1", "S1"], ["C14", "2"], ["R4", "1"], ["Q2", "2"], ["SW1", "2"], ["C3", "2"], ["C4", "2"], ["C5", "2"], ["C6", "2"], ["C7", "2"], ["C8", "2"], ["J3", "2"], ["C9", "2"], ["C11", "2"], ["C12", "2"], ["U9", "3"], ["C21", "2"], ["C22", "2"], ["C23", "2"], ["C24", "2"], ["C25", "2"], ["U15", "2"], ["C15", "2"], ["C16", "2"], ["C20", "2"], ["U19", "2"], ["U10", "2"], ["U11", "2"], ["U12", "2"], ["J2", "2"], ["J2", "3"], ["J2", "5"], ["R1", "1"], ["R2", "1"], ["C1", "2"], ["C2", "2"], ["C26", "2"], ["U16", "2"], ["U17", "2"], ["U18", "2"], ["C30", "2"], ["C17", "2"], ["C18", "2"], ["C19", "2"], ["C27", "2"], ["C28", "2"], ["C29", "2"]]},
  {name: "vbat", pads: [["U1", "1"], ["R3", "1"], ["Q1", "2"]]},
  {name: "v5v", pads: [["U2", "4"], ["TP1", "1"], ["D3", "1"], ["U3", "1"], ["U4", "1"], ["C2", "1"], ["U3", "3"], ["U4", "3"], ["U7", "1"], ["U7", "6"], ["C3", "1"], ["C5", "1"], ["C11", "1"], ["C12", "1"]]},
  {name: "v3v3", pads: [["U3", "5"], ["TP2", "1"], ["D4", "1"], ["U5", "28"], ["U5", "30"], ["D6", "2"], ["R24", "1"], ["C4", "1"], ["R13", "1"], ["J2", "1"], ["C7", "1"], ["J3", "7"], ["C9", "1"]]},
  {name: "vanalog", pads: [["U4", "5"], ["TP3", "1"], ["D5", "1"], ["U8", "5"], ["U8", "6"], ["R17", "1"], ["U9", "5"], ["U13", "5"], ["U13", "6"], ["R23", "1"], ["C6", "1"], ["U15", "5"], ["U15", "6"], ["C15", "1"], ["C16", "1"], ["C20", "1"], ["U19", "5"], ["U10", "5"], ["U11", "5"], ["U12", "5"], ["R25", "1"], ["R26", "1"], ["R27", "1"], ["R28", "1"], ["C26", "1"], ["C30", "1"], ["U16", "5"], ["U17", "5"], ["U18", "5"], ["C17", "1"], ["C18", "1"], ["C19", "1"], ["C27", "1"], ["C28", "1"], ["C29", "1"]]},
  {name: "vcenter", pads: [["U8", "4"], ["U9", "1"], ["U8", "1"]]},
  {name: "gate.pwr_out", pads: [["Q1", "3"], ["U2", "3"], ["R8", "1"], ["R5", "1"], ["L1", "1"], ["C1", "1"]]},
  {name: "vbatsense.output", pads: [["U5", "9"], ["R8", "2"], ["R9", "1"]]},
  {name: "data_usb.usb.dp", pads: [["J1", "A6"], ["J1", "B6"], ["U6", "2"], ["R6", "2"]]},
  {name: "data_usb.usb.dm", pads: [["J1", "A7"], ["J1", "B7"], ["U6", "1"], ["R7", "2"]]},
  {name: "mcu.pwr_usb", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["U5", "32"], ["C8", "1"]]},
  {name: "gate.btn_out", pads: [["U5", "50"], ["D2", "2"]]},
  {name: "gate.control", pads: [["U5", "49"], ["R4", "2"], ["Q2", "1"]]},
  {name: "mcu.gpio.rgb_red", pads: [["U5", "4"], ["R10", "2"]]},
  {name: "mcu.gpio.rgb_green", pads: [["U5", "5"], ["R11", "2"]]},
  {name: "mcu.gpio.rgb_blue", pads: [["U5", "6"], ["R12", "2"]]},
  {name: "sw1.out", pads: [["U5", "16"], ["SW2", "1"]]},
  {name: "sw2.out", pads: [["U5", "3"], ["SW3", "1"]]},
  {name: "lcd.reset", pads: [["U5", "8"], ["J3", "3"]]},
  {name: "lcd.rs", pads: [["U5", "10"], ["J3", "4"]]},
  {name: "lcd.spi.sck", pads: [["U5", "18"], ["J3", "6"]]},
  {name: "lcd.spi.mosi", pads: [["U5", "19"], ["J3", "5"]]},
  {name: "lcd.cs", pads: [["U5", "17"], ["J3", "8"]]},
  {name: "spk_chain_0", pads: [["U5", "36"], ["R14", "1"]]},
  {name: "spk_chain_1", pads: [["TP4", "1"], ["C13", "2"], ["R14", "2"], ["C10", "1"]]},
  {name: "spk_chain_2.a", pads: [["U7", "8"], ["J4", "1"]]},
  {name: "spk_chain_2.b", pads: [["U7", "5"], ["J4", "2"]]},
  {name: "ref_div.output", pads: [["U8", "3"], ["R17", "2"], ["R18", "1"]]},
  {name: "inn_merge", pads: [["J5", "1"], ["U14", "6"], ["U9", "4"], ["U12", "4"]]},
  {name: "mcu.gpio.inn_control_0", pads: [["U5", "41"], ["U9", "6"]]},
  {name: "inp.port", pads: [["J6", "1"], ["R19", "1"], ["D7", "1"]]},
  {name: "meas_chain_0", pads: [["U13", "3"], ["R19", "2"], ["R20", "1"], ["R21", "1"], ["R22", "1"]]},
  {name: "meas_chain_1", pads: [["U14", "5"], ["U13", "4"], ["TP5", "1"], ["U13", "1"]]},
  {name: "adc.spi.sck", pads: [["U14", "14"], ["U5", "37"]]},
  {name: "adc.spi.mosi", pads: [["U14", "15"], ["U5", "26"]]},
  {name: "adc.spi.miso", pads: [["U14", "16"], ["U5", "24"]]},
  {name: "mcu.gpio.measure_select_0_0", pads: [["U5", "42"], ["U10", "6"], ["U11", "6"]]},
  {name: "mcu.gpio.measure_select_1_0", pads: [["U5", "43"], ["U12", "6"]]},
  {name: "adc.cs", pads: [["U5", "39"], ["U14", "13"]]},
  {name: "driver_dac.input", pads: [["U5", "45"], ["R29", "1"]]},
  {name: "driver_dac.output", pads: [["U15", "3"], ["R29", "2"], ["C31", "1"]]},
  {name: "mcu.gpio.driver_select_0_0", pads: [["U5", "46"], ["U16", "6"], ["U17", "6"]]},
  {name: "mcu.gpio.driver_select_1_0", pads: [["U5", "44"], ["U18", "6"]]},
  {name: "driver.enable", pads: [["U5", "48"], ["U19", "6"]]},
  {name: "data_usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "data_usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "gate.pwr_gate.btn_in", pads: [["D2", "1"], ["D1", "1"], ["SW1", "1"]]},
  {name: "gate.pwr_gate.pull_res.b", pads: [["R3", "2"], ["D1", "2"], ["Q1", "1"], ["Q2", "3"]]},
  {name: "reg_5v.power_path.switch", pads: [["U2", "5"], ["L1", "2"]]},
  {name: "reg_5v.ic.ce", pads: [["U2", "1"], ["R5", "2"]]},
  {name: "mcu.swd_node.swdio", pads: [["U5", "51"], ["J2", "10"]]},
  {name: "mcu.swd_node.swclk", pads: [["U5", "53"], ["J2", "9"]]},
  {name: "mcu.reset_node", pads: [["U5", "40"], ["J2", "6"]]},
  {name: "mcu.usb_chain_0.d_P", pads: [["U5", "35"], ["R6", "1"]]},
  {name: "mcu.usb_chain_0.d_N", pads: [["U5", "34"], ["R7", "1"]]},
  {name: "mcu.swd.swo", pads: [["U5", "47"], ["J2", "8"]]},
  {name: "mcu.swd.tdi", pads: [["J2", "7"]]},
  {name: "rgb.red_res.a", pads: [["R10", "1"], ["D6", "3"]]},
  {name: "rgb.green_res.a", pads: [["R11", "1"], ["D6", "4"]]},
  {name: "rgb.blue_res.a", pads: [["R12", "1"], ["D6", "1"]]},
  {name: "lcd.led_res.b", pads: [["R13", "2"], ["J3", "1"]]},
  {name: "spk_drv.inp_cap.pos", pads: [["C13", "1"], ["R15", "1"]]},
  {name: "spk_drv.inp_res.b", pads: [["R15", "2"], ["U7", "4"]]},
  {name: "spk_drv.inn_cap.pos", pads: [["C14", "1"], ["R16", "1"]]},
  {name: "spk_drv.inn_res.b", pads: [["R16", "2"], ["U7", "3"]]},
  {name: "measure.range.res[0].b", pads: [["R20", "2"], ["U10", "3"]]},
  {name: "measure.range.res[1].b", pads: [["R21", "2"], ["U10", "1"]]},
  {name: "measure.range.res[2].b", pads: [["R22", "2"], ["U11", "3"]]},
  {name: "measure.range.dummy.io", pads: [["U11", "1"]]},
  {name: "measure.range.switch.sw[0_0].com", pads: [["U12", "3"], ["U10", "4"]]},
  {name: "measure.range.switch.sw[0_1].com", pads: [["U12", "1"], ["U11", "4"]]},
  {name: "adc.vins.2", pads: [["U14", "7"]]},
  {name: "adc.vins.3", pads: [["U14", "8"]]},
  {name: "adc.vins.4", pads: [["U14", "9"]]},
  {name: "adc.vins.5", pads: [["U14", "10"]]},
  {name: "adc.vins.6", pads: [["U14", "11"]]},
  {name: "adc.vins.7", pads: [["U14", "12"]]},
  {name: "adc.ic.avdd", pads: [["U14", "1"], ["R23", "2"], ["C21", "1"], ["C22", "1"]]},
  {name: "adc.ic.dvdd", pads: [["U14", "20"], ["R24", "2"], ["C23", "1"], ["C24", "1"]]},
  {name: "adc.ic.vrefp", pads: [["U14", "4"], ["C25", "1"]]},
  {name: "driver.fet.source", pads: [["Q3", "2"], ["U15", "4"], ["U19", "3"], ["U18", "4"]]},
  {name: "driver.amp.out", pads: [["U15", "1"], ["U19", "1"]]},
  {name: "driver.fet.gate", pads: [["Q3", "1"], ["U19", "4"]]},
  {name: "driver.fet.drain", pads: [["Q3", "3"], ["D7", "2"]]},
  {name: "driver.range.res[0].b", pads: [["R25", "2"], ["U16", "3"]]},
  {name: "driver.range.res[1].b", pads: [["R26", "2"], ["U16", "1"]]},
  {name: "driver.range.res[2].b", pads: [["R27", "2"], ["U17", "3"]]},
  {name: "driver.range.res[3].b", pads: [["R28", "2"], ["U17", "1"]]},
  {name: "driver.range.switch.sw[0_0].com", pads: [["U18", "3"], ["U16", "4"]]},
  {name: "driver.range.switch.sw[0_1].com", pads: [["U18", "1"], ["U17", "4"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.9010236220472447, 2.82992125984252);
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


