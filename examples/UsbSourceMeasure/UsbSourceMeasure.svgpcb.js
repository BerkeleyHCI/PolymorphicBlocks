const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.425, 5.093), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.465, 5.093), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.425, 5.132), rotate: 0,
  id: 'H3'
})
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(4.210, 3.545), rotate: 0,
  id: 'J1'
})
// tp_gnd.tp
const TP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.959, 4.858), rotate: 0,
  id: 'TP1'
})
// vusb_sense.ic
const U1 = board.add(SOT_23_8, {
  translate: pt(0.914, 4.507), rotate: 0,
  id: 'U1'
})
// vusb_sense.vs_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(1.063, 4.642), rotate: 0,
  id: 'C1'
})
// vusb_sense.Rs.res.res
const R1 = board.add(R_0805_2012Metric, {
  translate: pt(0.899, 4.651), rotate: 0,
  id: 'R1'
})
// filt_vusb.fb
const FB1 = board.add(L_1206_3216Metric, {
  translate: pt(2.683, 4.868), rotate: 0,
  id: 'FB1'
})
// fuse_vusb.fuse
const F1 = board.add(Fuseholder_Littelfuse_Nano2_154x, {
  translate: pt(2.134, 4.549), rotate: 0,
  id: 'F1'
})
// prot_vusb.diode
const D1 = board.add(D_SMA, {
  translate: pt(1.546, 4.889), rotate: 0,
  id: 'D1'
})
// tp_vusb.tp
const TP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.210, 4.858), rotate: 0,
  id: 'TP2'
})
// reg_v5.ic
const U2 = board.add(SOT_23_6, {
  translate: pt(2.127, 3.447), rotate: 0,
  id: 'U2'
})
// reg_v5.fb.div.top_res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(2.239, 3.666), rotate: 0,
  id: 'R2'
})
// reg_v5.fb.div.bottom_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(1.845, 3.796), rotate: 0,
  id: 'R3'
})
// reg_v5.hf_in_cap.cap
const C2 = board.add(C_0603_1608Metric, {
  translate: pt(2.001, 3.796), rotate: 0,
  id: 'C2'
})
// reg_v5.boot_cap
const C3 = board.add(C_0603_1608Metric, {
  translate: pt(2.157, 3.796), rotate: 0,
  id: 'C3'
})
// reg_v5.power_path.inductor
const L1 = board.add(L_Sunlord_SWPA5040S, {
  translate: pt(1.897, 3.489), rotate: 0,
  id: 'L1'
})
// reg_v5.power_path.in_cap.cap
const C4 = board.add(C_0805_2012Metric, {
  translate: pt(2.074, 3.676), rotate: 0,
  id: 'C4'
})
// reg_v5.power_path.out_cap.cap
const C5 = board.add(C_1206_3216Metric, {
  translate: pt(1.877, 3.682), rotate: 0,
  id: 'C5'
})
// reg_v5.en_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(2.313, 3.796), rotate: 0,
  id: 'R4'
})
// tp_v5.tp
const TP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.460, 4.858), rotate: 0,
  id: 'TP3'
})
// reg_3v3.ic
const U3 = board.add(SOT_23_6, {
  translate: pt(3.282, 3.447), rotate: 0,
  id: 'U3'
})
// reg_3v3.fb.div.top_res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(3.480, 3.626), rotate: 0,
  id: 'R5'
})
// reg_3v3.fb.div.bottom_res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(3.039, 3.756), rotate: 0,
  id: 'R6'
})
// reg_3v3.hf_in_cap.cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(3.195, 3.756), rotate: 0,
  id: 'C6'
})
// reg_3v3.boot_cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(3.351, 3.756), rotate: 0,
  id: 'C7'
})
// reg_3v3.power_path.inductor
const L2 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(3.072, 3.469), rotate: 0,
  id: 'L2'
})
// reg_3v3.power_path.in_cap.cap.c[0]
const C8 = board.add(C_1206_3216Metric, {
  translate: pt(3.493, 3.426), rotate: 0,
  id: 'C8'
})
// reg_3v3.power_path.in_cap.cap.c[1]
const C9 = board.add(C_1206_3216Metric, {
  translate: pt(3.072, 3.643), rotate: 0,
  id: 'C9'
})
// reg_3v3.power_path.out_cap.cap
const C10 = board.add(C_1206_3216Metric, {
  translate: pt(3.292, 3.643), rotate: 0,
  id: 'C10'
})
// reg_3v3.en_res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(3.507, 3.756), rotate: 0,
  id: 'R7'
})
// prot_3v3.diode
const D2 = board.add(D_SMA, {
  translate: pt(1.940, 4.889), rotate: 0,
  id: 'D2'
})
// tp_3v3.tp
const TP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.711, 4.858), rotate: 0,
  id: 'TP4'
})
// convin_sense.ic
const U4 = board.add(SOT_23_8, {
  translate: pt(1.320, 4.507), rotate: 0,
  id: 'U4'
})
// convin_sense.vs_cap.cap
const C11 = board.add(C_0603_1608Metric, {
  translate: pt(1.469, 4.642), rotate: 0,
  id: 'C11'
})
// convin_sense.Rs.res.res
const R8 = board.add(R_0805_2012Metric, {
  translate: pt(1.306, 4.651), rotate: 0,
  id: 'R8'
})
// precharge.switch.pre
const Q1 = board.add(SOT_23, {
  translate: pt(5.194, 2.132), rotate: 0,
  id: 'Q1'
})
// precharge.switch.pull
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(4.836, 2.285), rotate: 0,
  id: 'R9'
})
// precharge.switch.drv
const Q2 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(4.924, 1.920), rotate: 0,
  id: 'Q2'
})
// precharge.res.res
const R10 = board.add(R_2512_6332Metric, {
  translate: pt(4.928, 2.141), rotate: 0,
  id: 'R10'
})
// cap_conv.cap
const C12 = board.add(CP_Elec_8x10, {
  translate: pt(4.754, 3.554), rotate: 0,
  id: 'C12'
})
// conv.power_path.inductor
const L3 = board.add(L_Bourns_SRP1245A, {
  translate: pt(2.469, 2.069), rotate: 0,
  id: 'L3'
})
// conv.power_path.in_cap.cap.c[0]
const C13 = board.add(C_1206_3216Metric, {
  translate: pt(2.270, 2.725), rotate: 0,
  id: 'C13'
})
// conv.power_path.in_cap.cap.c[1]
const C14 = board.add(C_1206_3216Metric, {
  translate: pt(2.491, 2.725), rotate: 0,
  id: 'C14'
})
// conv.power_path.in_cap.cap.c[2]
const C15 = board.add(C_1206_3216Metric, {
  translate: pt(2.711, 2.725), rotate: 0,
  id: 'C15'
})
// conv.power_path.out_cap.cap.c[0]
const C16 = board.add(C_1206_3216Metric, {
  translate: pt(2.931, 2.725), rotate: 0,
  id: 'C16'
})
// conv.power_path.out_cap.cap.c[1]
const C17 = board.add(C_1206_3216Metric, {
  translate: pt(3.152, 2.725), rotate: 0,
  id: 'C17'
})
// conv.power_path.out_cap.cap.c[2]
const C18 = board.add(C_1206_3216Metric, {
  translate: pt(3.372, 2.725), rotate: 0,
  id: 'C18'
})
// conv.power_path.out_cap.cap.c[3]
const C19 = board.add(C_1206_3216Metric, {
  translate: pt(3.593, 2.725), rotate: 0,
  id: 'C19'
})
// conv.power_path.out_cap.cap.c[4]
const C20 = board.add(C_1206_3216Metric, {
  translate: pt(2.270, 2.855), rotate: 0,
  id: 'C20'
})
// conv.power_path.out_cap.cap.c[5]
const C21 = board.add(C_1206_3216Metric, {
  translate: pt(2.491, 2.855), rotate: 0,
  id: 'C21'
})
// conv.power_path.out_cap.cap.c[6]
const C22 = board.add(C_1206_3216Metric, {
  translate: pt(2.711, 2.855), rotate: 0,
  id: 'C22'
})
// conv.power_path.out_cap.cap.c[7]
const C23 = board.add(C_1206_3216Metric, {
  translate: pt(2.931, 2.855), rotate: 0,
  id: 'C23'
})
// conv.power_path.out_cap.cap.c[8]
const C24 = board.add(C_1206_3216Metric, {
  translate: pt(3.152, 2.855), rotate: 0,
  id: 'C24'
})
// conv.buck_sw.driver.ic
const U5 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(3.278, 2.471), rotate: 0,
  id: 'U5'
})
// conv.buck_sw.driver.cap.cap
const C25 = board.add(C_0603_1608Metric, {
  translate: pt(3.672, 2.838), rotate: 0,
  id: 'C25'
})
// conv.buck_sw.driver.high_cap.cap
const C26 = board.add(C_0603_1608Metric, {
  translate: pt(2.238, 2.968), rotate: 0,
  id: 'C26'
})
// conv.buck_sw.driver.boot
const D3 = board.add(D_SOD_323, {
  translate: pt(3.345, 2.847), rotate: 0,
  id: 'D3'
})
// conv.buck_sw.low_fet
const Q3 = board.add(TO_252_2, {
  translate: pt(3.049, 1.951), rotate: 0,
  id: 'Q3'
})
// conv.buck_sw.low_gate_res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(2.394, 2.968), rotate: 0,
  id: 'R11'
})
// conv.buck_sw.high_fet
const Q4 = board.add(TO_252_2, {
  translate: pt(3.526, 1.951), rotate: 0,
  id: 'Q4'
})
// conv.buck_sw.high_gate_res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(2.550, 2.968), rotate: 0,
  id: 'R12'
})
// conv.boost_sw.driver.ic
const U6 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(3.609, 2.471), rotate: 0,
  id: 'U6'
})
// conv.boost_sw.driver.cap.cap
const C27 = board.add(C_0603_1608Metric, {
  translate: pt(2.706, 2.968), rotate: 0,
  id: 'C27'
})
// conv.boost_sw.driver.high_cap.cap
const C28 = board.add(C_0603_1608Metric, {
  translate: pt(2.861, 2.968), rotate: 0,
  id: 'C28'
})
// conv.boost_sw.driver.boot
const D4 = board.add(D_SOD_323, {
  translate: pt(3.511, 2.847), rotate: 0,
  id: 'D4'
})
// conv.boost_sw.low_fet
const Q5 = board.add(TO_252_2, {
  translate: pt(2.431, 2.502), rotate: 0,
  id: 'Q5'
})
// conv.boost_sw.low_gate_res
const R13 = board.add(R_0603_1608Metric, {
  translate: pt(3.017, 2.968), rotate: 0,
  id: 'R13'
})
// conv.boost_sw.high_fet
const Q6 = board.add(TO_252_2, {
  translate: pt(2.907, 2.502), rotate: 0,
  id: 'Q6'
})
// conv.boost_sw.high_gate_res
const R14 = board.add(R_0603_1608Metric, {
  translate: pt(3.173, 2.968), rotate: 0,
  id: 'R14'
})
// prot_conv.diode
const D5 = board.add(D_SMA, {
  translate: pt(2.334, 4.889), rotate: 0,
  id: 'D5'
})
// tp_conv.tp
const TP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.961, 4.858), rotate: 0,
  id: 'TP5'
})
// reg_v12.ic
const U7 = board.add(SOT_23_5, {
  translate: pt(5.160, 3.447), rotate: 0,
  id: 'U7'
})
// reg_v12.fb.div.top_res
const R15 = board.add(R_0603_1608Metric, {
  translate: pt(5.480, 3.582), rotate: 0,
  id: 'R15'
})
// reg_v12.fb.div.bottom_res
const R16 = board.add(R_0603_1608Metric, {
  translate: pt(5.137, 3.696), rotate: 0,
  id: 'R16'
})
// reg_v12.power_path.inductor
const L4 = board.add(L_0805_2012Metric, {
  translate: pt(5.314, 3.587), rotate: 0,
  id: 'L4'
})
// reg_v12.power_path.in_cap.cap
const C29 = board.add(C_0805_2012Metric, {
  translate: pt(5.347, 3.419), rotate: 0,
  id: 'C29'
})
// reg_v12.power_path.out_cap.cap
const C30 = board.add(C_0603_1608Metric, {
  translate: pt(5.293, 3.696), rotate: 0,
  id: 'C30'
})
// reg_v12.cf
const C31 = board.add(C_0603_1608Metric, {
  translate: pt(5.449, 3.696), rotate: 0,
  id: 'C31'
})
// reg_v12.rect
const D6 = board.add(D_SOD_323, {
  translate: pt(5.143, 3.591), rotate: 0,
  id: 'D6'
})
// tp_v12.tp
const TP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.211, 4.858), rotate: 0,
  id: 'TP6'
})
// reg_analog.ic
const U8 = board.add(SOT_23_5, {
  translate: pt(3.782, 3.447), rotate: 0,
  id: 'U8'
})
// reg_analog.in_cap.cap
const C32 = board.add(C_0603_1608Metric, {
  translate: pt(3.760, 3.712), rotate: 0,
  id: 'C32'
})
// reg_analog.out_cap.cap
const C33 = board.add(C_1206_3216Metric, {
  translate: pt(3.792, 3.599), rotate: 0,
  id: 'C33'
})
// tp_analog.tp
const TP7 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.462, 4.858), rotate: 0,
  id: 'TP7'
})
// reg_vref.ic
const U9 = board.add(SOT_23, {
  translate: pt(1.721, 4.507), rotate: 0,
  id: 'U9'
})
// reg_vref.in_cap.cap
const C34 = board.add(C_0603_1608Metric, {
  translate: pt(1.704, 4.642), rotate: 0,
  id: 'C34'
})
// tp_vref.tp
const TP8 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.712, 4.858), rotate: 0,
  id: 'TP8'
})
// ref_div.div.top_res
const R17 = board.add(R_0603_1608Metric, {
  translate: pt(5.869, 4.469), rotate: 0,
  id: 'R17'
})
// ref_div.div.bottom_res
const R18 = board.add(R_0603_1608Metric, {
  translate: pt(5.869, 4.566), rotate: 0,
  id: 'R18'
})
// ref_cap.cap
const C35 = board.add(C_0603_1608Metric, {
  translate: pt(5.956, 4.849), rotate: 0,
  id: 'C35'
})
// reg_vcontrol.ic
const U10 = board.add(SOT_23_5, {
  translate: pt(5.737, 3.447), rotate: 0,
  id: 'U10'
})
// reg_vcontrol.fb.div.top_res
const R19 = board.add(R_0603_1608Metric, {
  translate: pt(5.881, 3.582), rotate: 0,
  id: 'R19'
})
// reg_vcontrol.fb.div.bottom_res
const R20 = board.add(R_0603_1608Metric, {
  translate: pt(6.037, 3.582), rotate: 0,
  id: 'R20'
})
// reg_vcontrol.power_path.inductor
const L5 = board.add(L_0603_1608Metric, {
  translate: pt(5.715, 3.696), rotate: 0,
  id: 'L5'
})
// reg_vcontrol.power_path.in_cap.cap
const C36 = board.add(C_0603_1608Metric, {
  translate: pt(5.871, 3.696), rotate: 0,
  id: 'C36'
})
// reg_vcontrol.power_path.out_cap.cap
const C37 = board.add(C_0805_2012Metric, {
  translate: pt(5.924, 3.419), rotate: 0,
  id: 'C37'
})
// reg_vcontrol.cf
const C38 = board.add(C_0603_1608Metric, {
  translate: pt(6.027, 3.696), rotate: 0,
  id: 'C38'
})
// reg_vcontrol.rect
const D7 = board.add(D_SOD_323, {
  translate: pt(5.720, 3.591), rotate: 0,
  id: 'D7'
})
// tp_vcontrol.tp
const TP9 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.963, 4.858), rotate: 0,
  id: 'TP9'
})
// filt_vcontroln.fb
const FB2 = board.add(L_0603_1608Metric, {
  translate: pt(6.191, 4.849), rotate: 0,
  id: 'FB2'
})
// reg_vcontroln.ic
const U11 = board.add(SOT_23_6, {
  translate: pt(6.362, 4.057), rotate: 0,
  id: 'U11'
})
// reg_vcontroln.cf
const C39 = board.add(C_0805_2012Metric, {
  translate: pt(6.569, 4.202), rotate: 0,
  id: 'C39'
})
// reg_vcontroln.cout.cap.c[0]
const C40 = board.add(C_1206_3216Metric, {
  translate: pt(6.572, 4.036), rotate: 0,
  id: 'C40'
})
// reg_vcontroln.cout.cap.c[1]
const C41 = board.add(C_1206_3216Metric, {
  translate: pt(6.372, 4.209), rotate: 0,
  id: 'C41'
})
// tp_vcontroln.tp
const TP10 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(5.213, 4.858), rotate: 0,
  id: 'TP10'
})
// control.dmeas.r1
const R21 = board.add(R_0603_1608Metric, {
  translate: pt(1.068, 2.826), rotate: 0,
  id: 'R21'
})
// control.dmeas.r2
const R22 = board.add(R_0603_1608Metric, {
  translate: pt(1.224, 2.826), rotate: 0,
  id: 'R22'
})
// control.dmeas.rf
const R23 = board.add(R_0603_1608Metric, {
  translate: pt(1.380, 2.826), rotate: 0,
  id: 'R23'
})
// control.dmeas.rg
const R24 = board.add(R_0603_1608Metric, {
  translate: pt(1.535, 2.826), rotate: 0,
  id: 'R24'
})
// control.err_volt.rtop
const R25 = board.add(R_0603_1608Metric, {
  translate: pt(1.691, 2.826), rotate: 0,
  id: 'R25'
})
// control.err_volt.rbot
const R26 = board.add(R_0603_1608Metric, {
  translate: pt(1.847, 2.826), rotate: 0,
  id: 'R26'
})
// control.err_volt.rout
const R27 = board.add(R_0603_1608Metric, {
  translate: pt(2.003, 2.826), rotate: 0,
  id: 'R27'
})
// control.err_volt.cin.cap
const C42 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.943), rotate: 0,
  id: 'C42'
})
// control.err_volt.rfine
const R28 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.943), rotate: 0,
  id: 'R28'
})
// control.err_source.rtop
const R29 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 2.943), rotate: 0,
  id: 'R29'
})
// control.err_source.rbot
const R30 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 2.943), rotate: 0,
  id: 'R30'
})
// control.err_source.diode
const D8 = board.add(D_SOD_323, {
  translate: pt(0.410, 2.835), rotate: 0,
  id: 'D8'
})
// control.err_source.cin.cap
const C43 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 2.943), rotate: 0,
  id: 'C43'
})
// control.err_sink.rtop
const R31 = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 2.943), rotate: 0,
  id: 'R31'
})
// control.err_sink.rbot
const R32 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 2.943), rotate: 0,
  id: 'R32'
})
// control.err_sink.diode
const D9 = board.add(D_SOD_323, {
  translate: pt(0.576, 2.835), rotate: 0,
  id: 'D9'
})
// control.err_sink.cin.cap
const C44 = board.add(C_0603_1608Metric, {
  translate: pt(1.150, 2.943), rotate: 0,
  id: 'C44'
})
// control.dclamp.jfet1
const jfet1 = board.add(SOT_23, {
  translate: pt(0.076, 2.518), rotate: 0,
  id: 'jfet1'
})
// control.dclamp.r
const R33 = board.add(R_0603_1608Metric, {
  translate: pt(1.306, 2.943), rotate: 0,
  id: 'R33'
})
// control.dclamp.jfet2
const jfet2 = board.add(SOT_23, {
  translate: pt(0.266, 2.518), rotate: 0,
  id: 'jfet2'
})
// control.comp_source.ic
const U12 = board.add(SOT_353_SC_70_5, {
  translate: pt(0.254, 2.680), rotate: 0,
  id: 'U12'
})
// control.comp_source.vdd_cap.cap
const C45 = board.add(C_0603_1608Metric, {
  translate: pt(1.461, 2.943), rotate: 0,
  id: 'C45'
})
// control.comp_sink.ic
const U13 = board.add(SOT_353_SC_70_5, {
  translate: pt(0.419, 2.680), rotate: 0,
  id: 'U13'
})
// control.comp_sink.vdd_cap.cap
const C46 = board.add(C_0603_1608Metric, {
  translate: pt(1.617, 2.943), rotate: 0,
  id: 'C46'
})
// control.off_sw.device.ic
const U14 = board.add(SOT_363_SC_70_6, {
  translate: pt(0.584, 2.680), rotate: 0,
  id: 'U14'
})
// control.off_sw.device.vdd_cap.cap
const C47 = board.add(C_0603_1608Metric, {
  translate: pt(1.773, 2.943), rotate: 0,
  id: 'C47'
})
// control.int.r
const R34 = board.add(R_0603_1608Metric, {
  translate: pt(1.929, 2.943), rotate: 0,
  id: 'R34'
})
// control.int.c
const C48 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 3.040), rotate: 0,
  id: 'C48'
})
// control.hvclamp.res
const R35 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 3.040), rotate: 0,
  id: 'R35'
})
// control.amp.r1
const R36 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 3.040), rotate: 0,
  id: 'R36'
})
// control.amp.r2
const R37 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 3.040), rotate: 0,
  id: 'R37'
})
// control.driver.clamp1
const D10 = board.add(D_SOD_323, {
  translate: pt(0.741, 2.835), rotate: 0,
  id: 'D10'
})
// control.driver.clamp2
const D11 = board.add(D_SOD_323, {
  translate: pt(0.907, 2.835), rotate: 0,
  id: 'D11'
})
// control.driver.high_fet
const Q7 = board.add(TO_252_2, {
  translate: pt(1.155, 1.951), rotate: 0,
  id: 'Q7'
})
// control.driver.low_fet
const Q8 = board.add(TO_252_2, {
  translate: pt(1.631, 1.951), rotate: 0,
  id: 'Q8'
})
// control.driver.res.res[0]
const R38 = board.add(R_0603_1608Metric, {
  translate: pt(0.682, 3.040), rotate: 0,
  id: 'R38'
})
// control.driver.res.res[1]
const R39 = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 3.040), rotate: 0,
  id: 'R39'
})
// control.driver.res.res[2]
const R40 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 3.040), rotate: 0,
  id: 'R40'
})
// control.driver.high_gate.device.ic
const U15 = board.add(SOT_23_6, {
  translate: pt(0.462, 2.518), rotate: 0,
  id: 'U15'
})
// control.driver.high_gate.device.vdd_cap.cap
const C49 = board.add(C_0805_2012Metric, {
  translate: pt(0.972, 2.663), rotate: 0,
  id: 'C49'
})
// control.driver.low_gate.device.ic
const U16 = board.add(SOT_23_6, {
  translate: pt(0.663, 2.518), rotate: 0,
  id: 'U16'
})
// control.driver.low_gate.device.vdd_cap.cap
const C50 = board.add(C_0805_2012Metric, {
  translate: pt(1.146, 2.663), rotate: 0,
  id: 'C50'
})
// control.driver.high_res
const R41 = board.add(R_0603_1608Metric, {
  translate: pt(1.150, 3.040), rotate: 0,
  id: 'R41'
})
// control.driver.low_res
const R42 = board.add(R_0603_1608Metric, {
  translate: pt(1.306, 3.040), rotate: 0,
  id: 'R42'
})
// control.driver.cap_in1.cap
const C51 = board.add(CP_Elec_8x10, {
  translate: pt(0.217, 1.987), rotate: 0,
  id: 'C51'
})
// control.driver.cap_in2.cap
const C52 = board.add(C_0805_2012Metric, {
  translate: pt(1.319, 2.663), rotate: 0,
  id: 'C52'
})
// control.driver.cap_in3.cap
const C53 = board.add(C_0603_1608Metric, {
  translate: pt(1.461, 3.040), rotate: 0,
  id: 'C53'
})
// control.vdiv.div.top_res
const R43 = board.add(R_0603_1608Metric, {
  translate: pt(1.617, 3.040), rotate: 0,
  id: 'R43'
})
// control.vdiv.div.bottom_res
const R44 = board.add(R_0603_1608Metric, {
  translate: pt(1.773, 3.040), rotate: 0,
  id: 'R44'
})
// control.cdiv.cap
const C54 = board.add(C_0603_1608Metric, {
  translate: pt(1.929, 3.040), rotate: 0,
  id: 'C54'
})
// control.isense.ranges[0].isense.res.res
const R45 = board.add(R_1206_3216Metric, {
  translate: pt(0.776, 2.669), rotate: 0,
  id: 'R45'
})
// control.isense.ranges[0].sense_sw.device.ic
const U17 = board.add(SOT_23_6, {
  translate: pt(0.863, 2.518), rotate: 0,
  id: 'U17'
})
// control.isense.ranges[0].sense_sw.device.vdd_cap.cap
const C55 = board.add(C_0805_2012Metric, {
  translate: pt(1.492, 2.663), rotate: 0,
  id: 'C55'
})
// control.isense.ranges[0].pwr_sw.ic
const U18 = board.add(SMDIP_6_W7_62mm, {
  translate: pt(0.663, 1.975), rotate: 0,
  id: 'U18'
})
// control.isense.ranges[0].pwr_sw.res
const R46 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 3.137), rotate: 0,
  id: 'R46'
})
// control.isense.ranges[1].isense.res.res
const R47 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 3.137), rotate: 0,
  id: 'R47'
})
// control.isense.ranges[1].sense_sw.device.ic
const U19 = board.add(SOT_23_6, {
  translate: pt(1.064, 2.518), rotate: 0,
  id: 'U19'
})
// control.isense.ranges[1].sense_sw.device.vdd_cap.cap
const C56 = board.add(C_0805_2012Metric, {
  translate: pt(1.665, 2.663), rotate: 0,
  id: 'C56'
})
// control.isense.ranges[1].pwr_sw.ic
const U20 = board.add(SO_4_4_4x3_6mm_P2_54mm, {
  translate: pt(0.835, 2.280), rotate: 0,
  id: 'U20'
})
// control.isense.ranges[1].pwr_sw.res
const R48 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 3.137), rotate: 0,
  id: 'R48'
})
// control.isense.ranges[2].isense.res.res
const R49 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 3.137), rotate: 0,
  id: 'R49'
})
// control.isense.ranges[2].sense_sw.device.ic
const U21 = board.add(SOT_23_6, {
  translate: pt(1.265, 2.518), rotate: 0,
  id: 'U21'
})
// control.isense.ranges[2].sense_sw.device.vdd_cap.cap
const C57 = board.add(C_0805_2012Metric, {
  translate: pt(1.839, 2.663), rotate: 0,
  id: 'C57'
})
// control.isense.ranges[2].pwr_sw.ic
const U22 = board.add(SO_4_4_4x3_6mm_P2_54mm, {
  translate: pt(1.220, 2.280), rotate: 0,
  id: 'U22'
})
// control.isense.ranges[2].pwr_sw.res
const R50 = board.add(R_0603_1608Metric, {
  translate: pt(0.682, 3.137), rotate: 0,
  id: 'R50'
})
// control.ifilt.rp
const R51 = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 3.137), rotate: 0,
  id: 'R51'
})
// control.ifilt.rn
const R52 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 3.137), rotate: 0,
  id: 'R52'
})
// control.ifilt.c
const C58 = board.add(C_0603_1608Metric, {
  translate: pt(1.150, 3.137), rotate: 0,
  id: 'C58'
})
// control.vmeas.ic
const U23 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.146, 2.306), rotate: 0,
  id: 'U23'
})
// control.vmeas.vdd_cap.cap
const C59 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 2.836), rotate: 0,
  id: 'C59'
})
// control.vmeas.rg
const R53 = board.add(R_0603_1608Metric, {
  translate: pt(1.306, 3.137), rotate: 0,
  id: 'R53'
})
// control.imeas.ic
const U24 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.476, 2.306), rotate: 0,
  id: 'U24'
})
// control.imeas.vdd_cap.cap
const C60 = board.add(C_0805_2012Metric, {
  translate: pt(0.240, 2.836), rotate: 0,
  id: 'C60'
})
// control.imeas.rg
const R54 = board.add(R_0603_1608Metric, {
  translate: pt(1.461, 3.137), rotate: 0,
  id: 'R54'
})
// control.vclamp.jfet1
const jfet3 = board.add(SOT_23, {
  translate: pt(1.461, 2.518), rotate: 0,
  id: 'jfet3'
})
// control.vclamp.r
const R55 = board.add(R_0603_1608Metric, {
  translate: pt(1.617, 3.137), rotate: 0,
  id: 'R55'
})
// control.vclamp.jfet2
const jfet4 = board.add(SOT_23, {
  translate: pt(1.651, 2.518), rotate: 0,
  id: 'jfet4'
})
// control.snub_r.res
const R56 = board.add(R_0603_1608Metric, {
  translate: pt(1.773, 3.137), rotate: 0,
  id: 'R56'
})
// control.snub_c.cap
const C61 = board.add(C_0603_1608Metric, {
  translate: pt(1.929, 3.137), rotate: 0,
  id: 'C61'
})
// control.iclamp.jfet1
const jfet5 = board.add(SOT_23, {
  translate: pt(1.842, 2.518), rotate: 0,
  id: 'jfet5'
})
// control.iclamp.r
const R57 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 3.233), rotate: 0,
  id: 'R57'
})
// control.iclamp.jfet2
const jfet6 = board.add(SOT_23, {
  translate: pt(0.076, 2.691), rotate: 0,
  id: 'jfet6'
})
// control.tvs_p
const tvs_p1 = board.add(D_SMA, {
  translate: pt(1.571, 2.268), rotate: 0,
  id: 'tvs_p1'
})
// control.tvs_n
const tvs_n1 = board.add(D_SMA, {
  translate: pt(1.887, 2.268), rotate: 0,
  id: 'tvs_n1'
})
// pd.ic
const U25 = board.add(WQFN_14_1EP_2_5x2_5mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(0.073, 4.513), rotate: 0,
  id: 'U25'
})
// pd.vdd_cap[0].cap
const C62 = board.add(C_0603_1608Metric, {
  translate: pt(0.231, 4.654), rotate: 0,
  id: 'C62'
})
// pd.vdd_cap[1].cap
const C63 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 4.664), rotate: 0,
  id: 'C63'
})
// mcu.ic
const U26 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(3.504, 0.530), rotate: 0,
  id: 'U26'
})
// mcu.vcc_cap0.cap
const C64 = board.add(C_1206_3216Metric, {
  translate: pt(4.579, 0.242), rotate: 0,
  id: 'C64'
})
// mcu.vcc_cap1.cap
const C65 = board.add(C_0603_1608Metric, {
  translate: pt(4.767, 0.226), rotate: 0,
  id: 'C65'
})
// mcu.prog.conn
const J2 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(4.626, 0.079), rotate: 0,
  id: 'J2'
})
// mcu.en_pull.rc.r
const R58 = board.add(R_0603_1608Metric, {
  translate: pt(4.546, 0.356), rotate: 0,
  id: 'R58'
})
// mcu.en_pull.rc.c
const C66 = board.add(C_0603_1608Metric, {
  translate: pt(4.702, 0.356), rotate: 0,
  id: 'C66'
})
// led.package
const D12 = board.add(LED_0603_1608Metric, {
  translate: pt(5.634, 4.469), rotate: 0,
  id: 'D12'
})
// led.res
const R59 = board.add(R_0603_1608Metric, {
  translate: pt(5.634, 4.566), rotate: 0,
  id: 'R59'
})
// usb_esd
const U27 = board.add(SOT_23, {
  translate: pt(0.310, 5.160), rotate: 0,
  id: 'U27'
})
// i2c_tp.tp_scl.tp
const TP11 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.397, 4.478), rotate: 0,
  id: 'TP11'
})
// i2c_tp.tp_sda.tp
const TP12 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.397, 4.592), rotate: 0,
  id: 'TP12'
})
// i2c_pull.scl_res.res
const R60 = board.add(R_0603_1608Metric, {
  translate: pt(6.104, 4.469), rotate: 0,
  id: 'R60'
})
// i2c_pull.sda_res.res
const R61 = board.add(R_0603_1608Metric, {
  translate: pt(6.104, 4.566), rotate: 0,
  id: 'R61'
})
// oled.device.conn
const J3 = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(0.356, 1.577), rotate: 0,
  id: 'J3'
})
// oled.lcd
const U28 = board.add(Lcd_Er_Oled022_1_Outline, {
  translate: pt(1.220, 0.607), rotate: 0,
  id: 'U28'
})
// oled.iref_res
const R62 = board.add(R_0603_1608Metric, {
  translate: pt(1.377, 1.413), rotate: 0,
  id: 'R62'
})
// oled.vcomh_cap.cap
const C67 = board.add(C_1206_3216Metric, {
  translate: pt(0.843, 1.430), rotate: 0,
  id: 'C67'
})
// oled.vdd_cap1.cap
const C68 = board.add(C_0603_1608Metric, {
  translate: pt(1.533, 1.413), rotate: 0,
  id: 'C68'
})
// oled.vdd_cap2.cap
const C69 = board.add(C_0805_2012Metric, {
  translate: pt(1.039, 1.423), rotate: 0,
  id: 'C69'
})
// oled.vcc_cap1.cap
const C70 = board.add(C_0603_1608Metric, {
  translate: pt(1.689, 1.413), rotate: 0,
  id: 'C70'
})
// oled.vcc_cap2.cap
const C71 = board.add(C_0805_2012Metric, {
  translate: pt(1.213, 1.423), rotate: 0,
  id: 'C71'
})
// oled_rc.rc.r
const R63 = board.add(R_0603_1608Metric, {
  translate: pt(6.338, 4.469), rotate: 0,
  id: 'R63'
})
// oled_rc.rc.c
const C72 = board.add(C_0603_1608Metric, {
  translate: pt(6.338, 4.566), rotate: 0,
  id: 'C72'
})
// ioe_ctl.ic
const U29 = board.add(TSSOP_16_4_4x5mm_P0_65mm, {
  translate: pt(1.517, 4.099), rotate: 0,
  id: 'U29'
})
// ioe_ctl.vdd_cap.cap
const C73 = board.add(C_0603_1608Metric, {
  translate: pt(1.424, 4.275), rotate: 0,
  id: 'C73'
})
// buck_rc.rc.r
const R64 = board.add(R_0603_1608Metric, {
  translate: pt(6.573, 4.469), rotate: 0,
  id: 'R64'
})
// buck_rc.rc.c
const C74 = board.add(C_0603_1608Metric, {
  translate: pt(6.573, 4.566), rotate: 0,
  id: 'C74'
})
// boost_rc.rc.r
const R65 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 4.849), rotate: 0,
  id: 'R65'
})
// boost_rc.rc.c
const C75 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 4.946), rotate: 0,
  id: 'C75'
})
// conv_ovp.comp.ic
const U30 = board.add(SOT_353_SC_70_5, {
  translate: pt(3.313, 4.495), rotate: 0,
  id: 'U30'
})
// conv_ovp.comp.vdd_cap.cap
const C76 = board.add(C_0603_1608Metric, {
  translate: pt(3.474, 4.469), rotate: 0,
  id: 'C76'
})
// conv_ovp.comp_div.div.top_res
const R66 = board.add(R_0603_1608Metric, {
  translate: pt(3.309, 4.619), rotate: 0,
  id: 'R66'
})
// conv_ovp.comp_div.div.bottom_res
const R67 = board.add(R_0603_1608Metric, {
  translate: pt(3.465, 4.619), rotate: 0,
  id: 'R67'
})
// conv_latch.ic.ic
const U31 = board.add(VSSOP_8_2_4x2_1mm_P0_5mm, {
  translate: pt(4.127, 4.491), rotate: 0,
  id: 'U31'
})
// conv_latch.ic.vdd_cap.cap
const C77 = board.add(C_0603_1608Metric, {
  translate: pt(4.099, 4.611), rotate: 0,
  id: 'C77'
})
// conv_en_pull.res
const R68 = board.add(R_0603_1608Metric, {
  translate: pt(6.426, 4.849), rotate: 0,
  id: 'R68'
})
// comp_pull.res
const R69 = board.add(R_0603_1608Metric, {
  translate: pt(6.660, 4.849), rotate: 0,
  id: 'R69'
})
// pass_temp.ic
const U32 = board.add(SOT_563, {
  translate: pt(4.634, 4.483), rotate: 0,
  id: 'U32'
})
// pass_temp.vdd_cap.cap
const C78 = board.add(C_0603_1608Metric, {
  translate: pt(4.639, 4.595), rotate: 0,
  id: 'C78'
})
// conv_temp.ic
const U33 = board.add(SOT_563, {
  translate: pt(4.869, 4.483), rotate: 0,
  id: 'U33'
})
// conv_temp.vdd_cap.cap
const C79 = board.add(C_0603_1608Metric, {
  translate: pt(4.874, 4.595), rotate: 0,
  id: 'C79'
})
// conv_sense.div.top_res
const R70 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 4.849), rotate: 0,
  id: 'R70'
})
// conv_sense.div.bottom_res
const R71 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 4.946), rotate: 0,
  id: 'R71'
})
// ioe_ui.ic
const U34 = board.add(TSSOP_16_4_4x5mm_P0_65mm, {
  translate: pt(1.938, 4.099), rotate: 0,
  id: 'U34'
})
// ioe_ui.vdd_cap.cap
const C80 = board.add(C_0603_1608Metric, {
  translate: pt(1.845, 4.275), rotate: 0,
  id: 'C80'
})
// enc.package
const SW1 = board.add(RotaryEncoder_Bourns_PEC11S, {
  translate: pt(4.266, 2.158), rotate: 0,
  id: 'SW1'
})
// dir.package
const SW2 = board.add(DirectionSwitch_Alps_SKRH, {
  translate: pt(2.676, 3.595), rotate: 0,
  id: 'SW2'
})
// rgb.package
const D13 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(3.692, 4.495), rotate: 0,
  id: 'D13'
})
// rgb.red_res
const R72 = board.add(R_0603_1608Metric, {
  translate: pt(3.831, 4.469), rotate: 0,
  id: 'R72'
})
// rgb.green_res
const R73 = board.add(R_0603_1608Metric, {
  translate: pt(3.709, 4.619), rotate: 0,
  id: 'R73'
})
// rgb.blue_res
const R74 = board.add(R_0603_1608Metric, {
  translate: pt(3.865, 4.619), rotate: 0,
  id: 'R74'
})
// qwiic_pull.scl_res.res
const R75 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 4.849), rotate: 0,
  id: 'R75'
})
// qwiic_pull.sda_res.res
const R76 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 4.946), rotate: 0,
  id: 'R76'
})
// qwiic.conn
const J4 = board.add(JST_SH_SM04B_SRSS_TB_1x04_1MP_P1_00mm_Horizontal, {
  translate: pt(0.561, 4.569), rotate: 0,
  id: 'J4'
})
// dutio.conn
const J5 = board.add(PinHeader_1x03_P2_54mm_Horizontal, {
  translate: pt(6.284, 3.650), rotate: 0,
  id: 'J5'
})
// touch_duck
const U35 = board.add(Symbol_DucklingSolid, {
  translate: pt(0.583, 5.093), rotate: 0,
  id: 'U35'
})
// fan_drv.pre
const Q9 = board.add(SOT_23, {
  translate: pt(3.512, 4.057), rotate: 0,
  id: 'Q9'
})
// fan_drv.pull
const R77 = board.add(R_0603_1608Metric, {
  translate: pt(3.685, 4.193), rotate: 0,
  id: 'R77'
})
// fan_drv.drv
const Q10 = board.add(SOT_23, {
  translate: pt(3.512, 4.231), rotate: 0,
  id: 'Q10'
})
// fan.conn
const J6 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.567, 4.570), rotate: 0,
  id: 'J6'
})
// spk_drv.ic
const U36 = board.add(QFN_16_1EP_3x3mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(5.957, 4.074), rotate: 0,
  id: 'U36'
})
// spk_drv.pwr_cap0.cap
const C81 = board.add(C_0603_1608Metric, {
  translate: pt(6.105, 4.226), rotate: 0,
  id: 'C81'
})
// spk_drv.pwr_cap1.cap
const C82 = board.add(C_0805_2012Metric, {
  translate: pt(5.940, 4.236), rotate: 0,
  id: 'C82'
})
// spk.conn
const J7 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.957, 4.570), rotate: 0,
  id: 'J7'
})
// dac.ic
const U37 = board.add(MSOP_10_3x3mm_P0_5mm, {
  translate: pt(0.125, 4.059), rotate: 0,
  id: 'U37'
})
// dac.vdd_cap[0].cap
const C83 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 4.196), rotate: 0,
  id: 'C83'
})
// dac.vdd_cap[1].cap
const C84 = board.add(C_0805_2012Metric, {
  translate: pt(0.357, 4.029), rotate: 0,
  id: 'C84'
})
// dac.out_cap[0]
const C85 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 4.196), rotate: 0,
  id: 'C85'
})
// dac.out_cap[1]
const C86 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 4.196), rotate: 0,
  id: 'C86'
})
// dac.out_cap[2]
const C87 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 4.293), rotate: 0,
  id: 'C87'
})
// dac.out_cap[3]
const C88 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 4.293), rotate: 0,
  id: 'C88'
})
// dac_ferrite.fb
const FB3 = board.add(L_0603_1608Metric, {
  translate: pt(0.058, 5.122), rotate: 0,
  id: 'FB3'
})
// tp_cv.conn
const J8 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(3.941, 4.089), rotate: 0,
  id: 'J8'
})
// tp_cv.res
const R78 = board.add(R_0603_1608Metric, {
  translate: pt(3.920, 4.256), rotate: 0,
  id: 'R78'
})
// tp_cvf.conn
const J9 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(4.228, 4.089), rotate: 0,
  id: 'J9'
})
// tp_cvf.res
const R79 = board.add(R_0603_1608Metric, {
  translate: pt(4.207, 4.256), rotate: 0,
  id: 'R79'
})
// tp_cisrc.conn
const J10 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(4.516, 4.089), rotate: 0,
  id: 'J10'
})
// tp_cisrc.res
const R80 = board.add(R_0603_1608Metric, {
  translate: pt(4.494, 4.256), rotate: 0,
  id: 'R80'
})
// tp_cisnk.conn
const J11 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(4.803, 4.089), rotate: 0,
  id: 'J11'
})
// tp_cisnk.res
const R81 = board.add(R_0603_1608Metric, {
  translate: pt(4.782, 4.256), rotate: 0,
  id: 'R81'
})
// adc.ic
const U38 = board.add(TSSOP_20_4_4x6_5mm_P0_65mm, {
  translate: pt(1.344, 3.518), rotate: 0,
  id: 'U38'
})
// adc.avdd_res.res
const R82 = board.add(R_0603_1608Metric, {
  translate: pt(1.593, 3.526), rotate: 0,
  id: 'R82'
})
// adc.dvdd_res.res
const R83 = board.add(R_0603_1608Metric, {
  translate: pt(1.593, 3.622), rotate: 0,
  id: 'R83'
})
// adc.avdd_cap_0.cap
const C89 = board.add(C_0603_1608Metric, {
  translate: pt(1.250, 3.724), rotate: 0,
  id: 'C89'
})
// adc.avdd_cap_1.cap
const C90 = board.add(C_0603_1608Metric, {
  translate: pt(1.406, 3.724), rotate: 0,
  id: 'C90'
})
// adc.dvdd_cap_0.cap
const C91 = board.add(C_0603_1608Metric, {
  translate: pt(1.562, 3.724), rotate: 0,
  id: 'C91'
})
// adc.dvdd_cap_1.cap
const C92 = board.add(C_0603_1608Metric, {
  translate: pt(1.250, 3.821), rotate: 0,
  id: 'C92'
})
// adc.vref_cap.cap
const C93 = board.add(C_0805_2012Metric, {
  translate: pt(1.602, 3.419), rotate: 0,
  id: 'C93'
})
// tp_vcen.conn
const J12 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.091, 4.089), rotate: 0,
  id: 'J12'
})
// tp_vcen.res
const R84 = board.add(R_0603_1608Metric, {
  translate: pt(5.069, 4.256), rotate: 0,
  id: 'R84'
})
// vcen_rc.rc.r
const R85 = board.add(R_0603_1608Metric, {
  translate: pt(0.762, 4.849), rotate: 0,
  id: 'R85'
})
// vcen_rc.rc.c
const C94 = board.add(C_0603_1608Metric, {
  translate: pt(0.762, 4.946), rotate: 0,
  id: 'C94'
})
// tp_mi.conn
const J13 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.378, 4.089), rotate: 0,
  id: 'J13'
})
// tp_mi.res
const R86 = board.add(R_0603_1608Metric, {
  translate: pt(5.357, 4.256), rotate: 0,
  id: 'R86'
})
// mi_rc.rc.r
const R87 = board.add(R_0603_1608Metric, {
  translate: pt(0.997, 4.849), rotate: 0,
  id: 'R87'
})
// mi_rc.rc.c
const C95 = board.add(C_0603_1608Metric, {
  translate: pt(0.997, 4.946), rotate: 0,
  id: 'C95'
})
// tp_mv.conn
const J14 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.665, 4.089), rotate: 0,
  id: 'J14'
})
// tp_mv.res
const R88 = board.add(R_0603_1608Metric, {
  translate: pt(5.644, 4.256), rotate: 0,
  id: 'R88'
})
// mv_rc.rc.r
const R89 = board.add(R_0603_1608Metric, {
  translate: pt(1.231, 4.849), rotate: 0,
  id: 'R89'
})
// mv_rc.rc.c
const C96 = board.add(C_0603_1608Metric, {
  translate: pt(1.231, 4.946), rotate: 0,
  id: 'C96'
})
// tp_lsrc.tp
const TP13 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(5.463, 4.858), rotate: 0,
  id: 'TP13'
})
// tp_lsnk.tp
const TP14 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(5.714, 4.858), rotate: 0,
  id: 'TP14'
})
// outn
const J15 = board.add(CalTest_CT3151, {
  translate: pt(6.269, 2.199), rotate: 0,
  id: 'J15'
})
// outp
const J16 = board.add(CalTest_CT3151, {
  translate: pt(0.882, 3.766), rotate: 0,
  id: 'J16'
})
// outd
const J17 = board.add(PinHeader_1x02_P2_54mm_Horizontal, {
  translate: pt(5.121, 4.611), rotate: 0,
  id: 'J17'
})
// vimeas_amps.ic
const U39 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.692, 4.097), rotate: 0,
  id: 'U39'
})
// vimeas_amps.vdd_cap.cap
const C97 = board.add(C_0805_2012Metric, {
  translate: pt(0.613, 4.281), rotate: 0,
  id: 'C97'
})
// ampdmeas_amps.ic
const U40 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.102, 4.097), rotate: 0,
  id: 'U40'
})
// ampdmeas_amps.vdd_cap.cap
const C98 = board.add(C_0805_2012Metric, {
  translate: pt(1.023, 4.281), rotate: 0,
  id: 'C98'
})
// cv_amps.ic
const U41 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.354, 4.097), rotate: 0,
  id: 'U41'
})
// cv_amps.vdd_cap.cap
const C99 = board.add(C_0603_1608Metric, {
  translate: pt(2.266, 4.271), rotate: 0,
  id: 'C99'
})
// ci_amps.ic
const U42 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.763, 4.097), rotate: 0,
  id: 'U42'
})
// ci_amps.vdd_cap.cap
const C100 = board.add(C_0603_1608Metric, {
  translate: pt(2.676, 4.271), rotate: 0,
  id: 'C100'
})
// cintref_amps.ic
const U43 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(3.172, 4.097), rotate: 0,
  id: 'U43'
})
// cintref_amps.vdd_cap.cap
const C101 = board.add(C_0603_1608Metric, {
  translate: pt(3.085, 4.271), rotate: 0,
  id: 'C101'
})

board.setNetlist([
  {name: "gnd", pads: [["U27", "3"], ["J8", "2"], ["J9", "2"], ["J10", "2"], ["J11", "2"], ["J12", "2"], ["J13", "2"], ["J14", "2"], ["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["J15", "1"], ["J17", "1"], ["TP1", "1"], ["U1", "3"], ["U1", "7"], ["U1", "8"], ["D1", "2"], ["U2", "1"], ["U3", "1"], ["D2", "2"], ["U4", "3"], ["U4", "8"], ["C12", "2"], ["D5", "2"], ["U7", "2"], ["U8", "2"], ["U9", "3"], ["C35", "2"], ["U10", "2"], ["U11", "1"], ["U25", "8"], ["U25", "9"], ["U25", "15"], ["U26", "1"], ["U26", "40"], ["U26", "41"], ["U29", "1"], ["U29", "2"], ["U29", "3"], ["U29", "8"], ["R68", "1"], ["U32", "2"], ["U32", "4"], ["U33", "2"], ["U34", "1"], ["U34", "3"], ["U34", "8"], ["SW1", "C"], ["SW1", "S2"], ["SW2", "5"], ["J4", "1"], ["J5", "1"], ["Q9", "2"], ["J6", "1"], ["U36", "3"], ["U36", "11"], ["U36", "15"], ["U36", "17"], ["U37", "10"], ["U38", "2"], ["U38", "3"], ["U38", "19"], ["Q1", "2"], ["R18", "2"], ["C72", "2"], ["C74", "2"], ["C75", "2"], ["U31", "4"], ["R71", "2"], ["C94", "2"], ["C95", "2"], ["C96", "2"], ["J1", "S1"], ["tvs_n1", "1"], ["R62", "2"], ["C85", "2"], ["C86", "2"], ["C87", "2"], ["C88", "2"], ["C1", "2"], ["C2", "2"], ["C6", "2"], ["C11", "2"], ["C32", "2"], ["C33", "2"], ["C34", "2"], ["U12", "2"], ["U13", "2"], ["U23", "1"], ["C61", "2"], ["C54", "2"], ["C62", "2"], ["C63", "2"], ["C64", "2"], ["C65", "2"], ["J2", "5"], ["J3", "3"], ["J3", "1"], ["J3", "24"], ["J3", "2"], ["J3", "12"], ["J3", "11"], ["J3", "16"], ["J3", "17"], ["J3", "18"], ["J3", "19"], ["J3", "20"], ["C67", "2"], ["C68", "2"], ["C69", "2"], ["C70", "2"], ["C71", "2"], ["C73", "2"], ["U30", "2"], ["C78", "2"], ["C79", "2"], ["C80", "2"], ["C81", "2"], ["C82", "2"], ["C83", "2"], ["C84", "2"], ["C89", "2"], ["C90", "2"], ["C91", "2"], ["C92", "2"], ["C93", "2"], ["R3", "2"], ["R6", "2"], ["R16", "2"], ["R20", "2"], ["U43", "4"], ["R44", "2"], ["U14", "2"], ["C66", "2"], ["R67", "2"], ["C77", "2"], ["Q3", "3"], ["Q5", "3"], ["Q8", "2"], ["J3", "7"], ["J3", "10"], ["J3", "8"], ["C4", "2"], ["C5", "2"], ["C10", "2"], ["U5", "6"], ["U6", "6"], ["C29", "2"], ["C30", "2"], ["C36", "2"], ["C37", "2"], ["C40", "2"], ["C41", "2"], ["C42", "2"], ["U41", "4"], ["C45", "2"], ["C46", "2"], ["C44", "2"], ["U42", "4"], ["C43", "2"], ["C51", "2"], ["C52", "2"], ["C53", "2"], ["C76", "2"], ["C101", "2"], ["C47", "2"], ["C8", "2"], ["C9", "2"], ["C13", "2"], ["C14", "2"], ["C15", "2"], ["C16", "2"], ["C17", "2"], ["C18", "2"], ["C19", "2"], ["C20", "2"], ["C21", "2"], ["C22", "2"], ["C23", "2"], ["C24", "2"], ["C25", "2"], ["C27", "2"], ["C99", "2"], ["C100", "2"], ["R46", "2"], ["R48", "2"], ["R50", "2"], ["U17", "2"], ["U17", "4"], ["U19", "2"], ["U19", "4"], ["U21", "2"], ["U21", "4"], ["C55", "2"], ["C56", "2"], ["C57", "2"]]},
  {name: "vusb", pads: [["U25", "2"], ["U2", "3"], ["U3", "3"], ["R1", "2"], ["U1", "2"], ["R4", "1"], ["R7", "1"], ["C2", "1"], ["C6", "1"], ["C4", "1"], ["R9", "1"], ["Q2", "1"], ["Q2", "2"], ["Q2", "3"], ["C8", "1"], ["C9", "1"], ["R10", "1"]]},
  {name: "v5", pads: [["TP3", "1"], ["U7", "5"], ["U8", "1"], ["U9", "1"], ["U10", "5"], ["R77", "1"], ["Q10", "2"], ["U36", "4"], ["U36", "7"], ["U36", "8"], ["R2", "1"], ["U7", "4"], ["U8", "3"], ["U10", "4"], ["C32", "1"], ["C34", "1"], ["C81", "1"], ["C82", "1"], ["U5", "4"], ["U6", "4"], ["L4", "1"], ["L5", "1"], ["D3", "2"], ["D4", "2"], ["C29", "1"], ["C36", "1"], ["C25", "1"], ["C27", "1"], ["L1", "2"], ["C5", "1"]]},
  {name: "v3v3", pads: [["D2", "1"], ["TP4", "1"], ["U1", "4"], ["U4", "4"], ["U4", "7"], ["U25", "3"], ["U25", "4"], ["U26", "2"], ["D12", "2"], ["U29", "16"], ["R69", "1"], ["U32", "5"], ["U33", "4"], ["U33", "5"], ["U34", "2"], ["U34", "16"], ["D13", "2"], ["J4", "2"], ["R63", "1"], ["U30", "5"], ["U31", "8"], ["R83", "1"], ["R5", "1"], ["C1", "1"], ["C11", "1"], ["C62", "1"], ["C63", "1"], ["C64", "1"], ["C65", "1"], ["J2", "1"], ["R60", "1"], ["R61", "1"], ["J3", "5"], ["C68", "1"], ["C69", "1"], ["C73", "1"], ["C78", "1"], ["C79", "1"], ["C80", "1"], ["R75", "1"], ["R76", "1"], ["R58", "1"], ["C76", "1"], ["C77", "1"], ["J3", "6"], ["L2", "2"], ["C10", "1"]]},
  {name: "vconv", pads: [["D5", "1"], ["TP5", "1"], ["R70", "1"], ["Q7", "2"], ["C51", "1"], ["C52", "1"], ["C53", "1"], ["R66", "1"], ["Q6", "2"], ["C16", "1"], ["C17", "1"], ["C18", "1"], ["C19", "1"], ["C20", "1"], ["C21", "1"], ["C22", "1"], ["C23", "1"], ["C24", "1"]]},
  {name: "v12", pads: [["TP6", "1"], ["D6", "1"], ["C31", "1"], ["R15", "1"], ["C30", "1"], ["J3", "23"], ["C70", "1"], ["C71", "1"]]},
  {name: "vanalog", pads: [["U8", "5"], ["TP7", "1"], ["FB2", "1"], ["R82", "1"], ["C33", "1"], ["U13", "5"], ["U12", "5"], ["U41", "8"], ["U14", "5"], ["U43", "8"], ["U42", "8"], ["C46", "1"], ["C45", "1"], ["C99", "1"], ["C47", "1"], ["C101", "1"], ["C100", "1"]]},
  {name: "vref", pads: [["U9", "2"], ["TP8", "1"], ["FB3", "1"], ["U38", "4"], ["R17", "1"], ["C93", "1"]]},
  {name: "vcenter", pads: [["U30", "3"], ["U41", "5"], ["U39", "5"], ["U43", "6"], ["C35", "1"], ["R84", "1"], ["U23", "6"], ["U24", "6"], ["R85", "1"], ["U43", "3"], ["U43", "7"], ["R24", "1"], ["R37", "2"]]},
  {name: "vcontrol", pads: [["TP9", "1"], ["D7", "1"], ["C38", "1"], ["R19", "1"], ["C37", "1"], ["U23", "8"], ["U24", "8"], ["U39", "8"], ["U40", "8"], ["C59", "1"], ["C60", "1"], ["U15", "5"], ["U16", "5"], ["C97", "1"], ["C98", "1"], ["U17", "5"], ["U19", "5"], ["U21", "5"], ["C49", "1"], ["C50", "1"], ["C55", "1"], ["C56", "1"], ["C57", "1"]]},
  {name: "vcontroln", pads: [["U11", "2"], ["TP10", "1"], ["U23", "5"], ["U24", "5"], ["U39", "4"], ["U40", "4"], ["C59", "2"], ["C60", "2"], ["C97", "2"], ["C98", "2"], ["U15", "2"], ["U15", "4"], ["U16", "2"], ["U16", "4"], ["C40", "1"], ["C41", "1"], ["C49", "2"], ["C50", "2"]]},
  {name: "usb.pwr", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["FB1", "1"]]},
  {name: "filt_vusb.pwr_out", pads: [["FB1", "2"], ["F1", "1"]]},
  {name: "fuse_vusb.pwr_out", pads: [["F1", "2"], ["D1", "1"], ["TP2", "1"], ["R1", "1"], ["U1", "1"]]},
  {name: "precharge.pwr_out", pads: [["Q2", "5"], ["Q2", "6"], ["Q2", "7"], ["Q2", "8"], ["R8", "1"], ["U4", "1"], ["R10", "2"]]},
  {name: "convin_sense.sense_neg", pads: [["C12", "1"], ["R8", "2"], ["U4", "2"], ["Q4", "2"], ["C13", "1"], ["C14", "1"], ["C15", "1"]]},
  {name: "ref_div.output", pads: [["U43", "5"], ["R17", "2"], ["R18", "1"]]},
  {name: "filt_vcontroln.pwr_out", pads: [["U11", "4"], ["U11", "5"], ["FB2", "2"]]},
  {name: "usb.cc.cc1", pads: [["J1", "A5"], ["U25", "10"], ["U25", "11"]]},
  {name: "usb.cc.cc2", pads: [["J1", "B5"], ["U25", "1"], ["U25", "14"]]},
  {name: "mcu.program_boot_node", pads: [["R59", "2"], ["U26", "27"], ["J2", "2"]]},
  {name: "usb_chain_0.d_P", pads: [["J1", "A6"], ["J1", "B6"], ["U27", "2"], ["U26", "14"]]},
  {name: "usb_chain_0.d_N", pads: [["J1", "A7"], ["J1", "B7"], ["U27", "1"], ["U26", "13"]]},
  {name: "i2c_pull.i2c.scl", pads: [["U26", "39"], ["U25", "6"], ["U1", "5"], ["U4", "5"], ["U29", "14"], ["U32", "1"], ["U33", "1"], ["U34", "14"], ["U37", "2"], ["R60", "2"], ["TP11", "1"], ["J3", "13"]]},
  {name: "i2c_pull.i2c.sda", pads: [["U26", "38"], ["U25", "7"], ["U1", "6"], ["U4", "6"], ["U29", "15"], ["U32", "6"], ["U33", "6"], ["U34", "15"], ["U37", "3"], ["R61", "2"], ["TP12", "1"], ["J3", "14"], ["J3", "15"]]},
  {name: "pd.int", pads: [["U26", "21"], ["U25", "5"]]},
  {name: "oled.reset", pads: [["J3", "9"], ["R63", "2"], ["C72", "1"]]},
  {name: "control.high_gate_ctl", pads: [["U29", "4"], ["U15", "3"]]},
  {name: "control.low_gate_ctl", pads: [["U29", "5"], ["U16", "3"]]},
  {name: "ioe_ctl.io.irange_0", pads: [["U29", "9"], ["U17", "3"], ["U18", "1"]]},
  {name: "ioe_ctl.io.irange_1", pads: [["U29", "10"], ["U19", "3"], ["U20", "1"]]},
  {name: "ioe_ctl.io.irange_2", pads: [["U29", "11"], ["U21", "3"], ["U22", "1"]]},
  {name: "ioe_ctl.io.off_0", pads: [["U29", "12"], ["U14", "6"]]},
  {name: "precharge.control", pads: [["U29", "6"], ["Q1", "1"]]},
  {name: "buck_rc.input", pads: [["U26", "35"], ["R64", "1"]]},
  {name: "buck_rc.output", pads: [["U5", "2"], ["R64", "2"], ["C74", "1"]]},
  {name: "boost_rc.input", pads: [["U26", "32"], ["R65", "1"]]},
  {name: "boost_rc.output", pads: [["U6", "2"], ["R65", "2"], ["C75", "1"]]},
  {name: "conv_en_pull.io", pads: [["U26", "33"], ["U31", "5"], ["R68", "2"]]},
  {name: "conv_ovp.output", pads: [["U30", "4"], ["U31", "1"], ["R69", "2"]]},
  {name: "conv_latch.out", pads: [["U29", "7"], ["U31", "7"], ["U31", "6"], ["U5", "3"], ["U6", "3"]]},
  {name: "conv_sense.output", pads: [["U26", "18"], ["R70", "2"], ["R71", "1"]]},
  {name: "enc.a", pads: [["U26", "5"], ["SW1", "A"]]},
  {name: "enc.b", pads: [["U26", "6"], ["SW1", "B"]]},
  {name: "enc.sw", pads: [["U26", "4"], ["SW1", "S1"]]},
  {name: "dir.a", pads: [["U34", "4"], ["SW2", "1"]]},
  {name: "dir.b", pads: [["U34", "5"], ["SW2", "4"]]},
  {name: "dir.c", pads: [["U34", "6"], ["SW2", "3"]]},
  {name: "dir.d", pads: [["U34", "7"], ["SW2", "6"]]},
  {name: "dir.center", pads: [["U34", "9"], ["SW2", "2"]]},
  {name: "ioe_ui.io.rgb_red", pads: [["U34", "10"], ["R72", "2"]]},
  {name: "ioe_ui.io.rgb_green", pads: [["U34", "11"], ["R73", "2"]]},
  {name: "ioe_ui.io.rgb_blue", pads: [["U34", "12"], ["R74", "2"]]},
  {name: "qwiic_pull.i2c.scl", pads: [["U26", "24"], ["R75", "2"], ["J4", "4"]]},
  {name: "qwiic_pull.i2c.sda", pads: [["U26", "25"], ["J4", "3"], ["R76", "2"]]},
  {name: "dutio.io0", pads: [["U26", "15"], ["J5", "2"]]},
  {name: "dutio.io1", pads: [["U26", "17"], ["J5", "3"]]},
  {name: "touch_duck.pad", pads: [["U26", "22"], ["U35", "1"]]},
  {name: "fan_drv.control", pads: [["U26", "19"], ["Q9", "1"]]},
  {name: "fan.pwr", pads: [["J6", "2"], ["Q10", "3"]]},
  {name: "spk_drv.i2s.sck", pads: [["U26", "23"], ["U36", "16"]]},
  {name: "spk_drv.i2s.ws", pads: [["U26", "31"], ["U36", "14"]]},
  {name: "spk_drv.i2s.sd", pads: [["U26", "34"], ["U36", "1"]]},
  {name: "spk_drv.out.a", pads: [["U36", "9"], ["J7", "1"]]},
  {name: "spk_drv.out.b", pads: [["U36", "10"], ["J7", "2"]]},
  {name: "dac_ferrite.pwr_out", pads: [["FB3", "2"], ["U37", "1"], ["U37", "4"], ["C83", "1"], ["C84", "1"]]},
  {name: "dac.out0", pads: [["U37", "6"], ["R78", "1"], ["R25", "1"], ["C85", "1"]]},
  {name: "dac.out3", pads: [["U37", "9"], ["R79", "1"], ["R28", "1"], ["C88", "1"]]},
  {name: "dac.out1", pads: [["U37", "7"], ["R80", "1"], ["R31", "1"], ["C86", "1"]]},
  {name: "dac.out2", pads: [["U37", "8"], ["R81", "1"], ["R29", "1"], ["C87", "1"]]},
  {name: "adc.spi.sck", pads: [["U38", "14"], ["U26", "8"]]},
  {name: "adc.spi.mosi", pads: [["U38", "15"], ["U26", "9"]]},
  {name: "adc.spi.miso", pads: [["U38", "16"], ["U26", "10"]]},
  {name: "adc.cs", pads: [["U38", "13"], ["U26", "7"]]},
  {name: "adc.mclkin", pads: [["U38", "18"], ["U26", "12"]]},
  {name: "vcen_rc.output", pads: [["U38", "5"], ["R85", "2"], ["C94", "1"]]},
  {name: "control.meas_i", pads: [["R86", "1"], ["R87", "1"], ["jfet6", "2"], ["R30", "1"], ["R32", "1"]]},
  {name: "mi_rc.output", pads: [["U38", "6"], ["R87", "2"], ["C95", "1"]]},
  {name: "control.meas_v", pads: [["R88", "1"], ["R89", "1"], ["jfet4", "2"], ["R26", "1"]]},
  {name: "mv_rc.output", pads: [["U38", "7"], ["R89", "2"], ["C96", "1"]]},
  {name: "control.limit_source", pads: [["U12", "4"], ["U26", "20"], ["TP13", "1"]]},
  {name: "control.limit_sink", pads: [["U13", "4"], ["U26", "11"], ["TP14", "1"]]},
  {name: "dummy_amp_lv.output", pads: [["U41", "6"], ["U41", "7"]]},
  {name: "dummy_amp_hv.output", pads: [["U39", "6"], ["U39", "7"]]},
  {name: "outp.port", pads: [["J16", "1"], ["J17", "2"], ["tvs_p1", "1"], ["R56", "1"], ["R35", "1"], ["U18", "6"], ["U20", "4"], ["U22", "4"]]},
  {name: "vimeas_amps.inp.0", pads: [["U39", "3"], ["R35", "2"]]},
  {name: "control.outa", pads: [["U39", "2"], ["U39", "1"], ["R21", "1"], ["R43", "1"]]},
  {name: "ampdmeas_amps.inp.0", pads: [["U40", "3"], ["U43", "1"], ["C48", "1"]]},
  {name: "ampdmeas_amps.inn.0", pads: [["U40", "2"], ["R36", "2"], ["R37", "1"]]},
  {name: "control.drive", pads: [["U40", "1"], ["R36", "1"], ["R22", "1"], ["R38", "1"]]},
  {name: "ampdmeas_amps.inp.1", pads: [["U40", "5"], ["R22", "2"], ["R24", "2"]]},
  {name: "ampdmeas_amps.inn.1", pads: [["U40", "6"], ["R21", "2"], ["R23", "2"]]},
  {name: "ampdmeas_amps.out.1", pads: [["U40", "7"], ["R23", "1"], ["jfet1", "2"]]},
  {name: "cv_amps.inp.0", pads: [["U41", "3"], ["R25", "2"], ["R26", "2"], ["R28", "2"], ["C42", "1"]]},
  {name: "cv_amps.inn.0", pads: [["U41", "2"], ["R27", "2"], ["U12", "3"], ["U13", "1"], ["U14", "3"], ["U42", "6"], ["U42", "2"], ["D8", "1"], ["D9", "2"]]},
  {name: "cv_amps.out.0", pads: [["U41", "1"], ["R27", "1"]]},
  {name: "ci_amps.inp.0", pads: [["U42", "3"], ["R31", "2"], ["R32", "2"], ["C44", "1"]]},
  {name: "ci_amps.out.0", pads: [["U42", "1"], ["D9", "1"], ["U13", "3"]]},
  {name: "ci_amps.inp.1", pads: [["U42", "5"], ["R29", "2"], ["R30", "2"], ["C43", "1"]]},
  {name: "ci_amps.out.1", pads: [["U42", "7"], ["D8", "2"], ["U12", "1"]]},
  {name: "cintref_amps.inn.0", pads: [["U43", "2"], ["R34", "2"], ["C48", "2"]]},
  {name: "reg_v5.fb.output", pads: [["U2", "4"], ["R2", "2"], ["R3", "1"]]},
  {name: "reg_v5.boot_cap.neg", pads: [["C3", "2"], ["U2", "2"], ["L1", "1"]]},
  {name: "reg_v5.boot_cap.pos", pads: [["C3", "1"], ["U2", "6"]]},
  {name: "reg_v5.en_res.b", pads: [["R4", "2"], ["U2", "5"]]},
  {name: "reg_3v3.fb.output", pads: [["U3", "4"], ["R5", "2"], ["R6", "1"]]},
  {name: "reg_3v3.boot_cap.neg", pads: [["C7", "2"], ["U3", "2"], ["L2", "1"]]},
  {name: "reg_3v3.boot_cap.pos", pads: [["C7", "1"], ["U3", "6"]]},
  {name: "reg_3v3.en_res.b", pads: [["R7", "2"], ["U3", "5"]]},
  {name: "precharge.switch.pre.drain", pads: [["Q1", "3"], ["R9", "2"], ["Q2", "4"]]},
  {name: "conv.sw_in_force", pads: [["Q3", "2"], ["Q4", "3"], ["L3", "1"], ["U5", "7"], ["C26", "2"]]},
  {name: "conv.sw_out_force", pads: [["L3", "2"], ["Q5", "2"], ["Q6", "3"], ["U6", "7"], ["C28", "2"]]},
  {name: "conv.buck_sw.low_gate_res.a", pads: [["R11", "1"], ["U5", "5"]]},
  {name: "conv.buck_sw.low_gate_res.b", pads: [["R11", "2"], ["Q3", "1"]]},
  {name: "conv.buck_sw.high_gate_res.a", pads: [["R12", "1"], ["U5", "8"]]},
  {name: "conv.buck_sw.high_gate_res.b", pads: [["R12", "2"], ["Q4", "1"]]},
  {name: "conv.buck_sw.driver.ic.bst", pads: [["U5", "1"], ["D3", "1"], ["C26", "1"]]},
  {name: "conv.boost_sw.low_gate_res.a", pads: [["R13", "1"], ["U6", "5"]]},
  {name: "conv.boost_sw.low_gate_res.b", pads: [["R13", "2"], ["Q5", "1"]]},
  {name: "conv.boost_sw.high_gate_res.a", pads: [["R14", "1"], ["U6", "8"]]},
  {name: "conv.boost_sw.high_gate_res.b", pads: [["R14", "2"], ["Q6", "1"]]},
  {name: "conv.boost_sw.driver.ic.bst", pads: [["U6", "1"], ["D4", "1"], ["C28", "1"]]},
  {name: "reg_v12.fb.output", pads: [["U7", "3"], ["C31", "2"], ["R15", "2"], ["R16", "1"]]},
  {name: "reg_v12.power_path.switch", pads: [["U7", "1"], ["L4", "2"], ["D6", "2"]]},
  {name: "reg_vcontrol.fb.output", pads: [["U10", "3"], ["C38", "2"], ["R19", "2"], ["R20", "1"]]},
  {name: "reg_vcontrol.power_path.switch", pads: [["U10", "1"], ["L5", "2"], ["D7", "2"]]},
  {name: "reg_vcontroln.cf.neg", pads: [["C39", "2"], ["U11", "3"]]},
  {name: "reg_vcontroln.cf.pos", pads: [["C39", "1"], ["U11", "6"]]},
  {name: "control.int_link", pads: [["U14", "4"], ["R34", "1"]]},
  {name: "control.dclamp.output", pads: [["jfet2", "2"], ["U14", "1"]]},
  {name: "control.driver.out", pads: [["R41", "2"], ["Q7", "3"], ["D11", "2"], ["Q8", "3"], ["R42", "2"], ["R45", "1"], ["R47", "1"], ["R49", "1"], ["R51", "1"]]},
  {name: "control.vdiv.output", pads: [["U23", "4"], ["C54", "1"], ["R43", "2"], ["R44", "1"]]},
  {name: "control.isense.sense_out", pads: [["R52", "1"], ["U17", "6"], ["U19", "6"], ["U21", "6"]]},
  {name: "control.ifilt.outp", pads: [["U24", "4"], ["R51", "2"], ["C58", "1"]]},
  {name: "control.ifilt.outn", pads: [["U24", "1"], ["R52", "2"], ["C58", "2"]]},
  {name: "control.vmeas.output", pads: [["U23", "7"], ["jfet3", "2"]]},
  {name: "control.imeas.output", pads: [["U24", "7"], ["jfet5", "2"]]},
  {name: "control.snub_r.pwr_out", pads: [["R56", "2"], ["C61", "1"]]},
  {name: "control.tvs_p.ports.2", pads: [["tvs_p1", "2"], ["tvs_n1", "2"]]},
  {name: "control.dclamp.r.a", pads: [["jfet1", "1"], ["R33", "1"], ["jfet2", "3"]]},
  {name: "control.dclamp.r.b", pads: [["jfet1", "3"], ["R33", "2"], ["jfet2", "1"]]},
  {name: "control.driver.res.b", pads: [["R40", "2"], ["D10", "2"], ["U16", "1"], ["U15", "1"]]},
  {name: "control.driver.high_fet.gate", pads: [["Q7", "1"], ["R41", "1"], ["U15", "6"]]},
  {name: "control.driver.low_fet.gate", pads: [["Q8", "1"], ["R42", "1"], ["U16", "6"]]},
  {name: "control.driver.clamp1.cathode", pads: [["D10", "1"], ["D11", "1"]]},
  {name: "control.driver.res.res[0].b", pads: [["R38", "2"], ["R39", "1"]]},
  {name: "control.driver.res.res[1].b", pads: [["R39", "2"], ["R40", "1"]]},
  {name: "control.isense.ranges[0].isense.pwr_out", pads: [["U18", "4"], ["R45", "2"], ["U17", "1"]]},
  {name: "control.isense.ranges[0].pwr_sw.res.a", pads: [["R46", "1"], ["U18", "2"]]},
  {name: "control.isense.ranges[1].isense.pwr_out", pads: [["U20", "3"], ["R47", "2"], ["U19", "1"]]},
  {name: "control.isense.ranges[1].pwr_sw.res.a", pads: [["R48", "1"], ["U20", "2"]]},
  {name: "control.isense.ranges[2].isense.pwr_out", pads: [["U22", "3"], ["R49", "2"], ["U21", "1"]]},
  {name: "control.isense.ranges[2].pwr_sw.res.a", pads: [["R50", "1"], ["U22", "2"]]},
  {name: "control.vmeas.rg.a", pads: [["R53", "1"], ["U23", "2"]]},
  {name: "control.vmeas.rg.b", pads: [["R53", "2"], ["U23", "3"]]},
  {name: "control.imeas.rg.a", pads: [["R54", "1"], ["U24", "2"]]},
  {name: "control.imeas.rg.b", pads: [["R54", "2"], ["U24", "3"]]},
  {name: "control.vclamp.r.a", pads: [["jfet3", "1"], ["R55", "1"], ["jfet4", "3"]]},
  {name: "control.vclamp.r.b", pads: [["jfet3", "3"], ["R55", "2"], ["jfet4", "1"]]},
  {name: "control.iclamp.r.a", pads: [["jfet5", "1"], ["R57", "1"], ["jfet6", "3"]]},
  {name: "control.iclamp.r.b", pads: [["jfet5", "3"], ["R57", "2"], ["jfet6", "1"]]},
  {name: "pd.ic.vconn", pads: [["U25", "12"], ["U25", "13"]]},
  {name: "mcu.program_uart_node.a_tx", pads: [["U26", "37"], ["J2", "3"]]},
  {name: "mcu.program_uart_node.b_tx", pads: [["U26", "36"], ["J2", "4"]]},
  {name: "mcu.program_en_node", pads: [["U26", "3"], ["J2", "6"], ["R58", "2"], ["C66", "1"]]},
  {name: "led.res.a", pads: [["R59", "1"], ["D12", "1"]]},
  {name: "oled.iref_res.a", pads: [["R62", "1"], ["J3", "21"]]},
  {name: "oled.device.vcomh", pads: [["J3", "22"], ["C67", "1"]]},
  {name: "conv_ovp.comp.inp", pads: [["U30", "1"], ["R66", "2"], ["R67", "1"]]},
  {name: "conv_latch.ic.out2", pads: [["U31", "3"], ["U31", "2"]]},
  {name: "pass_temp.alert", pads: [["U32", "3"]]},
  {name: "conv_temp.alert", pads: [["U33", "3"]]},
  {name: "rgb.red_res.a", pads: [["R72", "1"], ["D13", "3"]]},
  {name: "rgb.green_res.a", pads: [["R73", "1"], ["D13", "4"]]},
  {name: "rgb.blue_res.a", pads: [["R74", "1"], ["D13", "1"]]},
  {name: "fan_drv.pre.drain", pads: [["Q9", "3"], ["R77", "2"], ["Q10", "1"]]},
  {name: "dac.rdy", pads: [["U37", "5"]]},
  {name: "tp_cv.res.b", pads: [["R78", "2"], ["J8", "1"]]},
  {name: "tp_cvf.res.b", pads: [["R79", "2"], ["J9", "1"]]},
  {name: "tp_cisrc.res.b", pads: [["R80", "2"], ["J10", "1"]]},
  {name: "tp_cisnk.res.b", pads: [["R81", "2"], ["J11", "1"]]},
  {name: "adc.vins.3", pads: [["U38", "8"]]},
  {name: "adc.vins.4", pads: [["U38", "9"]]},
  {name: "adc.vins.5", pads: [["U38", "10"]]},
  {name: "adc.vins.6", pads: [["U38", "11"]]},
  {name: "adc.vins.7", pads: [["U38", "12"]]},
  {name: "adc.ic.avdd", pads: [["U38", "1"], ["R82", "2"], ["C89", "1"], ["C90", "1"]]},
  {name: "adc.ic.dvdd", pads: [["U38", "20"], ["R83", "2"], ["C91", "1"], ["C92", "1"]]},
  {name: "tp_vcen.res.b", pads: [["R84", "2"], ["J12", "1"]]},
  {name: "tp_mi.res.b", pads: [["R86", "2"], ["J13", "1"]]},
  {name: "tp_mv.res.b", pads: [["R88", "2"], ["J14", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(6.836614173228348, 5.268503937007874);
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


