const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(5.588, 4.566), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(5.627, 4.566), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(5.588, 4.605), rotate: 0,
  id: 'H3'
})
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(3.954, 3.280), rotate: 0,
  id: 'J1'
})
// tp_gnd.tp
const TP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.259, 4.603), rotate: 0,
  id: 'TP1'
})
// filt_vusb.fb
const FB1 = board.add(L_1206_3216Metric, {
  translate: pt(1.979, 4.613), rotate: 0,
  id: 'FB1'
})
// cap_vusb.cap
const C1 = board.add(CP_Elec_8x10, {
  translate: pt(4.498, 3.288), rotate: 0,
  id: 'C1'
})
// prot_vusb.diode
const D1 = board.add(D_SMA, {
  translate: pt(1.630, 4.635), rotate: 0,
  id: 'D1'
})
// tp_vusb.tp
const TP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.256, 4.603), rotate: 0,
  id: 'TP2'
})
// reg_v5.ic
const U1 = board.add(SOT_23_6, {
  translate: pt(2.127, 3.182), rotate: 0,
  id: 'U1'
})
// reg_v5.fb.div.top_res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(2.286, 3.400), rotate: 0,
  id: 'R1'
})
// reg_v5.fb.div.bottom_res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(1.845, 3.530), rotate: 0,
  id: 'R2'
})
// reg_v5.hf_in_cap.cap
const C2 = board.add(C_0603_1608Metric, {
  translate: pt(2.001, 3.530), rotate: 0,
  id: 'C2'
})
// reg_v5.boot_cap
const C3 = board.add(C_0603_1608Metric, {
  translate: pt(2.157, 3.530), rotate: 0,
  id: 'C3'
})
// reg_v5.power_path.inductor
const L1 = board.add(L_Sunlord_SWPA5040S, {
  translate: pt(1.897, 3.224), rotate: 0,
  id: 'L1'
})
// reg_v5.power_path.in_cap.cap
const C4 = board.add(C_1206_3216Metric, {
  translate: pt(1.877, 3.417), rotate: 0,
  id: 'C4'
})
// reg_v5.power_path.out_cap.cap
const C5 = board.add(C_1206_3216Metric, {
  translate: pt(2.098, 3.417), rotate: 0,
  id: 'C5'
})
// reg_v5.en_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(2.313, 3.530), rotate: 0,
  id: 'R3'
})
// tp_v5.tp
const TP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.758, 4.603), rotate: 0,
  id: 'TP3'
})
// reg_3v3.ic
const U2 = board.add(SOT_223_3_TabPin2, {
  translate: pt(3.154, 3.257), rotate: 0,
  id: 'U2'
})
// reg_3v3.in_cap.cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(3.213, 3.467), rotate: 0,
  id: 'C6'
})
// reg_3v3.out_cap.cap
const C7 = board.add(C_0805_2012Metric, {
  translate: pt(3.048, 3.476), rotate: 0,
  id: 'C7'
})
// prot_3v3.diode
const D2 = board.add(D_SMA, {
  translate: pt(0.842, 4.635), rotate: 0,
  id: 'D2'
})
// tp_3v3.tp
const TP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.509, 4.603), rotate: 0,
  id: 'TP4'
})
// conv.power_path.inductor
const L2 = board.add(L_Bourns_SRP1245A, {
  translate: pt(0.289, 2.069), rotate: 0,
  id: 'L2'
})
// conv.power_path.in_cap.cap.c[0]
const C8 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 2.725), rotate: 0,
  id: 'C8'
})
// conv.power_path.in_cap.cap.c[1]
const C9 = board.add(C_1206_3216Metric, {
  translate: pt(0.311, 2.725), rotate: 0,
  id: 'C9'
})
// conv.power_path.in_cap.cap.c[2]
const C10 = board.add(C_1206_3216Metric, {
  translate: pt(0.531, 2.725), rotate: 0,
  id: 'C10'
})
// conv.power_path.out_cap.cap.c[0]
const C11 = board.add(C_1206_3216Metric, {
  translate: pt(0.752, 2.725), rotate: 0,
  id: 'C11'
})
// conv.power_path.out_cap.cap.c[1]
const C12 = board.add(C_1206_3216Metric, {
  translate: pt(0.972, 2.725), rotate: 0,
  id: 'C12'
})
// conv.power_path.out_cap.cap.c[2]
const C13 = board.add(C_1206_3216Metric, {
  translate: pt(1.193, 2.725), rotate: 0,
  id: 'C13'
})
// conv.power_path.out_cap.cap.c[3]
const C14 = board.add(C_1206_3216Metric, {
  translate: pt(1.413, 2.725), rotate: 0,
  id: 'C14'
})
// conv.power_path.out_cap.cap.c[4]
const C15 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 2.855), rotate: 0,
  id: 'C15'
})
// conv.power_path.out_cap.cap.c[5]
const C16 = board.add(C_1206_3216Metric, {
  translate: pt(0.311, 2.855), rotate: 0,
  id: 'C16'
})
// conv.power_path.out_cap.cap.c[6]
const C17 = board.add(C_1206_3216Metric, {
  translate: pt(0.531, 2.855), rotate: 0,
  id: 'C17'
})
// conv.power_path.out_cap.cap.c[7]
const C18 = board.add(C_1206_3216Metric, {
  translate: pt(0.752, 2.855), rotate: 0,
  id: 'C18'
})
// conv.power_path.out_cap.cap.c[8]
const C19 = board.add(C_1206_3216Metric, {
  translate: pt(0.972, 2.855), rotate: 0,
  id: 'C19'
})
// conv.buck_sw.driver.ic
const U3 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.098, 2.471), rotate: 0,
  id: 'U3'
})
// conv.buck_sw.driver.cap.cap
const C20 = board.add(C_0603_1608Metric, {
  translate: pt(1.492, 2.838), rotate: 0,
  id: 'C20'
})
// conv.buck_sw.driver.high_cap.cap
const C21 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.968), rotate: 0,
  id: 'C21'
})
// conv.buck_sw.driver.boot
const D3 = board.add(D_SOD_323, {
  translate: pt(1.166, 2.847), rotate: 0,
  id: 'D3'
})
// conv.buck_sw.low_fet
const Q1 = board.add(TO_252_2, {
  translate: pt(0.870, 1.951), rotate: 0,
  id: 'Q1'
})
// conv.buck_sw.low_gate_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.968), rotate: 0,
  id: 'R4'
})
// conv.buck_sw.high_fet
const Q2 = board.add(TO_252_2, {
  translate: pt(1.346, 1.951), rotate: 0,
  id: 'Q2'
})
// conv.buck_sw.high_gate_res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 2.968), rotate: 0,
  id: 'R5'
})
// conv.boost_sw.driver.ic
const U4 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.429, 2.471), rotate: 0,
  id: 'U4'
})
// conv.boost_sw.driver.cap.cap
const C22 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 2.968), rotate: 0,
  id: 'C22'
})
// conv.boost_sw.driver.high_cap.cap
const C23 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 2.968), rotate: 0,
  id: 'C23'
})
// conv.boost_sw.driver.boot
const D4 = board.add(D_SOD_323, {
  translate: pt(1.331, 2.847), rotate: 0,
  id: 'D4'
})
// conv.boost_sw.low_fet
const Q3 = board.add(TO_252_2, {
  translate: pt(0.252, 2.502), rotate: 0,
  id: 'Q3'
})
// conv.boost_sw.low_gate_res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 2.968), rotate: 0,
  id: 'R6'
})
// conv.boost_sw.high_fet
const Q4 = board.add(TO_252_2, {
  translate: pt(0.728, 2.502), rotate: 0,
  id: 'Q4'
})
// conv.boost_sw.high_gate_res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 2.968), rotate: 0,
  id: 'R7'
})
// prot_conv.diode
const D5 = board.add(D_SMA, {
  translate: pt(1.236, 4.635), rotate: 0,
  id: 'D5'
})
// tp_conv.tp
const TP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.507, 4.603), rotate: 0,
  id: 'TP5'
})
// reg_v12.ic
const U5 = board.add(SOT_23_5, {
  translate: pt(5.460, 3.182), rotate: 0,
  id: 'U5'
})
// reg_v12.fb.div.top_res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(5.781, 3.317), rotate: 0,
  id: 'R8'
})
// reg_v12.fb.div.bottom_res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(5.438, 3.431), rotate: 0,
  id: 'R9'
})
// reg_v12.power_path.inductor
const L3 = board.add(L_0805_2012Metric, {
  translate: pt(5.614, 3.322), rotate: 0,
  id: 'L3'
})
// reg_v12.power_path.in_cap.cap
const C24 = board.add(C_0805_2012Metric, {
  translate: pt(5.647, 3.154), rotate: 0,
  id: 'C24'
})
// reg_v12.power_path.out_cap.cap
const C25 = board.add(C_0603_1608Metric, {
  translate: pt(5.594, 3.431), rotate: 0,
  id: 'C25'
})
// reg_v12.cf
const C26 = board.add(C_0603_1608Metric, {
  translate: pt(5.750, 3.431), rotate: 0,
  id: 'C26'
})
// reg_v12.rect
const D6 = board.add(D_SOD_323, {
  translate: pt(5.443, 3.326), rotate: 0,
  id: 'D6'
})
// tp_v12.tp
const TP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.007, 4.603), rotate: 0,
  id: 'TP6'
})
// reg_analog.ic
const U6 = board.add(SOT_23_5, {
  translate: pt(3.526, 3.182), rotate: 0,
  id: 'U6'
})
// reg_analog.in_cap.cap
const C27 = board.add(C_0603_1608Metric, {
  translate: pt(3.504, 3.447), rotate: 0,
  id: 'C27'
})
// reg_analog.out_cap.cap
const C28 = board.add(C_1206_3216Metric, {
  translate: pt(3.536, 3.333), rotate: 0,
  id: 'C28'
})
// tp_analog.tp
const TP7 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.756, 4.603), rotate: 0,
  id: 'TP7'
})
// reg_vref.ic
const U7 = board.add(SOT_23, {
  translate: pt(1.409, 4.251), rotate: 0,
  id: 'U7'
})
// reg_vref.in_cap.cap
const C29 = board.add(C_0603_1608Metric, {
  translate: pt(1.391, 4.386), rotate: 0,
  id: 'C29'
})
// tp_vref.tp
const TP8 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.008, 4.603), rotate: 0,
  id: 'TP8'
})
// ref_div.div.top_res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(5.394, 4.213), rotate: 0,
  id: 'R10'
})
// ref_div.div.bottom_res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(5.394, 4.309), rotate: 0,
  id: 'R11'
})
// ref_cap
const C30 = board.add(C_0603_1608Metric, {
  translate: pt(5.804, 4.594), rotate: 0,
  id: 'C30'
})
// reg_vcontrol.ic
const U8 = board.add(SOT_23_5, {
  translate: pt(4.904, 3.182), rotate: 0,
  id: 'U8'
})
// reg_vcontrol.fb.div.top_res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(5.047, 3.317), rotate: 0,
  id: 'R12'
})
// reg_vcontrol.fb.div.bottom_res
const R13 = board.add(R_0603_1608Metric, {
  translate: pt(5.203, 3.317), rotate: 0,
  id: 'R13'
})
// reg_vcontrol.power_path.inductor
const L4 = board.add(L_0603_1608Metric, {
  translate: pt(4.881, 3.431), rotate: 0,
  id: 'L4'
})
// reg_vcontrol.power_path.in_cap.cap
const C31 = board.add(C_0603_1608Metric, {
  translate: pt(5.037, 3.431), rotate: 0,
  id: 'C31'
})
// reg_vcontrol.power_path.out_cap.cap
const C32 = board.add(C_0805_2012Metric, {
  translate: pt(5.091, 3.154), rotate: 0,
  id: 'C32'
})
// reg_vcontrol.cf
const C33 = board.add(C_0603_1608Metric, {
  translate: pt(5.193, 3.431), rotate: 0,
  id: 'C33'
})
// reg_vcontrol.rect
const D7 = board.add(D_SOD_323, {
  translate: pt(4.887, 3.326), rotate: 0,
  id: 'D7'
})
// tp_vcontrol.tp
const TP9 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.257, 4.603), rotate: 0,
  id: 'TP9'
})
// reg_vcontroln.ic
const U9 = board.add(SOT_23_6, {
  translate: pt(0.081, 4.251), rotate: 0,
  id: 'U9'
})
// reg_vcontroln.cf
const C34 = board.add(C_0805_2012Metric, {
  translate: pt(0.287, 4.396), rotate: 0,
  id: 'C34'
})
// reg_vcontroln.cout.cap.c[0]
const C35 = board.add(C_1206_3216Metric, {
  translate: pt(0.291, 4.229), rotate: 0,
  id: 'C35'
})
// reg_vcontroln.cout.cap.c[1]
const C36 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 4.402), rotate: 0,
  id: 'C36'
})
// tp_vcontroln.tp
const TP10 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.506, 4.603), rotate: 0,
  id: 'TP10'
})
// control.dmeas.r1
const R14 = board.add(R_0603_1608Metric, {
  translate: pt(2.980, 2.519), rotate: 0,
  id: 'R14'
})
// control.dmeas.r2
const R15 = board.add(R_0603_1608Metric, {
  translate: pt(3.135, 2.519), rotate: 0,
  id: 'R15'
})
// control.dmeas.rf
const R16 = board.add(R_0603_1608Metric, {
  translate: pt(1.751, 2.647), rotate: 0,
  id: 'R16'
})
// control.dmeas.rg
const R17 = board.add(R_0603_1608Metric, {
  translate: pt(1.907, 2.647), rotate: 0,
  id: 'R17'
})
// control.dclamp.res
const R18 = board.add(R_0603_1608Metric, {
  translate: pt(2.063, 2.647), rotate: 0,
  id: 'R18'
})
// control.err_d.rtop
const R19 = board.add(R_0603_1608Metric, {
  translate: pt(2.219, 2.647), rotate: 0,
  id: 'R19'
})
// control.err_d.rbot
const R20 = board.add(R_0603_1608Metric, {
  translate: pt(2.375, 2.647), rotate: 0,
  id: 'R20'
})
// control.err_d.rout
const R21 = board.add(R_0603_1608Metric, {
  translate: pt(2.531, 2.647), rotate: 0,
  id: 'R21'
})
// control.err_volt.rtop
const R22 = board.add(R_0603_1608Metric, {
  translate: pt(2.687, 2.647), rotate: 0,
  id: 'R22'
})
// control.err_volt.rbot
const R23 = board.add(R_0603_1608Metric, {
  translate: pt(2.843, 2.647), rotate: 0,
  id: 'R23'
})
// control.err_volt.rout
const R24 = board.add(R_0603_1608Metric, {
  translate: pt(2.998, 2.647), rotate: 0,
  id: 'R24'
})
// control.err_source.rtop
const R25 = board.add(R_0603_1608Metric, {
  translate: pt(3.154, 2.647), rotate: 0,
  id: 'R25'
})
// control.err_source.rbot
const R26 = board.add(R_0603_1608Metric, {
  translate: pt(1.751, 2.744), rotate: 0,
  id: 'R26'
})
// control.err_source.rout
const R27 = board.add(R_0603_1608Metric, {
  translate: pt(1.907, 2.744), rotate: 0,
  id: 'R27'
})
// control.err_source.diode
const D8 = board.add(D_SOD_323, {
  translate: pt(2.322, 2.528), rotate: 0,
  id: 'D8'
})
// control.err_sink.rtop
const R28 = board.add(R_0603_1608Metric, {
  translate: pt(2.063, 2.744), rotate: 0,
  id: 'R28'
})
// control.err_sink.rbot
const R29 = board.add(R_0603_1608Metric, {
  translate: pt(2.219, 2.744), rotate: 0,
  id: 'R29'
})
// control.err_sink.rout
const R30 = board.add(R_0603_1608Metric, {
  translate: pt(2.375, 2.744), rotate: 0,
  id: 'R30'
})
// control.err_sink.diode
const D9 = board.add(D_SOD_323, {
  translate: pt(2.487, 2.528), rotate: 0,
  id: 'D9'
})
// control.off_sw.device.ic
const U10 = board.add(SOT_363_SC_70_6, {
  translate: pt(2.965, 2.231), rotate: 0,
  id: 'U10'
})
// control.off_sw.device.vdd_cap.cap
const C37 = board.add(C_0603_1608Metric, {
  translate: pt(2.531, 2.744), rotate: 0,
  id: 'C37'
})
// control.int.r
const R31 = board.add(R_0603_1608Metric, {
  translate: pt(2.687, 2.744), rotate: 0,
  id: 'R31'
})
// control.int.c
const C38 = board.add(C_0603_1608Metric, {
  translate: pt(2.843, 2.744), rotate: 0,
  id: 'C38'
})
// control.amp.r1
const R32 = board.add(R_0603_1608Metric, {
  translate: pt(2.998, 2.744), rotate: 0,
  id: 'R32'
})
// control.amp.r2
const R33 = board.add(R_0603_1608Metric, {
  translate: pt(3.154, 2.744), rotate: 0,
  id: 'R33'
})
// control.hvclamp.res
const R34 = board.add(R_0603_1608Metric, {
  translate: pt(1.751, 2.841), rotate: 0,
  id: 'R34'
})
// control.driver.clamp1
const D10 = board.add(D_SOD_323, {
  translate: pt(2.653, 2.528), rotate: 0,
  id: 'D10'
})
// control.driver.clamp2
const D11 = board.add(D_SOD_323, {
  translate: pt(2.819, 2.528), rotate: 0,
  id: 'D11'
})
// control.driver.high_fet
const Q5 = board.add(TO_252_2, {
  translate: pt(2.826, 1.951), rotate: 0,
  id: 'Q5'
})
// control.driver.low_fet
const Q6 = board.add(TO_252_2, {
  translate: pt(1.944, 2.313), rotate: 0,
  id: 'Q6'
})
// control.driver.res
const R35 = board.add(R_0603_1608Metric, {
  translate: pt(1.907, 2.841), rotate: 0,
  id: 'R35'
})
// control.isense.ranges[0].pwr_sw.ic
const U11 = board.add(SMDIP_6_W7_62mm, {
  translate: pt(1.894, 1.975), rotate: 0,
  id: 'U11'
})
// control.isense.ranges[0].pwr_sw.res
const R36 = board.add(R_0603_1608Metric, {
  translate: pt(2.063, 2.841), rotate: 0,
  id: 'R36'
})
// control.isense.ranges[0].isense.res.res
const R37 = board.add(R_1206_3216Metric, {
  translate: pt(3.157, 2.220), rotate: 0,
  id: 'R37'
})
// control.isense.ranges[0].clamp.res
const R38 = board.add(R_0603_1608Metric, {
  translate: pt(2.219, 2.841), rotate: 0,
  id: 'R38'
})
// control.isense.ranges[0].sense_sw.device.ic
const U12 = board.add(SOT_23_6, {
  translate: pt(2.581, 2.243), rotate: 0,
  id: 'U12'
})
// control.isense.ranges[0].sense_sw.device.vdd_cap.cap
const C39 = board.add(C_0805_2012Metric, {
  translate: pt(1.979, 2.529), rotate: 0,
  id: 'C39'
})
// control.isense.ranges[1].pwr_sw.ic
const U13 = board.add(SMDIP_6_W7_62mm, {
  translate: pt(2.335, 1.975), rotate: 0,
  id: 'U13'
})
// control.isense.ranges[1].pwr_sw.res
const R39 = board.add(R_0603_1608Metric, {
  translate: pt(2.375, 2.841), rotate: 0,
  id: 'R39'
})
// control.isense.ranges[1].isense.res.res
const R40 = board.add(R_1206_3216Metric, {
  translate: pt(1.783, 2.535), rotate: 0,
  id: 'R40'
})
// control.isense.ranges[1].clamp.res
const R41 = board.add(R_0603_1608Metric, {
  translate: pt(2.531, 2.841), rotate: 0,
  id: 'R41'
})
// control.isense.ranges[1].sense_sw.device.ic
const U14 = board.add(SOT_23_6, {
  translate: pt(2.781, 2.243), rotate: 0,
  id: 'U14'
})
// control.isense.ranges[1].sense_sw.device.vdd_cap.cap
const C40 = board.add(C_0805_2012Metric, {
  translate: pt(2.152, 2.529), rotate: 0,
  id: 'C40'
})
// control.imeas.amp
const U15 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.315, 2.282), rotate: 0,
  id: 'U15'
})
// control.imeas.vdd_cap.cap
const C41 = board.add(C_0603_1608Metric, {
  translate: pt(2.687, 2.841), rotate: 0,
  id: 'C41'
})
// control.vmeas.r1
const R42 = board.add(R_0603_1608Metric, {
  translate: pt(2.843, 2.841), rotate: 0,
  id: 'R42'
})
// control.vmeas.r2
const R43 = board.add(R_0603_1608Metric, {
  translate: pt(2.998, 2.841), rotate: 0,
  id: 'R43'
})
// control.vmeas.rf
const R44 = board.add(R_0603_1608Metric, {
  translate: pt(3.154, 2.841), rotate: 0,
  id: 'R44'
})
// control.vmeas.rg
const R45 = board.add(R_0603_1608Metric, {
  translate: pt(1.751, 2.937), rotate: 0,
  id: 'R45'
})
// control.vclamp.res
const R46 = board.add(R_0603_1608Metric, {
  translate: pt(1.907, 2.937), rotate: 0,
  id: 'R46'
})
// pd.ic
const U16 = board.add(WQFN_14_1EP_2_5x2_5mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(0.573, 4.257), rotate: 0,
  id: 'U16'
})
// pd.vdd_cap[0].cap
const C42 = board.add(C_0603_1608Metric, {
  translate: pt(0.731, 4.398), rotate: 0,
  id: 'C42'
})
// pd.vdd_cap[1].cap
const C43 = board.add(C_0805_2012Metric, {
  translate: pt(0.567, 4.407), rotate: 0,
  id: 'C43'
})
// mcu.ic
const U17 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(3.504, 0.530), rotate: 0,
  id: 'U17'
})
// mcu.vcc_cap0.cap
const C44 = board.add(C_1206_3216Metric, {
  translate: pt(4.579, 0.242), rotate: 0,
  id: 'C44'
})
// mcu.vcc_cap1.cap
const C45 = board.add(C_0603_1608Metric, {
  translate: pt(4.767, 0.226), rotate: 0,
  id: 'C45'
})
// mcu.prog.conn
const J2 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(4.626, 0.079), rotate: 0,
  id: 'J2'
})
// mcu.en_pull.rc.r
const R47 = board.add(R_0603_1608Metric, {
  translate: pt(4.546, 0.356), rotate: 0,
  id: 'R47'
})
// mcu.en_pull.rc.c
const C46 = board.add(C_0603_1608Metric, {
  translate: pt(4.702, 0.356), rotate: 0,
  id: 'C46'
})
// led.package
const D12 = board.add(LED_0603_1608Metric, {
  translate: pt(4.220, 4.213), rotate: 0,
  id: 'D12'
})
// led.res
const R48 = board.add(R_0603_1608Metric, {
  translate: pt(4.220, 4.310), rotate: 0,
  id: 'R48'
})
// usb_esd
const U18 = board.add(SOT_23, {
  translate: pt(5.473, 4.633), rotate: 0,
  id: 'U18'
})
// i2c_tp.tp_scl.tp
const TP11 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.983, 4.221), rotate: 0,
  id: 'TP11'
})
// i2c_tp.tp_sda.tp
const TP12 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.983, 4.335), rotate: 0,
  id: 'TP12'
})
// i2c_pull.scl_res.res
const R49 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 4.594), rotate: 0,
  id: 'R49'
})
// i2c_pull.sda_res.res
const R50 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 4.691), rotate: 0,
  id: 'R50'
})
// oled.device.conn
const J3 = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(0.356, 1.577), rotate: 0,
  id: 'J3'
})
// oled.lcd
const U19 = board.add(Lcd_Er_Oled022_1_Outline, {
  translate: pt(1.220, 0.607), rotate: 0,
  id: 'U19'
})
// oled.iref_res
const R51 = board.add(R_0603_1608Metric, {
  translate: pt(1.377, 1.413), rotate: 0,
  id: 'R51'
})
// oled.vcomh_cap.cap
const C47 = board.add(C_1206_3216Metric, {
  translate: pt(0.843, 1.430), rotate: 0,
  id: 'C47'
})
// oled.vdd_cap1.cap
const C48 = board.add(C_0603_1608Metric, {
  translate: pt(1.533, 1.413), rotate: 0,
  id: 'C48'
})
// oled.vdd_cap2.cap
const C49 = board.add(C_0805_2012Metric, {
  translate: pt(1.039, 1.423), rotate: 0,
  id: 'C49'
})
// oled.vcc_cap1.cap
const C50 = board.add(C_0603_1608Metric, {
  translate: pt(1.689, 1.413), rotate: 0,
  id: 'C50'
})
// oled.vcc_cap2.cap
const C51 = board.add(C_0805_2012Metric, {
  translate: pt(1.213, 1.423), rotate: 0,
  id: 'C51'
})
// buck_rc.rc.r
const R52 = board.add(R_0603_1608Metric, {
  translate: pt(5.863, 4.213), rotate: 0,
  id: 'R52'
})
// buck_rc.rc.c
const C52 = board.add(C_0603_1608Metric, {
  translate: pt(5.863, 4.309), rotate: 0,
  id: 'C52'
})
// boost_rc.rc.r
const R53 = board.add(R_0603_1608Metric, {
  translate: pt(5.628, 4.213), rotate: 0,
  id: 'R53'
})
// boost_rc.rc.c
const C53 = board.add(C_0603_1608Metric, {
  translate: pt(5.628, 4.309), rotate: 0,
  id: 'C53'
})
// conv_comp.ic
const U20 = board.add(SOT_353_SC_70_5, {
  translate: pt(2.446, 4.239), rotate: 0,
  id: 'U20'
})
// conv_comp.vdd_cap.cap
const C54 = board.add(C_0603_1608Metric, {
  translate: pt(2.441, 4.362), rotate: 0,
  id: 'C54'
})
// comp_ref.div.top_res
const R54 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 4.594), rotate: 0,
  id: 'R54'
})
// comp_ref.div.bottom_res
const R55 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 4.691), rotate: 0,
  id: 'R55'
})
// comp_sense.div.top_res
const R56 = board.add(R_0603_1608Metric, {
  translate: pt(4.690, 4.213), rotate: 0,
  id: 'R56'
})
// comp_sense.div.bottom_res
const R57 = board.add(R_0603_1608Metric, {
  translate: pt(4.690, 4.309), rotate: 0,
  id: 'R57'
})
// conv_latch.ic
const U21 = board.add(VSSOP_8_2_4x2_1mm_P0_5mm, {
  translate: pt(2.713, 4.235), rotate: 0,
  id: 'U21'
})
// conv_latch.vdd_cap.cap
const C55 = board.add(C_0603_1608Metric, {
  translate: pt(2.685, 4.354), rotate: 0,
  id: 'C55'
})
// conv_en_pull.res
const R58 = board.add(R_0603_1608Metric, {
  translate: pt(4.752, 4.594), rotate: 0,
  id: 'R58'
})
// comp_pull.res
const R59 = board.add(R_0603_1608Metric, {
  translate: pt(5.221, 4.594), rotate: 0,
  id: 'R59'
})
// pass_temp.ic
const U22 = board.add(SOT_563, {
  translate: pt(3.455, 4.227), rotate: 0,
  id: 'U22'
})
// pass_temp.vdd_cap.cap
const C56 = board.add(C_0603_1608Metric, {
  translate: pt(3.460, 4.339), rotate: 0,
  id: 'C56'
})
// conv_temp.ic
const U23 = board.add(SOT_563, {
  translate: pt(3.220, 4.227), rotate: 0,
  id: 'U23'
})
// conv_temp.vdd_cap.cap
const C57 = board.add(C_0603_1608Metric, {
  translate: pt(3.225, 4.339), rotate: 0,
  id: 'C57'
})
// conv_sense.div.top_res
const R60 = board.add(R_0603_1608Metric, {
  translate: pt(4.455, 4.213), rotate: 0,
  id: 'R60'
})
// conv_sense.div.bottom_res
const R61 = board.add(R_0603_1608Metric, {
  translate: pt(4.455, 4.309), rotate: 0,
  id: 'R61'
})
// ioe.ic
const U24 = board.add(TSSOP_16_4_4x5mm_P0_65mm, {
  translate: pt(2.121, 3.833), rotate: 0,
  id: 'U24'
})
// ioe.vdd_cap.cap
const C58 = board.add(C_0603_1608Metric, {
  translate: pt(2.028, 4.010), rotate: 0,
  id: 'C58'
})
// enc.package
const SW1 = board.add(RotaryEncoder_Bourns_PEC11S, {
  translate: pt(3.758, 2.158), rotate: 0,
  id: 'SW1'
})
// dir.package
const SW2 = board.add(DirectionSwitch_Alps_SKRH, {
  translate: pt(2.676, 3.330), rotate: 0,
  id: 'SW2'
})
// rgb.package
const D13 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(2.033, 4.239), rotate: 0,
  id: 'D13'
})
// rgb.red_res
const R62 = board.add(R_0603_1608Metric, {
  translate: pt(2.172, 4.213), rotate: 0,
  id: 'R62'
})
// rgb.green_res
const R63 = board.add(R_0603_1608Metric, {
  translate: pt(2.050, 4.362), rotate: 0,
  id: 'R63'
})
// rgb.blue_res
const R64 = board.add(R_0603_1608Metric, {
  translate: pt(2.206, 4.362), rotate: 0,
  id: 'R64'
})
// qwiic_pull.scl_res.res
const R65 = board.add(R_0603_1608Metric, {
  translate: pt(5.159, 4.213), rotate: 0,
  id: 'R65'
})
// qwiic_pull.sda_res.res
const R66 = board.add(R_0603_1608Metric, {
  translate: pt(5.159, 4.309), rotate: 0,
  id: 'R66'
})
// qwiic.conn
const J4 = board.add(JST_SH_SM04B_SRSS_TB_1x04_1MP_P1_00mm_Horizontal, {
  translate: pt(1.061, 4.313), rotate: 0,
  id: 'J4'
})
// dutio.conn
const J5 = board.add(PinHeader_1x03_P2_54mm_Horizontal, {
  translate: pt(0.071, 3.995), rotate: 0,
  id: 'J5'
})
// touch_duck
const U25 = board.add(Symbol_DucklingSolid, {
  translate: pt(5.901, 4.566), rotate: 0,
  id: 'U25'
})
// fan_drv.pre
const Q7 = board.add(SOT_23, {
  translate: pt(4.104, 3.792), rotate: 0,
  id: 'Q7'
})
// fan_drv.pull
const R67 = board.add(R_0603_1608Metric, {
  translate: pt(4.278, 3.927), rotate: 0,
  id: 'R67'
})
// fan_drv.drv
const Q8 = board.add(SOT_23, {
  translate: pt(4.104, 3.965), rotate: 0,
  id: 'Q8'
})
// fan.conn
const J6 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.699, 4.314), rotate: 0,
  id: 'J6'
})
// dac.ic
const U26 = board.add(MSOP_10_3x3mm_P0_5mm, {
  translate: pt(0.730, 3.794), rotate: 0,
  id: 'U26'
})
// dac.vdd_cap[0].cap
const C59 = board.add(C_0603_1608Metric, {
  translate: pt(0.663, 3.931), rotate: 0,
  id: 'C59'
})
// dac.vdd_cap[1].cap
const C60 = board.add(C_0805_2012Metric, {
  translate: pt(0.961, 3.764), rotate: 0,
  id: 'C60'
})
// dac.out_cap[0]
const C61 = board.add(C_0603_1608Metric, {
  translate: pt(0.819, 3.931), rotate: 0,
  id: 'C61'
})
// dac.out_cap[1]
const C62 = board.add(C_0603_1608Metric, {
  translate: pt(0.974, 3.931), rotate: 0,
  id: 'C62'
})
// dac.out_cap[2]
const C63 = board.add(C_0603_1608Metric, {
  translate: pt(0.663, 4.028), rotate: 0,
  id: 'C63'
})
// dac_ferrite.fb
const FB2 = board.add(L_0603_1608Metric, {
  translate: pt(4.986, 4.594), rotate: 0,
  id: 'FB2'
})
// tp_cv.conn
const J7 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.396, 3.824), rotate: 0,
  id: 'J7'
})
// tp_cv.res
const R68 = board.add(R_0603_1608Metric, {
  translate: pt(5.374, 3.990), rotate: 0,
  id: 'R68'
})
// tp_cisrc.conn
const J8 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.108, 3.824), rotate: 0,
  id: 'J8'
})
// tp_cisrc.res
const R69 = board.add(R_0603_1608Metric, {
  translate: pt(5.087, 3.990), rotate: 0,
  id: 'R69'
})
// tp_cisnk.conn
const J9 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(4.533, 3.824), rotate: 0,
  id: 'J9'
})
// tp_cisnk.res
const R70 = board.add(R_0603_1608Metric, {
  translate: pt(4.512, 3.990), rotate: 0,
  id: 'R70'
})
// adc.ic
const U27 = board.add(TSSOP_20_4_4x6_5mm_P0_65mm, {
  translate: pt(1.344, 3.253), rotate: 0,
  id: 'U27'
})
// adc.avdd_res.res
const R71 = board.add(R_0603_1608Metric, {
  translate: pt(1.593, 3.260), rotate: 0,
  id: 'R71'
})
// adc.dvdd_res.res
const R72 = board.add(R_0603_1608Metric, {
  translate: pt(1.593, 3.357), rotate: 0,
  id: 'R72'
})
// adc.avdd_cap_0.cap
const C64 = board.add(C_0603_1608Metric, {
  translate: pt(1.250, 3.459), rotate: 0,
  id: 'C64'
})
// adc.avdd_cap_1.cap
const C65 = board.add(C_0603_1608Metric, {
  translate: pt(1.406, 3.459), rotate: 0,
  id: 'C65'
})
// adc.dvdd_cap_0.cap
const C66 = board.add(C_0603_1608Metric, {
  translate: pt(1.562, 3.459), rotate: 0,
  id: 'C66'
})
// adc.dvdd_cap_1.cap
const C67 = board.add(C_0603_1608Metric, {
  translate: pt(1.250, 3.556), rotate: 0,
  id: 'C67'
})
// adc.vref_cap.cap
const C68 = board.add(C_0805_2012Metric, {
  translate: pt(1.602, 3.154), rotate: 0,
  id: 'C68'
})
// tp_vcen.conn
const J10 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.683, 3.824), rotate: 0,
  id: 'J10'
})
// tp_vcen.res
const R73 = board.add(R_0603_1608Metric, {
  translate: pt(5.662, 3.990), rotate: 0,
  id: 'R73'
})
// vcen_rc.rc.r
const R74 = board.add(R_0603_1608Metric, {
  translate: pt(6.097, 4.213), rotate: 0,
  id: 'R74'
})
// vcen_rc.rc.c
const C69 = board.add(C_0603_1608Metric, {
  translate: pt(6.097, 4.309), rotate: 0,
  id: 'C69'
})
// tp_mi.conn
const J11 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(4.821, 3.824), rotate: 0,
  id: 'J11'
})
// tp_mi.res
const R75 = board.add(R_0603_1608Metric, {
  translate: pt(4.800, 3.990), rotate: 0,
  id: 'R75'
})
// mi_rc.rc.r
const R76 = board.add(R_0603_1608Metric, {
  translate: pt(4.924, 4.213), rotate: 0,
  id: 'R76'
})
// mi_rc.rc.c
const C70 = board.add(C_0603_1608Metric, {
  translate: pt(4.924, 4.309), rotate: 0,
  id: 'C70'
})
// tp_mv.conn
const J12 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.970, 3.824), rotate: 0,
  id: 'J12'
})
// tp_mv.res
const R77 = board.add(R_0603_1608Metric, {
  translate: pt(5.949, 3.990), rotate: 0,
  id: 'R77'
})
// mv_rc.rc.r
const R78 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 4.594), rotate: 0,
  id: 'R78'
})
// mv_rc.rc.c
const C71 = board.add(C_0603_1608Metric, {
  translate: pt(0.528, 4.691), rotate: 0,
  id: 'C71'
})
// outn
const J13 = board.add(CalTest_CT3151, {
  translate: pt(5.152, 2.199), rotate: 0,
  id: 'J13'
})
// outp
const J14 = board.add(CalTest_CT3151, {
  translate: pt(0.882, 3.500), rotate: 0,
  id: 'J14'
})
// outd
const J15 = board.add(PinHeader_1x02_P2_54mm_Horizontal, {
  translate: pt(3.707, 4.355), rotate: 0,
  id: 'J15'
})
// vimeas_amps.ic
const U28 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.706, 3.831), rotate: 0,
  id: 'U28'
})
// vimeas_amps.vdd_cap.cap
const C72 = board.add(C_0805_2012Metric, {
  translate: pt(1.627, 4.016), rotate: 0,
  id: 'C72'
})
// ampdmeas_amps.ic
const U29 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.296, 3.831), rotate: 0,
  id: 'U29'
})
// ampdmeas_amps.vdd_cap.cap
const C73 = board.add(C_0805_2012Metric, {
  translate: pt(1.218, 4.016), rotate: 0,
  id: 'C73'
})
// cd_amps.ic
const U30 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.537, 3.831), rotate: 0,
  id: 'U30'
})
// cd_amps.vdd_cap.cap
const C74 = board.add(C_0603_1608Metric, {
  translate: pt(2.449, 4.006), rotate: 0,
  id: 'C74'
})
// cv_amps.ic
const U31 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.946, 3.831), rotate: 0,
  id: 'U31'
})
// cv_amps.vdd_cap.cap
const C75 = board.add(C_0603_1608Metric, {
  translate: pt(2.859, 4.006), rotate: 0,
  id: 'C75'
})
// ci_amps.ic
const U32 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(3.765, 3.831), rotate: 0,
  id: 'U32'
})
// ci_amps.vdd_cap.cap
const C76 = board.add(C_0603_1608Metric, {
  translate: pt(3.678, 4.006), rotate: 0,
  id: 'C76'
})
// cintref_amps.ic
const U33 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(3.356, 3.831), rotate: 0,
  id: 'U33'
})
// cintref_amps.vdd_cap.cap
const C77 = board.add(C_0603_1608Metric, {
  translate: pt(3.268, 4.006), rotate: 0,
  id: 'C77'
})

board.setNetlist([
  {name: "gnd", pads: [["U18", "3"], ["J7", "2"], ["J8", "2"], ["J9", "2"], ["J10", "2"], ["J11", "2"], ["J12", "2"], ["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["C30", "2"], ["J13", "1"], ["J15", "1"], ["TP1", "1"], ["C1", "2"], ["D1", "2"], ["U1", "1"], ["U2", "1"], ["D2", "2"], ["D5", "2"], ["U5", "2"], ["U6", "2"], ["U7", "3"], ["U8", "2"], ["U9", "1"], ["U16", "8"], ["U16", "9"], ["U16", "15"], ["U17", "1"], ["U17", "40"], ["U17", "41"], ["U20", "2"], ["U21", "4"], ["U22", "2"], ["U22", "4"], ["U23", "2"], ["U24", "1"], ["U24", "2"], ["U24", "3"], ["U24", "8"], ["SW1", "C"], ["SW1", "S2"], ["SW2", "5"], ["J4", "1"], ["J5", "1"], ["Q7", "2"], ["J6", "1"], ["U26", "10"], ["U27", "2"], ["U27", "3"], ["U27", "19"], ["R11", "2"], ["C52", "2"], ["C53", "2"], ["R55", "2"], ["R57", "2"], ["R61", "2"], ["C69", "2"], ["C70", "2"], ["C71", "2"], ["J1", "S1"], ["R51", "2"], ["C61", "2"], ["C62", "2"], ["C63", "2"], ["C2", "2"], ["C6", "2"], ["C7", "2"], ["C27", "2"], ["C28", "2"], ["C29", "2"], ["U15", "2"], ["Q6", "2"], ["C42", "2"], ["C43", "2"], ["C44", "2"], ["C45", "2"], ["J2", "5"], ["J3", "3"], ["J3", "1"], ["J3", "24"], ["J3", "2"], ["J3", "12"], ["J3", "11"], ["J3", "16"], ["J3", "17"], ["J3", "18"], ["J3", "19"], ["J3", "20"], ["C47", "2"], ["C48", "2"], ["C49", "2"], ["C50", "2"], ["C51", "2"], ["C54", "2"], ["C55", "2"], ["C56", "2"], ["C57", "2"], ["C58", "2"], ["C59", "2"], ["C60", "2"], ["C64", "2"], ["C65", "2"], ["C66", "2"], ["C67", "2"], ["C68", "2"], ["R2", "2"], ["R9", "2"], ["R13", "2"], ["U30", "4"], ["U31", "4"], ["U33", "4"], ["U32", "4"], ["U10", "2"], ["C46", "2"], ["Q1", "3"], ["Q3", "3"], ["R42", "1"], ["J3", "7"], ["J3", "10"], ["J3", "8"], ["C4", "2"], ["C5", "2"], ["U3", "6"], ["U4", "6"], ["C24", "2"], ["C25", "2"], ["C31", "2"], ["C32", "2"], ["C35", "2"], ["C36", "2"], ["C41", "2"], ["C74", "2"], ["C75", "2"], ["C77", "2"], ["C76", "2"], ["C37", "2"], ["C8", "2"], ["C9", "2"], ["C10", "2"], ["C11", "2"], ["C12", "2"], ["C13", "2"], ["C14", "2"], ["C15", "2"], ["C16", "2"], ["C17", "2"], ["C18", "2"], ["C19", "2"], ["C20", "2"], ["C22", "2"], ["R36", "2"], ["R39", "2"], ["U12", "2"], ["U12", "4"], ["U14", "2"], ["U14", "4"], ["C39", "2"], ["C40", "2"]]},
  {name: "vusb", pads: [["U16", "2"], ["FB1", "2"], ["C1", "1"], ["D1", "1"], ["TP2", "1"], ["U1", "3"], ["R3", "1"], ["C2", "1"], ["C4", "1"], ["Q2", "2"], ["C8", "1"], ["C9", "1"], ["C10", "1"]]},
  {name: "v5", pads: [["TP3", "1"], ["U2", "3"], ["U5", "5"], ["U6", "1"], ["U7", "1"], ["U8", "5"], ["R67", "1"], ["Q8", "2"], ["R1", "1"], ["U5", "4"], ["U6", "3"], ["U8", "4"], ["C6", "1"], ["C27", "1"], ["C29", "1"], ["U3", "4"], ["U4", "4"], ["L3", "1"], ["L4", "1"], ["D3", "2"], ["D4", "2"], ["C24", "1"], ["C31", "1"], ["C20", "1"], ["C22", "1"], ["L1", "2"], ["C5", "1"]]},
  {name: "v3v3", pads: [["U9", "4"], ["U9", "5"], ["U2", "2"], ["D2", "1"], ["TP4", "1"], ["U16", "3"], ["U16", "4"], ["U17", "2"], ["D12", "2"], ["U20", "5"], ["U21", "8"], ["R58", "1"], ["R59", "1"], ["U22", "5"], ["U23", "4"], ["U23", "5"], ["U24", "16"], ["D13", "2"], ["J4", "2"], ["R54", "1"], ["R72", "1"], ["C7", "1"], ["C42", "1"], ["C43", "1"], ["C44", "1"], ["C45", "1"], ["J2", "1"], ["R49", "1"], ["R50", "1"], ["J3", "5"], ["C48", "1"], ["C49", "1"], ["C54", "1"], ["C55", "1"], ["C56", "1"], ["C57", "1"], ["C58", "1"], ["R65", "1"], ["R66", "1"], ["R47", "1"], ["J3", "6"]]},
  {name: "vconv", pads: [["D5", "1"], ["TP5", "1"], ["Q5", "2"], ["R56", "1"], ["R60", "1"], ["Q4", "2"], ["C11", "1"], ["C12", "1"], ["C13", "1"], ["C14", "1"], ["C15", "1"], ["C16", "1"], ["C17", "1"], ["C18", "1"], ["C19", "1"]]},
  {name: "v12", pads: [["TP6", "1"], ["D6", "1"], ["C26", "1"], ["R8", "1"], ["C25", "1"], ["J3", "23"], ["C50", "1"], ["C51", "1"]]},
  {name: "vanalog", pads: [["U6", "5"], ["TP7", "1"], ["R71", "1"], ["C28", "1"], ["U15", "6"], ["U30", "8"], ["U10", "5"], ["U33", "8"], ["U32", "8"], ["U31", "8"], ["C41", "1"], ["C74", "1"], ["C37", "1"], ["C77", "1"], ["C76", "1"], ["C75", "1"]]},
  {name: "vref", pads: [["U7", "2"], ["TP8", "1"], ["FB2", "1"], ["U27", "4"], ["R10", "1"], ["C68", "1"]]},
  {name: "vcenter", pads: [["U33", "6"], ["R73", "1"], ["R74", "1"], ["U33", "3"], ["U33", "7"], ["R17", "1"], ["R45", "1"], ["R33", "2"], ["R19", "1"], ["U15", "7"], ["U15", "3"]]},
  {name: "vcontrol", pads: [["TP9", "1"], ["D7", "1"], ["C33", "1"], ["R12", "1"], ["C32", "1"], ["U29", "8"], ["U28", "8"], ["C73", "1"], ["C72", "1"], ["U12", "5"], ["U14", "5"], ["C39", "1"], ["C40", "1"]]},
  {name: "vcontroln", pads: [["U9", "2"], ["TP10", "1"], ["U29", "4"], ["U28", "4"], ["C73", "2"], ["C72", "2"], ["C35", "1"], ["C36", "1"]]},
  {name: "usb.pwr", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["FB1", "1"]]},
  {name: "ref_div.output", pads: [["U33", "5"], ["C30", "1"], ["R10", "2"], ["R11", "1"]]},
  {name: "usb.cc.cc1", pads: [["J1", "A5"], ["U16", "10"], ["U16", "11"]]},
  {name: "usb.cc.cc2", pads: [["J1", "B5"], ["U16", "1"], ["U16", "14"]]},
  {name: "mcu.program_boot_node", pads: [["R48", "2"], ["U17", "27"], ["J2", "2"]]},
  {name: "usb_chain_0.d_P", pads: [["J1", "A6"], ["J1", "B6"], ["U18", "2"], ["U17", "14"]]},
  {name: "usb_chain_0.d_N", pads: [["J1", "A7"], ["J1", "B7"], ["U18", "1"], ["U17", "13"]]},
  {name: "i2c_pull.i2c.scl", pads: [["U17", "39"], ["U16", "6"], ["U22", "1"], ["U23", "1"], ["U24", "14"], ["U26", "2"], ["R49", "2"], ["TP11", "1"], ["J3", "13"]]},
  {name: "i2c_pull.i2c.sda", pads: [["U17", "38"], ["U16", "7"], ["U22", "6"], ["U23", "6"], ["U24", "15"], ["U26", "3"], ["R50", "2"], ["TP12", "1"], ["J3", "14"], ["J3", "15"]]},
  {name: "pd.int", pads: [["U17", "21"], ["U16", "5"]]},
  {name: "oled.reset", pads: [["U17", "20"], ["J3", "9"]]},
  {name: "mcu.gpio.irange_0", pads: [["U17", "12"], ["U12", "3"], ["U11", "1"]]},
  {name: "mcu.gpio.irange_1", pads: [["U17", "11"], ["U14", "3"], ["U13", "1"]]},
  {name: "mcu.gpio.off_0", pads: [["U17", "31"], ["U10", "6"]]},
  {name: "buck_rc.input", pads: [["U17", "35"], ["R52", "1"]]},
  {name: "buck_rc.output", pads: [["U3", "2"], ["R52", "2"], ["C52", "1"]]},
  {name: "boost_rc.input", pads: [["U17", "32"], ["R53", "1"]]},
  {name: "boost_rc.output", pads: [["U4", "2"], ["R53", "2"], ["C53", "1"]]},
  {name: "comp_ref.output", pads: [["U20", "1"], ["R54", "2"], ["R55", "1"]]},
  {name: "comp_sense.output", pads: [["U20", "3"], ["R56", "2"], ["R57", "1"]]},
  {name: "conv_en_pull.io", pads: [["U17", "33"], ["U21", "6"], ["R58", "2"]]},
  {name: "conv_comp.out", pads: [["U20", "4"], ["U21", "7"], ["R59", "2"]]},
  {name: "conv_latch.nq", pads: [["U21", "3"], ["U17", "23"], ["U3", "3"], ["U4", "3"]]},
  {name: "conv_sense.output", pads: [["U17", "18"], ["R60", "2"], ["R61", "1"]]},
  {name: "enc.a", pads: [["U17", "5"], ["SW1", "A"]]},
  {name: "enc.b", pads: [["U17", "6"], ["SW1", "B"]]},
  {name: "enc.sw", pads: [["U17", "4"], ["SW1", "S1"]]},
  {name: "dir.a", pads: [["U24", "5"], ["SW2", "1"]]},
  {name: "dir.b", pads: [["U24", "6"], ["SW2", "4"]]},
  {name: "dir.c", pads: [["U24", "9"], ["SW2", "3"]]},
  {name: "dir.d", pads: [["U24", "7"], ["SW2", "6"]]},
  {name: "dir.center", pads: [["U24", "4"], ["SW2", "2"]]},
  {name: "ioe.io.rgb_red", pads: [["U24", "11"], ["R62", "2"]]},
  {name: "ioe.io.rgb_green", pads: [["U24", "12"], ["R63", "2"]]},
  {name: "ioe.io.rgb_blue", pads: [["U24", "10"], ["R64", "2"]]},
  {name: "qwiic_pull.i2c.scl", pads: [["U17", "24"], ["R65", "2"], ["J4", "4"]]},
  {name: "qwiic_pull.i2c.sda", pads: [["U17", "25"], ["J4", "3"], ["R66", "2"]]},
  {name: "dutio.io0", pads: [["U17", "15"], ["J5", "2"]]},
  {name: "dutio.io1", pads: [["U17", "17"], ["J5", "3"]]},
  {name: "touch_duck.pad", pads: [["U17", "22"], ["U25", "1"]]},
  {name: "fan_drv.control", pads: [["U17", "19"], ["Q7", "1"]]},
  {name: "fan.pwr", pads: [["J6", "2"], ["Q8", "3"]]},
  {name: "dac_ferrite.pwr_out", pads: [["FB2", "2"], ["U26", "1"], ["U26", "4"], ["C59", "1"], ["C60", "1"]]},
  {name: "dac.out0", pads: [["U26", "6"], ["R68", "1"], ["R22", "1"], ["C61", "1"]]},
  {name: "dac.out1", pads: [["U26", "7"], ["R69", "1"], ["R28", "1"], ["C62", "1"]]},
  {name: "dac.out2", pads: [["U26", "8"], ["R70", "1"], ["R25", "1"], ["C63", "1"]]},
  {name: "adc.spi.sck", pads: [["U27", "14"], ["U17", "8"]]},
  {name: "adc.spi.mosi", pads: [["U27", "15"], ["U17", "9"]]},
  {name: "adc.spi.miso", pads: [["U27", "16"], ["U17", "10"]]},
  {name: "adc.cs", pads: [["U27", "13"], ["U17", "7"]]},
  {name: "vcen_rc.output", pads: [["U27", "5"], ["R74", "2"], ["C69", "1"]]},
  {name: "control.meas_i", pads: [["U15", "5"], ["R75", "1"], ["R76", "1"], ["R26", "1"], ["R29", "1"]]},
  {name: "mi_rc.output", pads: [["U27", "6"], ["R76", "2"], ["C70", "1"]]},
  {name: "control.measured_voltage", pads: [["U31", "3"], ["R77", "1"], ["R78", "1"], ["R46", "2"]]},
  {name: "mv_rc.output", pads: [["U27", "7"], ["R78", "2"], ["C71", "1"]]},
  {name: "outp.port", pads: [["J14", "1"], ["J15", "2"], ["R34", "1"], ["R37", "2"], ["R40", "2"], ["U15", "1"]]},
  {name: "vimeas_amps.inp.0", pads: [["U28", "3"], ["R43", "2"], ["R45", "2"]]},
  {name: "vimeas_amps.inn.0", pads: [["U28", "2"], ["R42", "2"], ["R44", "2"]]},
  {name: "vimeas_amps.out.0", pads: [["U28", "1"], ["R44", "1"], ["R46", "1"]]},
  {name: "vimeas_amps.inp.1", pads: [["U28", "5"], ["R34", "2"]]},
  {name: "control.outa", pads: [["U28", "6"], ["U28", "7"], ["R14", "1"], ["R43", "1"]]},
  {name: "ampdmeas_amps.inp.0", pads: [["U29", "3"], ["U33", "1"], ["C38", "1"]]},
  {name: "ampdmeas_amps.inn.0", pads: [["U29", "2"], ["R32", "2"], ["R33", "1"]]},
  {name: "control.drive", pads: [["U29", "1"], ["R32", "1"], ["R15", "1"], ["R35", "2"]]},
  {name: "ampdmeas_amps.inp.1", pads: [["U29", "5"], ["R15", "2"], ["R17", "2"]]},
  {name: "ampdmeas_amps.inn.1", pads: [["U29", "6"], ["R14", "2"], ["R16", "2"]]},
  {name: "ampdmeas_amps.out.1", pads: [["U29", "7"], ["R16", "1"], ["R18", "1"]]},
  {name: "cd_amps.inp.0", pads: [["U30", "3"], ["R18", "2"]]},
  {name: "cd_amps.inn.0", pads: [["U30", "2"], ["U30", "1"], ["R20", "1"]]},
  {name: "cd_amps.inp.1", pads: [["U30", "5"], ["R19", "2"], ["R20", "2"]]},
  {name: "cd_amps.inn.1", pads: [["U30", "6"], ["R21", "2"], ["U10", "1"]]},
  {name: "cd_amps.out.1", pads: [["U30", "7"], ["R21", "1"]]},
  {name: "control.meas_v", pads: [["U31", "2"], ["U31", "1"], ["R23", "1"]]},
  {name: "cv_amps.inp.1", pads: [["U31", "5"], ["R22", "2"], ["R23", "2"]]},
  {name: "cv_amps.inn.1", pads: [["U31", "6"], ["R24", "2"], ["U10", "3"], ["U32", "6"], ["U32", "2"], ["R27", "2"], ["R30", "2"]]},
  {name: "cv_amps.out.1", pads: [["U31", "7"], ["R24", "1"]]},
  {name: "ci_amps.inp.0", pads: [["U32", "3"], ["R28", "2"], ["R29", "2"]]},
  {name: "ci_amps.out.0", pads: [["U32", "1"], ["D9", "1"]]},
  {name: "ci_amps.inp.1", pads: [["U32", "5"], ["R25", "2"], ["R26", "2"]]},
  {name: "ci_amps.out.1", pads: [["U32", "7"], ["D8", "2"]]},
  {name: "cintref_amps.inn.0", pads: [["U33", "2"], ["R31", "2"], ["C38", "2"]]},
  {name: "reg_v5.fb.output", pads: [["U1", "4"], ["R1", "2"], ["R2", "1"]]},
  {name: "reg_v5.boot_cap.neg", pads: [["C3", "2"], ["U1", "2"], ["L1", "1"]]},
  {name: "reg_v5.boot_cap.pos", pads: [["C3", "1"], ["U1", "6"]]},
  {name: "reg_v5.en_res.b", pads: [["R3", "2"], ["U1", "5"]]},
  {name: "conv.sw_in_force", pads: [["Q1", "2"], ["Q2", "3"], ["L2", "1"], ["U3", "7"], ["C21", "2"]]},
  {name: "conv.sw_out_force", pads: [["L2", "2"], ["Q3", "2"], ["Q4", "3"], ["U4", "7"], ["C23", "2"]]},
  {name: "conv.buck_sw.low_gate_res.a", pads: [["R4", "1"], ["U3", "5"]]},
  {name: "conv.buck_sw.low_gate_res.b", pads: [["R4", "2"], ["Q1", "1"]]},
  {name: "conv.buck_sw.high_gate_res.a", pads: [["R5", "1"], ["U3", "8"]]},
  {name: "conv.buck_sw.high_gate_res.b", pads: [["R5", "2"], ["Q2", "1"]]},
  {name: "conv.buck_sw.driver.ic.bst", pads: [["U3", "1"], ["D3", "1"], ["C21", "1"]]},
  {name: "conv.boost_sw.low_gate_res.a", pads: [["R6", "1"], ["U4", "5"]]},
  {name: "conv.boost_sw.low_gate_res.b", pads: [["R6", "2"], ["Q3", "1"]]},
  {name: "conv.boost_sw.high_gate_res.a", pads: [["R7", "1"], ["U4", "8"]]},
  {name: "conv.boost_sw.high_gate_res.b", pads: [["R7", "2"], ["Q4", "1"]]},
  {name: "conv.boost_sw.driver.ic.bst", pads: [["U4", "1"], ["D4", "1"], ["C23", "1"]]},
  {name: "reg_v12.fb.output", pads: [["U5", "3"], ["C26", "2"], ["R8", "2"], ["R9", "1"]]},
  {name: "reg_v12.power_path.switch", pads: [["U5", "1"], ["L3", "2"], ["D6", "2"]]},
  {name: "reg_vcontrol.fb.output", pads: [["U8", "3"], ["C33", "2"], ["R12", "2"], ["R13", "1"]]},
  {name: "reg_vcontrol.power_path.switch", pads: [["U8", "1"], ["L4", "2"], ["D7", "2"]]},
  {name: "reg_vcontroln.cf.neg", pads: [["C34", "2"], ["U9", "3"]]},
  {name: "reg_vcontroln.cf.pos", pads: [["C34", "1"], ["U9", "6"]]},
  {name: "control.int_link", pads: [["U10", "4"], ["R31", "1"]]},
  {name: "control.driver.out", pads: [["D11", "2"], ["Q6", "3"], ["Q5", "3"], ["U11", "4"], ["U13", "4"]]},
  {name: "control.isense.sense_in", pads: [["U15", "8"], ["U12", "6"], ["U14", "6"]]},
  {name: "control.err_source.diode.cathode", pads: [["D8", "1"], ["R27", "1"]]},
  {name: "control.err_sink.diode.anode", pads: [["D9", "2"], ["R30", "1"]]},
  {name: "control.driver.res.a", pads: [["R35", "1"], ["D10", "2"], ["Q5", "1"], ["Q6", "1"]]},
  {name: "control.driver.clamp1.cathode", pads: [["D10", "1"], ["D11", "1"]]},
  {name: "control.isense.ranges[0].pwr_sw.pwr_out", pads: [["U11", "6"], ["R37", "1"], ["R38", "1"]]},
  {name: "control.isense.ranges[0].clamp.signal_out", pads: [["R38", "2"], ["U12", "1"]]},
  {name: "control.isense.ranges[0].pwr_sw.res.a", pads: [["R36", "1"], ["U11", "2"]]},
  {name: "control.isense.ranges[1].pwr_sw.pwr_out", pads: [["U13", "6"], ["R40", "1"], ["R41", "1"]]},
  {name: "control.isense.ranges[1].clamp.signal_out", pads: [["R41", "2"], ["U14", "1"]]},
  {name: "control.isense.ranges[1].pwr_sw.res.a", pads: [["R39", "1"], ["U13", "2"]]},
  {name: "pd.ic.vconn", pads: [["U16", "12"], ["U16", "13"]]},
  {name: "mcu.program_uart_node.a_tx", pads: [["U17", "37"], ["J2", "3"]]},
  {name: "mcu.program_uart_node.b_tx", pads: [["U17", "36"], ["J2", "4"]]},
  {name: "mcu.program_en_node", pads: [["U17", "3"], ["J2", "6"], ["R47", "2"], ["C46", "1"]]},
  {name: "led.res.a", pads: [["R48", "1"], ["D12", "1"]]},
  {name: "oled.iref_res.a", pads: [["R51", "1"], ["J3", "21"]]},
  {name: "oled.device.vcomh", pads: [["J3", "22"], ["C47", "1"]]},
  {name: "conv_latch.clk", pads: [["U21", "1"]]},
  {name: "conv_latch.d", pads: [["U21", "2"]]},
  {name: "conv_latch.q", pads: [["U21", "5"]]},
  {name: "pass_temp.alert", pads: [["U22", "3"]]},
  {name: "conv_temp.alert", pads: [["U23", "3"]]},
  {name: "rgb.red_res.a", pads: [["R62", "1"], ["D13", "3"]]},
  {name: "rgb.green_res.a", pads: [["R63", "1"], ["D13", "4"]]},
  {name: "rgb.blue_res.a", pads: [["R64", "1"], ["D13", "1"]]},
  {name: "fan_drv.pre.drain", pads: [["Q7", "3"], ["R67", "2"], ["Q8", "1"]]},
  {name: "dac.out3", pads: [["U26", "9"]]},
  {name: "dac.rdy", pads: [["U26", "5"]]},
  {name: "tp_cv.res.b", pads: [["R68", "2"], ["J7", "1"]]},
  {name: "tp_cisrc.res.b", pads: [["R69", "2"], ["J8", "1"]]},
  {name: "tp_cisnk.res.b", pads: [["R70", "2"], ["J9", "1"]]},
  {name: "adc.vins.3", pads: [["U27", "8"]]},
  {name: "adc.vins.4", pads: [["U27", "9"]]},
  {name: "adc.vins.5", pads: [["U27", "10"]]},
  {name: "adc.vins.6", pads: [["U27", "11"]]},
  {name: "adc.vins.7", pads: [["U27", "12"]]},
  {name: "adc.ic.avdd", pads: [["U27", "1"], ["R71", "2"], ["C64", "1"], ["C65", "1"]]},
  {name: "adc.ic.dvdd", pads: [["U27", "20"], ["R72", "2"], ["C66", "1"], ["C67", "1"]]},
  {name: "tp_vcen.res.b", pads: [["R73", "2"], ["J10", "1"]]},
  {name: "tp_mi.res.b", pads: [["R75", "2"], ["J11", "1"]]},
  {name: "tp_mv.res.b", pads: [["R77", "2"], ["J12", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(6.273818897637796, 4.838188976377953);
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


