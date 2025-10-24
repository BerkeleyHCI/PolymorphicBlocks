const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.000, 5.062), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.039, 5.062), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.000, 5.102), rotate: 0,
  id: 'H3'
})
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(4.969, 3.549), rotate: 0,
  id: 'J1'
})
// tp_gnd.tp
const TP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.490, 4.827), rotate: 0,
  id: 'TP1'
})
// vusb_sense.ic
const U1 = board.add(SOT_23_8, {
  translate: pt(4.244, 3.452), rotate: 0,
  id: 'U1'
})
// vusb_sense.vs_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(4.222, 3.714), rotate: 0,
  id: 'C1'
})
// vusb_sense.Rs.res.res
const R1 = board.add(R_1206_3216Metric, {
  translate: pt(4.254, 3.602), rotate: 0,
  id: 'R1'
})
// fuse_vusb.fuse
const F1 = board.add(Fuseholder_Littelfuse_Nano2_154x, {
  translate: pt(0.219, 4.563), rotate: 0,
  id: 'F1'
})
// filt_vusb.fb
const FB1 = board.add(L_1206_3216Metric, {
  translate: pt(2.213, 4.837), rotate: 0,
  id: 'FB1'
})
// prot_vusb.diode
const D1 = board.add(D_SMA, {
  translate: pt(1.077, 4.859), rotate: 0,
  id: 'D1'
})
// ramp.drv
const Q1 = board.add(PQFN_8_EP_6x5mm_P1_27mm_Generic, {
  translate: pt(2.619, 3.493), rotate: 0,
  id: 'Q1'
})
// ramp.cap_gd
const C2 = board.add(C_0603_1608Metric, {
  translate: pt(2.720, 3.669), rotate: 0,
  id: 'C2'
})
// ramp.cap_gs
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(2.556, 3.679), rotate: 0,
  id: 'C3'
})
// ramp.div.top_res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(2.876, 3.669), rotate: 0,
  id: 'R2'
})
// ramp.div.bottom_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(2.547, 3.786), rotate: 0,
  id: 'R3'
})
// ramp.ctl_fet
const Q2 = board.add(SOT_23, {
  translate: pt(2.880, 3.452), rotate: 0,
  id: 'Q2'
})
// cap_conv.cap
const C4 = board.add(CP_Elec_6_3x7_7, {
  translate: pt(5.049, 4.135), rotate: 0,
  id: 'C4'
})
// tp_vusb.tp
const TP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.741, 4.827), rotate: 0,
  id: 'TP2'
})
// reg_v5.ic
const U2 = board.add(SOT_23_6, {
  translate: pt(2.127, 3.452), rotate: 0,
  id: 'U2'
})
// reg_v5.fb.div.top_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(2.239, 3.670), rotate: 0,
  id: 'R4'
})
// reg_v5.fb.div.bottom_res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(1.845, 3.800), rotate: 0,
  id: 'R5'
})
// reg_v5.hf_in_cap.cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(2.001, 3.800), rotate: 0,
  id: 'C5'
})
// reg_v5.boot_cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(2.157, 3.800), rotate: 0,
  id: 'C6'
})
// reg_v5.power_path.inductor
const L1 = board.add(L_Sunlord_SWPA5040S, {
  translate: pt(1.897, 3.493), rotate: 0,
  id: 'L1'
})
// reg_v5.power_path.in_cap.cap
const C7 = board.add(C_0805_2012Metric, {
  translate: pt(2.074, 3.680), rotate: 0,
  id: 'C7'
})
// reg_v5.power_path.out_cap.cap
const C8 = board.add(C_1206_3216Metric, {
  translate: pt(1.877, 3.687), rotate: 0,
  id: 'C8'
})
// reg_v5.en_res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(2.313, 3.800), rotate: 0,
  id: 'R6'
})
// tp_v5.tp
const TP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.991, 4.827), rotate: 0,
  id: 'TP3'
})
// reg_3v3.ic
const U3 = board.add(SOT_23_6, {
  translate: pt(5.192, 1.831), rotate: 0,
  id: 'U3'
})
// reg_3v3.fb.div.top_res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(4.909, 2.180), rotate: 0,
  id: 'R7'
})
// reg_3v3.fb.div.bottom_res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(5.065, 2.180), rotate: 0,
  id: 'R8'
})
// reg_3v3.hf_in_cap.cap
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(5.221, 2.180), rotate: 0,
  id: 'C9'
})
// reg_3v3.boot_cap
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(5.377, 2.180), rotate: 0,
  id: 'C10'
})
// reg_3v3.power_path.inductor
const L2 = board.add(L_Sunlord_SWPA5040S, {
  translate: pt(4.961, 1.873), rotate: 0,
  id: 'L2'
})
// reg_3v3.power_path.in_cap.cap.c[0]
const C11 = board.add(C_1206_3216Metric, {
  translate: pt(4.942, 2.066), rotate: 0,
  id: 'C11'
})
// reg_3v3.power_path.in_cap.cap.c[1]
const C12 = board.add(C_1206_3216Metric, {
  translate: pt(5.162, 2.066), rotate: 0,
  id: 'C12'
})
// reg_3v3.power_path.out_cap.cap
const C13 = board.add(C_0805_2012Metric, {
  translate: pt(5.359, 2.059), rotate: 0,
  id: 'C13'
})
// reg_3v3.en_res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(4.909, 2.276), rotate: 0,
  id: 'R9'
})
// prot_3v3.diode
const D2 = board.add(D_SMA, {
  translate: pt(1.471, 4.859), rotate: 0,
  id: 'D2'
})
// tp_3v3.tp
const TP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.241, 4.827), rotate: 0,
  id: 'TP4'
})
// reg_v12.ic
const U4 = board.add(SOT_23_5, {
  translate: pt(5.377, 3.452), rotate: 0,
  id: 'U4'
})
// reg_v12.fb.div.top_res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(5.697, 3.587), rotate: 0,
  id: 'R10'
})
// reg_v12.fb.div.bottom_res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(5.354, 3.701), rotate: 0,
  id: 'R11'
})
// reg_v12.power_path.inductor
const L3 = board.add(L_0805_2012Metric, {
  translate: pt(5.531, 3.591), rotate: 0,
  id: 'L3'
})
// reg_v12.power_path.in_cap.cap
const C14 = board.add(C_0805_2012Metric, {
  translate: pt(5.564, 3.423), rotate: 0,
  id: 'C14'
})
// reg_v12.power_path.out_cap.cap
const C15 = board.add(C_0603_1608Metric, {
  translate: pt(5.510, 3.701), rotate: 0,
  id: 'C15'
})
// reg_v12.cf
const C16 = board.add(C_0603_1608Metric, {
  translate: pt(5.666, 3.701), rotate: 0,
  id: 'C16'
})
// reg_v12.rect
const D3 = board.add(D_SOD_323, {
  translate: pt(5.359, 3.595), rotate: 0,
  id: 'D3'
})
// convin_sense.ic
const U5 = board.add(SOT_23_8, {
  translate: pt(4.542, 3.452), rotate: 0,
  id: 'U5'
})
// convin_sense.vs_cap.cap
const C17 = board.add(C_0603_1608Metric, {
  translate: pt(4.520, 3.714), rotate: 0,
  id: 'C17'
})
// convin_sense.Rs.res.res
const R12 = board.add(R_1206_3216Metric, {
  translate: pt(4.551, 3.602), rotate: 0,
  id: 'R12'
})
// conv.power_path.inductor
const L4 = board.add(L_Bourns_SRP1245A, {
  translate: pt(2.593, 2.020), rotate: 0,
  id: 'L4'
})
// conv.power_path.in_cap.cap.c[0]
const C18 = board.add(C_1206_3216Metric, {
  translate: pt(2.725, 2.361), rotate: 0,
  id: 'C18'
})
// conv.power_path.in_cap.cap.c[1]
const C19 = board.add(C_1206_3216Metric, {
  translate: pt(2.946, 2.361), rotate: 0,
  id: 'C19'
})
// conv.power_path.in_cap.cap.c[2]
const C20 = board.add(C_1206_3216Metric, {
  translate: pt(3.166, 2.361), rotate: 0,
  id: 'C20'
})
// conv.power_path.in_cap.cap.c[3]
const C21 = board.add(C_1206_3216Metric, {
  translate: pt(3.387, 2.361), rotate: 0,
  id: 'C21'
})
// conv.power_path.in_cap.cap.c[4]
const C22 = board.add(C_1206_3216Metric, {
  translate: pt(3.607, 2.361), rotate: 0,
  id: 'C22'
})
// conv.power_path.in_cap.cap.c[5]
const C23 = board.add(C_1206_3216Metric, {
  translate: pt(2.394, 2.613), rotate: 0,
  id: 'C23'
})
// conv.power_path.in_cap.cap.c[6]
const C24 = board.add(C_1206_3216Metric, {
  translate: pt(2.615, 2.613), rotate: 0,
  id: 'C24'
})
// conv.power_path.out_cap.cap.c[0]
const C25 = board.add(C_1206_3216Metric, {
  translate: pt(2.835, 2.613), rotate: 0,
  id: 'C25'
})
// conv.power_path.out_cap.cap.c[1]
const C26 = board.add(C_1206_3216Metric, {
  translate: pt(3.056, 2.613), rotate: 0,
  id: 'C26'
})
// conv.power_path.out_cap.cap.c[2]
const C27 = board.add(C_1206_3216Metric, {
  translate: pt(3.276, 2.613), rotate: 0,
  id: 'C27'
})
// conv.power_path.out_cap.cap.c[3]
const C28 = board.add(C_1206_3216Metric, {
  translate: pt(3.497, 2.613), rotate: 0,
  id: 'C28'
})
// conv.power_path.out_cap.cap.c[4]
const C29 = board.add(C_1206_3216Metric, {
  translate: pt(3.717, 2.613), rotate: 0,
  id: 'C29'
})
// conv.power_path.out_cap.cap.c[5]
const C30 = board.add(C_1206_3216Metric, {
  translate: pt(2.394, 2.743), rotate: 0,
  id: 'C30'
})
// conv.power_path.out_cap.cap.c[6]
const C31 = board.add(C_1206_3216Metric, {
  translate: pt(2.615, 2.743), rotate: 0,
  id: 'C31'
})
// conv.power_path.out_cap.cap.c[7]
const C32 = board.add(C_1206_3216Metric, {
  translate: pt(2.835, 2.743), rotate: 0,
  id: 'C32'
})
// conv.buck_sw.driver.ic
const U6 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(3.383, 2.126), rotate: 0,
  id: 'U6'
})
// conv.buck_sw.driver.cap.cap
const C33 = board.add(C_0603_1608Metric, {
  translate: pt(3.355, 2.726), rotate: 0,
  id: 'C33'
})
// conv.buck_sw.driver.high_cap.cap
const C34 = board.add(C_0603_1608Metric, {
  translate: pt(3.511, 2.726), rotate: 0,
  id: 'C34'
})
// conv.buck_sw.driver.boot
const D4 = board.add(D_SOD_323, {
  translate: pt(3.029, 2.735), rotate: 0,
  id: 'D4'
})
// conv.buck_sw.low_fet
const Q3 = board.add(PQFN_8_EP_6x5mm_P1_27mm_Generic, {
  translate: pt(3.052, 1.872), rotate: 0,
  id: 'Q3'
})
// conv.buck_sw.low_gate_res
const R13 = board.add(R_0603_1608Metric, {
  translate: pt(3.667, 2.726), rotate: 0,
  id: 'R13'
})
// conv.buck_sw.high_fet
const Q4 = board.add(PQFN_8_EP_6x5mm_P1_27mm_Generic, {
  translate: pt(3.367, 1.872), rotate: 0,
  id: 'Q4'
})
// conv.buck_sw.high_gate_res
const R14 = board.add(R_0603_1608Metric, {
  translate: pt(2.362, 2.856), rotate: 0,
  id: 'R14'
})
// conv.boost_sw.driver.ic
const U7 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.450, 2.422), rotate: 0,
  id: 'U7'
})
// conv.boost_sw.driver.cap.cap
const C35 = board.add(C_0603_1608Metric, {
  translate: pt(2.518, 2.856), rotate: 0,
  id: 'C35'
})
// conv.boost_sw.driver.high_cap.cap
const C36 = board.add(C_0603_1608Metric, {
  translate: pt(2.674, 2.856), rotate: 0,
  id: 'C36'
})
// conv.boost_sw.driver.boot
const D5 = board.add(D_SOD_323, {
  translate: pt(3.194, 2.735), rotate: 0,
  id: 'D5'
})
// conv.boost_sw.low_fet
const Q5 = board.add(PQFN_8_EP_6x5mm_P1_27mm_Generic, {
  translate: pt(3.682, 1.872), rotate: 0,
  id: 'Q5'
})
// conv.boost_sw.low_gate_res
const R15 = board.add(R_0603_1608Metric, {
  translate: pt(2.830, 2.856), rotate: 0,
  id: 'R15'
})
// conv.boost_sw.high_fet
const Q6 = board.add(PQFN_8_EP_6x5mm_P1_27mm_Generic, {
  translate: pt(3.052, 2.128), rotate: 0,
  id: 'Q6'
})
// conv.boost_sw.high_gate_res
const R16 = board.add(R_0603_1608Metric, {
  translate: pt(2.986, 2.856), rotate: 0,
  id: 'R16'
})
// prot_conv.diode
const D6 = board.add(D_SMA, {
  translate: pt(1.865, 4.859), rotate: 0,
  id: 'D6'
})
// tp_conv.tp
const TP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.492, 4.827), rotate: 0,
  id: 'TP5'
})
// reg_analog.ic
const U8 = board.add(SOT_23_5, {
  translate: pt(3.945, 3.452), rotate: 0,
  id: 'U8'
})
// reg_analog.in_cap.cap
const C37 = board.add(C_0603_1608Metric, {
  translate: pt(3.923, 3.717), rotate: 0,
  id: 'C37'
})
// reg_analog.out_cap.cap
const C38 = board.add(C_1206_3216Metric, {
  translate: pt(3.955, 3.603), rotate: 0,
  id: 'C38'
})
// tp_analog.tp
const TP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.742, 4.827), rotate: 0,
  id: 'TP6'
})
// reg_vref.ic
const U9 = board.add(SOT_23, {
  translate: pt(6.261, 4.062), rotate: 0,
  id: 'U9'
})
// reg_vref.in_cap.cap
const C39 = board.add(C_0603_1608Metric, {
  translate: pt(6.244, 4.197), rotate: 0,
  id: 'C39'
})
// tp_vref.tp
const TP7 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.993, 4.827), rotate: 0,
  id: 'TP7'
})
// ref_div.div.top_res
const R17 = board.add(R_0603_1608Metric, {
  translate: pt(5.039, 4.482), rotate: 0,
  id: 'R17'
})
// ref_div.div.bottom_res
const R18 = board.add(R_0603_1608Metric, {
  translate: pt(5.039, 4.579), rotate: 0,
  id: 'R18'
})
// ref_rc.rc.r
const R19 = board.add(R_0603_1608Metric, {
  translate: pt(5.274, 4.482), rotate: 0,
  id: 'R19'
})
// ref_rc.rc.c
const C40 = board.add(C_0603_1608Metric, {
  translate: pt(5.274, 4.579), rotate: 0,
  id: 'C40'
})
// reg_vcontrol.ic
const U10 = board.add(SOT_23_5, {
  translate: pt(5.954, 3.452), rotate: 0,
  id: 'U10'
})
// reg_vcontrol.fb.div.top_res
const R20 = board.add(R_0603_1608Metric, {
  translate: pt(6.098, 3.587), rotate: 0,
  id: 'R20'
})
// reg_vcontrol.fb.div.bottom_res
const R21 = board.add(R_0603_1608Metric, {
  translate: pt(6.254, 3.587), rotate: 0,
  id: 'R21'
})
// reg_vcontrol.power_path.inductor
const L5 = board.add(L_0603_1608Metric, {
  translate: pt(5.932, 3.701), rotate: 0,
  id: 'L5'
})
// reg_vcontrol.power_path.in_cap.cap
const C41 = board.add(C_0603_1608Metric, {
  translate: pt(6.088, 3.701), rotate: 0,
  id: 'C41'
})
// reg_vcontrol.power_path.out_cap.cap
const C42 = board.add(C_0805_2012Metric, {
  translate: pt(6.141, 3.423), rotate: 0,
  id: 'C42'
})
// reg_vcontrol.cf
const C43 = board.add(C_0603_1608Metric, {
  translate: pt(6.244, 3.701), rotate: 0,
  id: 'C43'
})
// reg_vcontrol.rect
const D7 = board.add(D_SOD_323, {
  translate: pt(5.937, 3.595), rotate: 0,
  id: 'D7'
})
// tp_vcontrol.tp
const TP8 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.243, 4.827), rotate: 0,
  id: 'TP8'
})
// filt_vcontroln.fb
const FB2 = board.add(L_0603_1608Metric, {
  translate: pt(4.736, 4.819), rotate: 0,
  id: 'FB2'
})
// reg_vcontroln.ic
const U11 = board.add(SOT_23_6, {
  translate: pt(3.646, 3.452), rotate: 0,
  id: 'U11'
})
// reg_vcontroln.cf
const C44 = board.add(C_0805_2012Metric, {
  translate: pt(3.632, 3.726), rotate: 0,
  id: 'C44'
})
// reg_vcontroln.cout.cap
const C45 = board.add(C_1206_3216Metric, {
  translate: pt(3.656, 3.603), rotate: 0,
  id: 'C45'
})
// tp_vcontroln.tp
const TP9 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.493, 4.827), rotate: 0,
  id: 'TP9'
})
// control.dmeas.r1
const R22 = board.add(R_0603_1608Metric, {
  translate: pt(1.761, 2.831), rotate: 0,
  id: 'R22'
})
// control.dmeas.r2
const R23 = board.add(R_0603_1608Metric, {
  translate: pt(1.917, 2.831), rotate: 0,
  id: 'R23'
})
// control.dmeas.rf
const R24 = board.add(R_0603_1608Metric, {
  translate: pt(2.072, 2.831), rotate: 0,
  id: 'R24'
})
// control.dmeas.rg
const R25 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.947), rotate: 0,
  id: 'R25'
})
// control.err_volt.rtop
const R26 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.947), rotate: 0,
  id: 'R26'
})
// control.err_volt.rbot
const R27 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 2.947), rotate: 0,
  id: 'R27'
})
// control.err_volt.rout
const R28 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 2.947), rotate: 0,
  id: 'R28'
})
// control.err_volt.cin.cap
const C46 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 2.947), rotate: 0,
  id: 'C46'
})
// control.err_volt.rfine
const R29 = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 2.947), rotate: 0,
  id: 'R29'
})
// control.err_source.rtop
const R30 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 2.947), rotate: 0,
  id: 'R30'
})
// control.err_source.rbot
const R31 = board.add(R_0603_1608Metric, {
  translate: pt(1.150, 2.947), rotate: 0,
  id: 'R31'
})
// control.err_source.diode
const D8 = board.add(D_SOD_323, {
  translate: pt(1.103, 2.839), rotate: 0,
  id: 'D8'
})
// control.err_source.cin.cap
const C47 = board.add(C_0603_1608Metric, {
  translate: pt(1.306, 2.947), rotate: 0,
  id: 'C47'
})
// control.err_sink.rtop
const R32 = board.add(R_0603_1608Metric, {
  translate: pt(1.461, 2.947), rotate: 0,
  id: 'R32'
})
// control.err_sink.rbot
const R33 = board.add(R_0603_1608Metric, {
  translate: pt(1.617, 2.947), rotate: 0,
  id: 'R33'
})
// control.err_sink.diode
const D9 = board.add(D_SOD_323, {
  translate: pt(1.269, 2.839), rotate: 0,
  id: 'D9'
})
// control.err_sink.cin.cap
const C48 = board.add(C_0603_1608Metric, {
  translate: pt(1.773, 2.947), rotate: 0,
  id: 'C48'
})
// control.comp_source.ic
const U12 = board.add(SOT_353_SC_70_5, {
  translate: pt(1.227, 2.684), rotate: 0,
  id: 'U12'
})
// control.comp_source.vdd_cap.cap
const C49 = board.add(C_0603_1608Metric, {
  translate: pt(1.929, 2.947), rotate: 0,
  id: 'C49'
})
// control.comp_sink.ic
const U13 = board.add(SOT_353_SC_70_5, {
  translate: pt(1.392, 2.684), rotate: 0,
  id: 'U13'
})
// control.comp_sink.vdd_cap.cap
const C50 = board.add(C_0603_1608Metric, {
  translate: pt(2.085, 2.947), rotate: 0,
  id: 'C50'
})
// control.off_sw.device.ic
const U14 = board.add(SOT_363_SC_70_6, {
  translate: pt(1.557, 2.684), rotate: 0,
  id: 'U14'
})
// control.off_sw.device.vdd_cap.cap
const C51 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 3.044), rotate: 0,
  id: 'C51'
})
// control.int.r
const R34 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 3.044), rotate: 0,
  id: 'R34'
})
// control.int.c
const C52 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 3.044), rotate: 0,
  id: 'C52'
})
// control.hvclamp.res
const R35 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 3.044), rotate: 0,
  id: 'R35'
})
// control.amp.r1
const R36 = board.add(R_0603_1608Metric, {
  translate: pt(0.682, 3.044), rotate: 0,
  id: 'R36'
})
// control.amp.r2
const R37 = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 3.044), rotate: 0,
  id: 'R37'
})
// control.driver.clamp1
const D10 = board.add(D_SOD_323, {
  translate: pt(1.434, 2.839), rotate: 0,
  id: 'D10'
})
// control.driver.clamp2
const D11 = board.add(D_SOD_323, {
  translate: pt(1.600, 2.839), rotate: 0,
  id: 'D11'
})
// control.driver.high_fet
const Q7 = board.add(TO_220_3_Horizontal_TabUp, {
  translate: pt(0.107, 2.540), rotate: 0,
  id: 'Q7'
})
// control.driver.low_fet
const Q8 = board.add(TO_220_3_Horizontal_TabUp, {
  translate: pt(0.559, 2.540), rotate: 0,
  id: 'Q8'
})
// control.driver.res.res[0]
const R38 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 3.044), rotate: 0,
  id: 'R38'
})
// control.driver.res.res[1]
const R39 = board.add(R_0603_1608Metric, {
  translate: pt(1.150, 3.044), rotate: 0,
  id: 'R39'
})
// control.driver.res.res[2]
const R40 = board.add(R_0603_1608Metric, {
  translate: pt(1.306, 3.044), rotate: 0,
  id: 'R40'
})
// control.driver.high_gate.device.ic
const U15 = board.add(SOT_23_6, {
  translate: pt(1.617, 2.445), rotate: 0,
  id: 'U15'
})
// control.driver.high_gate.device.vdd_cap.cap
const C53 = board.add(C_0805_2012Metric, {
  translate: pt(1.946, 2.667), rotate: 0,
  id: 'C53'
})
// control.driver.low_gate.device.ic
const U16 = board.add(SOT_23_6, {
  translate: pt(1.818, 2.445), rotate: 0,
  id: 'U16'
})
// control.driver.low_gate.device.vdd_cap.cap
const C54 = board.add(C_0805_2012Metric, {
  translate: pt(2.119, 2.667), rotate: 0,
  id: 'C54'
})
// control.driver.high_res
const R41 = board.add(R_0603_1608Metric, {
  translate: pt(1.461, 3.044), rotate: 0,
  id: 'R41'
})
// control.driver.low_res
const R42 = board.add(R_0603_1608Metric, {
  translate: pt(1.617, 3.044), rotate: 0,
  id: 'R42'
})
// control.driver.cap_in1.cap
const C55 = board.add(CP_Elec_6_3x7_7, {
  translate: pt(1.531, 1.904), rotate: 0,
  id: 'C55'
})
// control.driver.cap_in2.cap
const C56 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 2.841), rotate: 0,
  id: 'C56'
})
// control.driver.cap_in3.cap
const C57 = board.add(C_0603_1608Metric, {
  translate: pt(1.773, 3.044), rotate: 0,
  id: 'C57'
})
// control.vdiv.div.top_res
const R43 = board.add(R_0603_1608Metric, {
  translate: pt(1.929, 3.044), rotate: 0,
  id: 'R43'
})
// control.vdiv.div.bottom_res
const R44 = board.add(R_0603_1608Metric, {
  translate: pt(2.085, 3.044), rotate: 0,
  id: 'R44'
})
// control.cdiv.cap
const C58 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 3.141), rotate: 0,
  id: 'C58'
})
// control.isense.ranges[0].isense.res.res
const R45 = board.add(R_1206_3216Metric, {
  translate: pt(1.750, 2.673), rotate: 0,
  id: 'R45'
})
// control.isense.ranges[0].sense_sw.device.ic
const U17 = board.add(SOT_23_6, {
  translate: pt(2.019, 2.445), rotate: 0,
  id: 'U17'
})
// control.isense.ranges[0].sense_sw.device.vdd_cap.cap
const C59 = board.add(C_0805_2012Metric, {
  translate: pt(0.240, 2.841), rotate: 0,
  id: 'C59'
})
// control.isense.ranges[0].pwr_sw.ic
const U18 = board.add(SMDIP_6_W7_62mm, {
  translate: pt(1.106, 1.926), rotate: 0,
  id: 'U18'
})
// control.isense.ranges[0].pwr_sw.res
const R46 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 3.141), rotate: 0,
  id: 'R46'
})
// control.isense.ranges[1].isense.res.res
const R47 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 3.141), rotate: 0,
  id: 'R47'
})
// control.isense.ranges[1].sense_sw.device.ic
const U19 = board.add(SOT_23_6, {
  translate: pt(0.081, 2.696), rotate: 0,
  id: 'U19'
})
// control.isense.ranges[1].sense_sw.device.vdd_cap.cap
const C60 = board.add(C_0805_2012Metric, {
  translate: pt(0.413, 2.841), rotate: 0,
  id: 'C60'
})
// control.isense.ranges[1].pwr_sw.ic
const U20 = board.add(SO_4_4_4x3_6mm_P2_54mm, {
  translate: pt(1.409, 2.207), rotate: 0,
  id: 'U20'
})
// control.isense.ranges[1].pwr_sw.res
const R48 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 3.141), rotate: 0,
  id: 'R48'
})
// control.isense.ranges[2].isense.res.res
const R49 = board.add(R_0603_1608Metric, {
  translate: pt(0.682, 3.141), rotate: 0,
  id: 'R49'
})
// control.isense.ranges[2].sense_sw.device.ic
const U21 = board.add(SOT_23_6, {
  translate: pt(0.281, 2.696), rotate: 0,
  id: 'U21'
})
// control.isense.ranges[2].sense_sw.device.vdd_cap.cap
const C61 = board.add(C_0805_2012Metric, {
  translate: pt(0.587, 2.841), rotate: 0,
  id: 'C61'
})
// control.isense.ranges[2].pwr_sw.ic
const U22 = board.add(SO_4_4_4x3_6mm_P2_54mm, {
  translate: pt(1.795, 2.207), rotate: 0,
  id: 'U22'
})
// control.isense.ranges[2].pwr_sw.res
const R50 = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 3.141), rotate: 0,
  id: 'R50'
})
// control.ifilt.rp
const R51 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 3.141), rotate: 0,
  id: 'R51'
})
// control.ifilt.rn
const R52 = board.add(R_0603_1608Metric, {
  translate: pt(1.150, 3.141), rotate: 0,
  id: 'R52'
})
// control.ifilt.c
const C62 = board.add(C_0603_1608Metric, {
  translate: pt(1.306, 3.141), rotate: 0,
  id: 'C62'
})
// control.vmeas.ic
const U23 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.902, 1.870), rotate: 0,
  id: 'U23'
})
// control.vmeas.vdd_cap.cap
const C63 = board.add(C_0805_2012Metric, {
  translate: pt(0.760, 2.841), rotate: 0,
  id: 'C63'
})
// control.vmeas.rg
const R53 = board.add(R_0603_1608Metric, {
  translate: pt(1.461, 3.141), rotate: 0,
  id: 'R53'
})
// control.imeas.ic
const U24 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.051, 2.233), rotate: 0,
  id: 'U24'
})
// control.imeas.vdd_cap.cap
const C64 = board.add(C_0805_2012Metric, {
  translate: pt(0.933, 2.841), rotate: 0,
  id: 'C64'
})
// control.imeas.rg
const R54 = board.add(R_0603_1608Metric, {
  translate: pt(1.617, 3.141), rotate: 0,
  id: 'R54'
})
// control.vclamp.Q1
const Q9 = board.add(SOT_23, {
  translate: pt(0.477, 2.696), rotate: 0,
  id: 'Q9'
})
// control.vclamp.r
const R55 = board.add(R_0603_1608Metric, {
  translate: pt(1.773, 3.141), rotate: 0,
  id: 'R55'
})
// control.vclamp.Q2
const Q10 = board.add(SOT_23, {
  translate: pt(0.668, 2.696), rotate: 0,
  id: 'Q10'
})
// control.snub_r.res
const R56 = board.add(R_0603_1608Metric, {
  translate: pt(1.929, 3.141), rotate: 0,
  id: 'R56'
})
// control.snub_c.cap
const C65 = board.add(C_0603_1608Metric, {
  translate: pt(2.085, 3.141), rotate: 0,
  id: 'C65'
})
// control.iclamp.Q1
const Q11 = board.add(SOT_23, {
  translate: pt(0.858, 2.696), rotate: 0,
  id: 'Q11'
})
// control.iclamp.r
const R57 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 3.238), rotate: 0,
  id: 'R57'
})
// control.iclamp.Q2
const Q12 = board.add(SOT_23, {
  translate: pt(1.049, 2.696), rotate: 0,
  id: 'Q12'
})
// control.Q1
const Q13 = board.add(D_SMA, {
  translate: pt(1.044, 2.447), rotate: 0,
  id: 'Q13'
})
// control.Q2
const Q14 = board.add(D_SMA, {
  translate: pt(1.359, 2.447), rotate: 0,
  id: 'Q14'
})
// tp_err.conn
const J2 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(1.415, 4.552), rotate: 0,
  id: 'J2'
})
// tp_int.conn
const J3 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(1.702, 4.552), rotate: 0,
  id: 'J3'
})
// pd.ic
const U25 = board.add(WQFN_14_1EP_2_5x2_5mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(5.425, 4.068), rotate: 0,
  id: 'U25'
})
// pd.vdd_cap[0].cap
const C66 = board.add(C_0603_1608Metric, {
  translate: pt(5.584, 4.209), rotate: 0,
  id: 'C66'
})
// pd.vdd_cap[1].cap
const C67 = board.add(C_0805_2012Metric, {
  translate: pt(5.419, 4.219), rotate: 0,
  id: 'C67'
})
// mcu.ic
const U26 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(3.504, 0.530), rotate: 0,
  id: 'U26'
})
// mcu.vcc_cap0.cap
const C68 = board.add(C_1206_3216Metric, {
  translate: pt(4.579, 0.242), rotate: 0,
  id: 'C68'
})
// mcu.vcc_cap1.cap
const C69 = board.add(C_0603_1608Metric, {
  translate: pt(4.767, 0.226), rotate: 0,
  id: 'C69'
})
// mcu.prog.conn
const J4 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(4.626, 0.079), rotate: 0,
  id: 'J4'
})
// mcu.en_pull.rc.r
const R58 = board.add(R_0603_1608Metric, {
  translate: pt(4.546, 0.356), rotate: 0,
  id: 'R58'
})
// mcu.en_pull.rc.c
const C70 = board.add(C_0603_1608Metric, {
  translate: pt(4.702, 0.356), rotate: 0,
  id: 'C70'
})
// led.package
const D12 = board.add(LED_0603_1608Metric, {
  translate: pt(4.805, 4.482), rotate: 0,
  id: 'D12'
})
// led.res
const R59 = board.add(R_0603_1608Metric, {
  translate: pt(4.804, 4.580), rotate: 0,
  id: 'R59'
})
// usb_esd
const U27 = board.add(SOT_23, {
  translate: pt(6.630, 4.857), rotate: 0,
  id: 'U27'
})
// i2c_tp.tp_scl.tp
const TP10 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.567, 4.491), rotate: 0,
  id: 'TP10'
})
// i2c_tp.tp_sda.tp
const TP11 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.567, 4.605), rotate: 0,
  id: 'TP11'
})
// i2c_pull.scl_res.res
const R60 = board.add(R_0603_1608Metric, {
  translate: pt(5.508, 4.482), rotate: 0,
  id: 'R60'
})
// i2c_pull.sda_res.res
const R61 = board.add(R_0603_1608Metric, {
  translate: pt(5.508, 4.579), rotate: 0,
  id: 'R61'
})
// oled.device.conn.conn
const J5 = board.add(TE_2_1734839_4_1x24_1MP_P0_5mm_Horizontal, {
  translate: pt(0.363, 1.552), rotate: 0,
  id: 'J5'
})
// oled.lcd
const U28 = board.add(Lcd_Er_Oled022_1_Outline, {
  translate: pt(1.220, 0.607), rotate: 0,
  id: 'U28'
})
// oled.iref_res
const R62 = board.add(R_0603_1608Metric, {
  translate: pt(1.391, 1.413), rotate: 0,
  id: 'R62'
})
// oled.vcomh_cap.cap
const C71 = board.add(C_1206_3216Metric, {
  translate: pt(0.856, 1.430), rotate: 0,
  id: 'C71'
})
// oled.vdd_cap1.cap
const C72 = board.add(C_0603_1608Metric, {
  translate: pt(1.546, 1.413), rotate: 0,
  id: 'C72'
})
// oled.vdd_cap2.cap
const C73 = board.add(C_0805_2012Metric, {
  translate: pt(1.053, 1.423), rotate: 0,
  id: 'C73'
})
// oled.vcc_cap1.cap
const C74 = board.add(C_0603_1608Metric, {
  translate: pt(1.702, 1.413), rotate: 0,
  id: 'C74'
})
// oled.vcc_cap2.cap
const C75 = board.add(C_0805_2012Metric, {
  translate: pt(1.226, 1.423), rotate: 0,
  id: 'C75'
})
// oled_rc.rc.r
const R63 = board.add(R_0603_1608Metric, {
  translate: pt(5.743, 4.482), rotate: 0,
  id: 'R63'
})
// oled_rc.rc.c
const C76 = board.add(C_0603_1608Metric, {
  translate: pt(5.743, 4.579), rotate: 0,
  id: 'C76'
})
// ioe_ctl.ic
const U29 = board.add(TSSOP_16_4_4x5mm_P0_65mm, {
  translate: pt(1.712, 4.103), rotate: 0,
  id: 'U29'
})
// ioe_ctl.vdd_cap.cap
const C77 = board.add(C_0603_1608Metric, {
  translate: pt(1.619, 4.280), rotate: 0,
  id: 'C77'
})
// ramp_pull.res
const R64 = board.add(R_0603_1608Metric, {
  translate: pt(4.970, 4.819), rotate: 0,
  id: 'R64'
})
// buck_rc.rc.r
const R65 = board.add(R_0603_1608Metric, {
  translate: pt(5.978, 4.482), rotate: 0,
  id: 'R65'
})
// buck_rc.rc.c
const C78 = board.add(C_0603_1608Metric, {
  translate: pt(5.978, 4.579), rotate: 0,
  id: 'C78'
})
// boost_rc.rc.r
const R66 = board.add(R_0603_1608Metric, {
  translate: pt(6.212, 4.482), rotate: 0,
  id: 'R66'
})
// boost_rc.rc.c
const C79 = board.add(C_0603_1608Metric, {
  translate: pt(6.212, 4.579), rotate: 0,
  id: 'C79'
})
// conv_ovp.comp.ic
const U30 = board.add(SOT_353_SC_70_5, {
  translate: pt(4.119, 4.050), rotate: 0,
  id: 'U30'
})
// conv_ovp.comp.vdd_cap.cap
const C80 = board.add(C_0603_1608Metric, {
  translate: pt(4.280, 4.024), rotate: 0,
  id: 'C80'
})
// conv_ovp.ref_div.div.top_res
const R67 = board.add(R_0603_1608Metric, {
  translate: pt(4.115, 4.173), rotate: 0,
  id: 'R67'
})
// conv_ovp.ref_div.div.bottom_res
const R68 = board.add(R_0603_1608Metric, {
  translate: pt(4.270, 4.173), rotate: 0,
  id: 'R68'
})
// conv_ovp.comp_div.div.top_res
const R69 = board.add(R_0603_1608Metric, {
  translate: pt(4.115, 4.270), rotate: 0,
  id: 'R69'
})
// conv_ovp.comp_div.div.bottom_res
const R70 = board.add(R_0603_1608Metric, {
  translate: pt(4.270, 4.270), rotate: 0,
  id: 'R70'
})
// conv_latch.ic.ic
const U31 = board.add(VSSOP_8_2_3x2mm_P0_5mm, {
  translate: pt(3.294, 4.503), rotate: 0,
  id: 'U31'
})
// conv_latch.ic.vdd_cap.cap
const C81 = board.add(C_0603_1608Metric, {
  translate: pt(3.264, 4.620), rotate: 0,
  id: 'C81'
})
// conv_en_pull.res
const R71 = board.add(R_0603_1608Metric, {
  translate: pt(5.205, 4.819), rotate: 0,
  id: 'R71'
})
// comp_pull.res
const R72 = board.add(R_0603_1608Metric, {
  translate: pt(5.440, 4.819), rotate: 0,
  id: 'R72'
})
// pass_temp.ic
const U32 = board.add(SOT_563, {
  translate: pt(3.804, 4.497), rotate: 0,
  id: 'U32'
})
// pass_temp.vdd_cap.cap
const C82 = board.add(C_0603_1608Metric, {
  translate: pt(3.809, 4.608), rotate: 0,
  id: 'C82'
})
// conv_temp.ic
const U33 = board.add(SOT_563, {
  translate: pt(4.039, 4.497), rotate: 0,
  id: 'U33'
})
// conv_temp.vdd_cap.cap
const C83 = board.add(C_0603_1608Metric, {
  translate: pt(4.044, 4.608), rotate: 0,
  id: 'C83'
})
// conv_sense.div.top_res
const R73 = board.add(R_0603_1608Metric, {
  translate: pt(6.447, 4.482), rotate: 0,
  id: 'R73'
})
// conv_sense.div.bottom_res
const R74 = board.add(R_0603_1608Metric, {
  translate: pt(6.447, 4.579), rotate: 0,
  id: 'R74'
})
// ioe_ui.ic
const U34 = board.add(TSSOP_16_4_4x5mm_P0_65mm, {
  translate: pt(2.133, 4.103), rotate: 0,
  id: 'U34'
})
// ioe_ui.vdd_cap.cap
const C84 = board.add(C_0603_1608Metric, {
  translate: pt(2.040, 4.280), rotate: 0,
  id: 'C84'
})
// enc.package
const SW1 = board.add(RotaryEncoder_Bourns_PEC11S, {
  translate: pt(4.339, 2.109), rotate: 0,
  id: 'SW1'
})
// dir.package
const SW2 = board.add(DirectionSwitch_Alps_SKRH, {
  translate: pt(3.260, 3.599), rotate: 0,
  id: 'SW2'
})
// qwiic_pull.scl_res.res
const R75 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 4.819), rotate: 0,
  id: 'R75'
})
// qwiic_pull.sda_res.res
const R76 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 4.915), rotate: 0,
  id: 'R76'
})
// qwiic.conn
const J6 = board.add(JST_SH_SM04B_SRSS_TB_1x04_1MP_P1_00mm_Horizontal, {
  translate: pt(5.914, 4.124), rotate: 0,
  id: 'J6'
})
// dutio.conn
const J7 = board.add(PinHeader_1x03_P2_54mm_Horizontal, {
  translate: pt(0.071, 4.265), rotate: 0,
  id: 'J7'
})
// dut0_clamp.res
const R77 = board.add(R_0603_1608Metric, {
  translate: pt(5.674, 4.819), rotate: 0,
  id: 'R77'
})
// dut1_clamp.res
const R78 = board.add(R_0603_1608Metric, {
  translate: pt(5.909, 4.819), rotate: 0,
  id: 'R78'
})
// touch_duck
const U35 = board.add(Symbol_DucklingSolid, {
  translate: pt(0.157, 5.062), rotate: 0,
  id: 'U35'
})
// rgbs.led[0]
const D13 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.950, 4.493), rotate: 0,
  id: 'D13'
})
// rgbs.led[1]
const D14 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.068, 4.493), rotate: 0,
  id: 'D14'
})
// rgbs.led[2]
const D15 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.186, 4.493), rotate: 0,
  id: 'D15'
})
// rgbs.led[3]
const D16 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.950, 4.611), rotate: 0,
  id: 'D16'
})
// rgbs.led[4]
const D17 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.068, 4.611), rotate: 0,
  id: 'D17'
})
// rgbs.led[5]
const D18 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.186, 4.611), rotate: 0,
  id: 'D18'
})
// rgb_shift.ic
const U36 = board.add(SOT_23_5, {
  translate: pt(6.535, 4.062), rotate: 0,
  id: 'U36'
})
// rgb_shift.vdd_cap.cap
const C85 = board.add(C_0603_1608Metric, {
  translate: pt(6.513, 4.197), rotate: 0,
  id: 'C85'
})
// fan_cap.cap
const C86 = board.add(C_0603_1608Metric, {
  translate: pt(6.144, 4.819), rotate: 0,
  id: 'C86'
})
// fan_drv.pre
const Q15 = board.add(SOT_23, {
  translate: pt(3.707, 4.062), rotate: 0,
  id: 'Q15'
})
// fan_drv.pull
const R79 = board.add(R_0603_1608Metric, {
  translate: pt(3.880, 4.197), rotate: 0,
  id: 'R79'
})
// fan_drv.drv
const Q16 = board.add(SOT_23, {
  translate: pt(3.707, 4.235), rotate: 0,
  id: 'Q16'
})
// fan.conn
const J8 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.652, 4.583), rotate: 0,
  id: 'J8'
})
// spk_drv.ic
const U37 = board.add(QFN_16_1EP_3x3mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(4.540, 4.079), rotate: 0,
  id: 'U37'
})
// spk_drv.pwr_cap0.cap
const C87 = board.add(C_0603_1608Metric, {
  translate: pt(4.688, 4.231), rotate: 0,
  id: 'C87'
})
// spk_drv.pwr_cap1.cap
const C88 = board.add(C_0805_2012Metric, {
  translate: pt(4.523, 4.241), rotate: 0,
  id: 'C88'
})
// spk.conn
const J9 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.042, 4.583), rotate: 0,
  id: 'J9'
})
// dac.ic
const U38 = board.add(MSOP_10_3x3mm_P0_5mm, {
  translate: pt(0.730, 4.064), rotate: 0,
  id: 'U38'
})
// dac.vdd_cap[0].cap
const C89 = board.add(C_0603_1608Metric, {
  translate: pt(0.663, 4.201), rotate: 0,
  id: 'C89'
})
// dac.vdd_cap[1].cap
const C90 = board.add(C_0805_2012Metric, {
  translate: pt(0.961, 4.033), rotate: 0,
  id: 'C90'
})
// dac.out_cap[0]
const C91 = board.add(C_0603_1608Metric, {
  translate: pt(0.819, 4.201), rotate: 0,
  id: 'C91'
})
// dac.out_cap[1]
const C92 = board.add(C_0603_1608Metric, {
  translate: pt(0.974, 4.201), rotate: 0,
  id: 'C92'
})
// dac.out_cap[2]
const C93 = board.add(C_0603_1608Metric, {
  translate: pt(0.663, 4.298), rotate: 0,
  id: 'C93'
})
// dac.out_cap[3]
const C94 = board.add(C_0603_1608Metric, {
  translate: pt(0.819, 4.298), rotate: 0,
  id: 'C94'
})
// dac_ferrite.fb
const FB3 = board.add(L_0603_1608Metric, {
  translate: pt(6.378, 4.819), rotate: 0,
  id: 'FB3'
})
// adc.ic
const U39 = board.add(TSSOP_20_4_4x6_5mm_P0_65mm, {
  translate: pt(1.344, 3.522), rotate: 0,
  id: 'U39'
})
// adc.avdd_res.res
const R80 = board.add(R_0603_1608Metric, {
  translate: pt(1.593, 3.530), rotate: 0,
  id: 'R80'
})
// adc.dvdd_res.res
const R81 = board.add(R_0603_1608Metric, {
  translate: pt(1.593, 3.627), rotate: 0,
  id: 'R81'
})
// adc.avdd_cap_0.cap
const C95 = board.add(C_0603_1608Metric, {
  translate: pt(1.250, 3.728), rotate: 0,
  id: 'C95'
})
// adc.avdd_cap_1.cap
const C96 = board.add(C_0603_1608Metric, {
  translate: pt(1.406, 3.728), rotate: 0,
  id: 'C96'
})
// adc.dvdd_cap_0.cap
const C97 = board.add(C_0603_1608Metric, {
  translate: pt(1.562, 3.728), rotate: 0,
  id: 'C97'
})
// adc.dvdd_cap_1.cap
const C98 = board.add(C_0603_1608Metric, {
  translate: pt(1.250, 3.825), rotate: 0,
  id: 'C98'
})
// adc.vref_cap.cap
const C99 = board.add(C_0805_2012Metric, {
  translate: pt(1.602, 3.423), rotate: 0,
  id: 'C99'
})
// tp_vcen.conn
const J10 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(2.423, 4.552), rotate: 0,
  id: 'J10'
})
// vcen_rc.rc.r
const R82 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 4.819), rotate: 0,
  id: 'R82'
})
// vcen_rc.rc.c
const C100 = board.add(C_0603_1608Metric, {
  translate: pt(0.293, 4.915), rotate: 0,
  id: 'C100'
})
// tp_mv.conn
const J11 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(2.710, 4.552), rotate: 0,
  id: 'J11'
})
// mv_rc.rc.r
const R83 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 4.819), rotate: 0,
  id: 'R83'
})
// mv_rc.rc.c
const C101 = board.add(C_0603_1608Metric, {
  translate: pt(0.528, 4.915), rotate: 0,
  id: 'C101'
})
// tp_mi.conn
const J12 = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(2.998, 4.552), rotate: 0,
  id: 'J12'
})
// mi_rc.rc.r
const R84 = board.add(R_0603_1608Metric, {
  translate: pt(0.762, 4.819), rotate: 0,
  id: 'R84'
})
// mi_rc.rc.c
const C102 = board.add(C_0603_1608Metric, {
  translate: pt(0.762, 4.915), rotate: 0,
  id: 'C102'
})
// outn
const J13 = board.add(CalTest_CT3151, {
  translate: pt(6.435, 2.150), rotate: 0,
  id: 'J13'
})
// outp
const J14 = board.add(CalTest_CT3151, {
  translate: pt(0.882, 3.770), rotate: 0,
  id: 'J14'
})
// outd
const J15 = board.add(PinHeader_1x02_P2_54mm_Horizontal, {
  translate: pt(4.291, 4.625), rotate: 0,
  id: 'J15'
})
// vimeas_amps.ic
const U40 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.296, 4.101), rotate: 0,
  id: 'U40'
})
// vimeas_amps.vdd_cap.cap
const C103 = board.add(C_0805_2012Metric, {
  translate: pt(1.218, 4.285), rotate: 0,
  id: 'C103'
})
// cv_amps.ic
const U41 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.548, 4.101), rotate: 0,
  id: 'U41'
})
// cv_amps.vdd_cap.cap
const C104 = board.add(C_0603_1608Metric, {
  translate: pt(2.461, 4.276), rotate: 0,
  id: 'C104'
})
// ci_amps.ic
const U42 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.958, 4.101), rotate: 0,
  id: 'U42'
})
// ci_amps.vdd_cap.cap
const C105 = board.add(C_0603_1608Metric, {
  translate: pt(2.870, 4.276), rotate: 0,
  id: 'C105'
})
// cintref_amps.ic
const U43 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(3.367, 4.101), rotate: 0,
  id: 'U43'
})
// cintref_amps.vdd_cap.cap
const C106 = board.add(C_0603_1608Metric, {
  translate: pt(3.280, 4.276), rotate: 0,
  id: 'C106'
})

board.setNetlist([
  {name: "gnd", pads: [["U27", "3"], ["J2", "2"], ["J3", "2"], ["J10", "2"], ["J11", "2"], ["J12", "2"], ["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["J13", "1"], ["J15", "1"], ["TP1", "1"], ["U1", "3"], ["U1", "7"], ["U1", "8"], ["D1", "2"], ["Q2", "2"], ["C4", "2"], ["U2", "1"], ["U3", "1"], ["D2", "2"], ["U4", "2"], ["U5", "3"], ["U5", "7"], ["D6", "2"], ["U8", "2"], ["U9", "3"], ["U10", "2"], ["U11", "1"], ["U25", "8"], ["U25", "9"], ["U25", "15"], ["U26", "1"], ["U26", "40"], ["U26", "41"], ["U29", "1"], ["U29", "2"], ["U29", "3"], ["U29", "8"], ["R64", "1"], ["R71", "1"], ["U32", "2"], ["U32", "4"], ["U33", "2"], ["U34", "1"], ["U34", "3"], ["U34", "8"], ["SW1", "C"], ["SW1", "S2"], ["SW2", "5"], ["J6", "1"], ["J7", "1"], ["D13", "4"], ["D14", "4"], ["D15", "4"], ["D16", "4"], ["D17", "4"], ["D18", "4"], ["U36", "1"], ["U36", "3"], ["C86", "2"], ["Q15", "2"], ["J8", "1"], ["U37", "3"], ["U37", "11"], ["U37", "15"], ["U37", "17"], ["U38", "10"], ["U39", "2"], ["U39", "3"], ["U39", "19"], ["R18", "2"], ["U41", "4"], ["C40", "2"], ["C76", "2"], ["C78", "2"], ["C79", "2"], ["U31", "4"], ["R74", "2"], ["C100", "2"], ["C101", "2"], ["C102", "2"], ["J1", "S1"], ["Q14", "1"], ["R62", "2"], ["C91", "2"], ["C92", "2"], ["C93", "2"], ["C94", "2"], ["C1", "2"], ["C5", "2"], ["C9", "2"], ["C17", "2"], ["C37", "2"], ["C38", "2"], ["C39", "2"], ["C45", "2"], ["U12", "2"], ["U13", "2"], ["U23", "1"], ["C65", "2"], ["C58", "2"], ["C66", "2"], ["C67", "2"], ["C68", "2"], ["C69", "2"], ["J4", "5"], ["C71", "2"], ["C72", "2"], ["C73", "2"], ["C74", "2"], ["C75", "2"], ["C77", "2"], ["U30", "2"], ["C82", "2"], ["C83", "2"], ["C84", "2"], ["C85", "2"], ["C87", "2"], ["C88", "2"], ["C89", "2"], ["C90", "2"], ["C95", "2"], ["C96", "2"], ["C97", "2"], ["C98", "2"], ["C99", "2"], ["R5", "2"], ["R8", "2"], ["R11", "2"], ["C104", "2"], ["R21", "2"], ["U43", "4"], ["R44", "2"], ["U14", "2"], ["C70", "2"], ["J5", "22"], ["J5", "24"], ["J5", "1"], ["J5", "23"], ["J5", "13"], ["J5", "14"], ["J5", "9"], ["J5", "8"], ["J5", "7"], ["J5", "6"], ["J5", "5"], ["R68", "2"], ["R70", "2"], ["C81", "2"], ["U15", "4"], ["U16", "4"], ["Q3", "1"], ["Q3", "2"], ["Q3", "3"], ["Q5", "1"], ["Q5", "2"], ["Q5", "3"], ["Q8", "2"], ["C7", "2"], ["C8", "2"], ["C13", "2"], ["C14", "2"], ["C15", "2"], ["U6", "6"], ["U7", "6"], ["C41", "2"], ["C42", "2"], ["C49", "2"], ["C50", "2"], ["C48", "2"], ["U42", "4"], ["C47", "2"], ["C55", "2"], ["C56", "2"], ["C57", "2"], ["C46", "2"], ["J5", "18"], ["J5", "15"], ["J5", "17"], ["C80", "2"], ["C106", "2"], ["C51", "2"], ["C11", "2"], ["C12", "2"], ["C18", "2"], ["C19", "2"], ["C20", "2"], ["C21", "2"], ["C22", "2"], ["C23", "2"], ["C24", "2"], ["C25", "2"], ["C26", "2"], ["C27", "2"], ["C28", "2"], ["C29", "2"], ["C30", "2"], ["C31", "2"], ["C32", "2"], ["C33", "2"], ["C35", "2"], ["C105", "2"], ["R46", "2"], ["R48", "2"], ["R50", "2"], ["U17", "2"], ["U17", "4"], ["U19", "2"], ["U19", "4"], ["U21", "2"], ["U21", "4"], ["C59", "2"], ["C60", "2"], ["C61", "2"]]},
  {name: "vusb", pads: [["U25", "2"], ["C3", "1"], ["Q1", "1"], ["Q1", "2"], ["Q1", "3"], ["U3", "3"], ["R2", "1"], ["R1", "2"], ["U1", "2"], ["R9", "1"], ["C9", "1"], ["C11", "1"], ["C12", "1"]]},
  {name: "vusb_ramp", pads: [["Q1", "5"], ["C2", "1"], ["C4", "1"], ["TP2", "1"], ["U2", "3"], ["R6", "1"], ["C5", "1"], ["C7", "1"], ["R12", "1"], ["U5", "1"]]},
  {name: "v5", pads: [["TP3", "1"], ["U4", "5"], ["U8", "1"], ["U9", "1"], ["U10", "5"], ["D13", "2"], ["D14", "2"], ["D15", "2"], ["D16", "2"], ["D17", "2"], ["D18", "2"], ["U36", "5"], ["C86", "1"], ["R79", "1"], ["Q16", "2"], ["U37", "4"], ["U37", "7"], ["U37", "8"], ["R4", "1"], ["U4", "4"], ["U8", "3"], ["U10", "4"], ["C37", "1"], ["C39", "1"], ["C85", "1"], ["C87", "1"], ["C88", "1"], ["U6", "4"], ["U7", "4"], ["L3", "1"], ["L5", "1"], ["C14", "1"], ["D4", "2"], ["D5", "2"], ["C41", "1"], ["C33", "1"], ["C35", "1"], ["L1", "2"], ["C8", "1"]]},
  {name: "v3v3", pads: [["D2", "1"], ["TP4", "1"], ["U1", "4"], ["U5", "4"], ["U5", "8"], ["U25", "3"], ["U25", "4"], ["U26", "2"], ["D12", "2"], ["U29", "16"], ["R72", "1"], ["U32", "5"], ["U33", "4"], ["U33", "5"], ["U34", "2"], ["U34", "16"], ["J6", "2"], ["R63", "1"], ["U31", "8"], ["R81", "1"], ["R7", "1"], ["C1", "1"], ["C17", "1"], ["C66", "1"], ["C67", "1"], ["C68", "1"], ["C69", "1"], ["J4", "1"], ["R60", "1"], ["R61", "1"], ["C72", "1"], ["C73", "1"], ["C77", "1"], ["U30", "5"], ["C82", "1"], ["C83", "1"], ["C84", "1"], ["R75", "1"], ["R76", "1"], ["R58", "1"], ["J5", "20"], ["R67", "1"], ["C81", "1"], ["J5", "19"], ["C80", "1"], ["L2", "2"], ["C13", "1"]]},
  {name: "v12", pads: [["D3", "1"], ["C16", "1"], ["R10", "1"], ["C15", "1"], ["C74", "1"], ["C75", "1"], ["J5", "2"]]},
  {name: "vconvin", pads: [["R12", "2"], ["U5", "2"], ["Q4", "5"], ["C18", "1"], ["C19", "1"], ["C20", "1"], ["C21", "1"], ["C22", "1"], ["C23", "1"], ["C24", "1"]]},
  {name: "vconv", pads: [["D6", "1"], ["TP5", "1"], ["R73", "1"], ["Q7", "2"], ["C55", "1"], ["C56", "1"], ["C57", "1"], ["R69", "1"], ["Q6", "5"], ["C25", "1"], ["C26", "1"], ["C27", "1"], ["C28", "1"], ["C29", "1"], ["C30", "1"], ["C31", "1"], ["C32", "1"]]},
  {name: "vanalog", pads: [["U8", "5"], ["TP6", "1"], ["FB2", "1"], ["U41", "8"], ["R80", "1"], ["C38", "1"], ["U13", "5"], ["U12", "5"], ["C104", "1"], ["U14", "5"], ["U43", "8"], ["U42", "8"], ["C50", "1"], ["C49", "1"], ["C51", "1"], ["C106", "1"], ["C105", "1"]]},
  {name: "vref", pads: [["U9", "2"], ["TP7", "1"], ["FB3", "1"], ["U39", "4"], ["R17", "1"], ["C99", "1"]]},
  {name: "vcenter", pads: [["J10", "1"], ["U23", "6"], ["U24", "6"], ["R82", "1"], ["U43", "3"], ["R19", "2"], ["C40", "1"], ["R25", "1"], ["R37", "2"]]},
  {name: "vcontrol", pads: [["TP8", "1"], ["D7", "1"], ["C43", "1"], ["R20", "1"], ["C42", "1"], ["U23", "8"], ["U24", "8"], ["U40", "8"], ["C63", "1"], ["C64", "1"], ["C103", "1"], ["U15", "5"], ["U16", "5"], ["U17", "5"], ["U19", "5"], ["U21", "5"], ["C53", "1"], ["C54", "1"], ["C59", "1"], ["C60", "1"], ["C61", "1"]]},
  {name: "vcontroln", pads: [["U11", "2"], ["TP9", "1"], ["U23", "5"], ["U24", "5"], ["U40", "4"], ["C45", "1"], ["C63", "2"], ["C64", "2"], ["C103", "2"], ["U15", "2"], ["U16", "2"], ["C53", "2"], ["C54", "2"]]},
  {name: "usb.pwr", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["F1", "1"]]},
  {name: "fuse_vusb.pwr_out", pads: [["F1", "2"], ["FB1", "1"]]},
  {name: "filt_vusb.pwr_out", pads: [["FB1", "2"], ["D1", "1"], ["R1", "1"], ["U1", "1"]]},
  {name: "ref_div.output", pads: [["U41", "3"], ["R17", "2"], ["R18", "1"]]},
  {name: "ref_buf.output", pads: [["U41", "2"], ["R19", "1"], ["U41", "1"]]},
  {name: "filt_vcontroln.pwr_out", pads: [["U11", "4"], ["U11", "5"], ["FB2", "2"]]},
  {name: "control.int_link", pads: [["J2", "1"], ["R34", "1"], ["U14", "4"]]},
  {name: "control.tp_int", pads: [["U40", "3"], ["J3", "1"], ["U43", "1"], ["C52", "1"]]},
  {name: "usb.cc.cc1", pads: [["J1", "A5"], ["U25", "10"], ["U25", "11"]]},
  {name: "usb.cc.cc2", pads: [["J1", "B5"], ["U25", "1"], ["U25", "14"]]},
  {name: "mcu.program_boot_node", pads: [["R59", "2"], ["U26", "27"], ["J4", "2"]]},
  {name: "usb_chain_0.d_P", pads: [["J1", "A6"], ["J1", "B6"], ["U27", "2"], ["U26", "14"]]},
  {name: "usb_chain_0.d_N", pads: [["J1", "A7"], ["J1", "B7"], ["U27", "1"], ["U26", "13"]]},
  {name: "i2c_pull.i2c.scl", pads: [["U26", "8"], ["U25", "6"], ["U1", "5"], ["U5", "5"], ["U29", "14"], ["U32", "1"], ["U33", "1"], ["U34", "14"], ["U38", "2"], ["R60", "2"], ["TP10", "1"], ["J5", "12"]]},
  {name: "i2c_pull.i2c.sda", pads: [["U26", "7"], ["U25", "7"], ["U1", "6"], ["U5", "6"], ["U29", "15"], ["U32", "6"], ["U33", "6"], ["U34", "15"], ["U38", "3"], ["R61", "2"], ["TP11", "1"], ["J5", "11"], ["J5", "10"]]},
  {name: "pd.int", pads: [["U26", "9"], ["U25", "5"]]},
  {name: "oled.reset", pads: [["J5", "16"], ["R63", "2"], ["C76", "1"]]},
  {name: "control.high_gate_ctl", pads: [["U29", "11"], ["U15", "3"]]},
  {name: "control.low_gate_ctl", pads: [["U29", "12"], ["U16", "3"]]},
  {name: "ioe_ctl.io.off_0", pads: [["U29", "9"], ["U14", "6"]]},
  {name: "ramp_pull.io", pads: [["U29", "4"], ["R64", "2"], ["Q2", "1"]]},
  {name: "buck_rc.input", pads: [["U26", "10"], ["R65", "1"]]},
  {name: "buck_rc.output", pads: [["U6", "2"], ["R65", "2"], ["C78", "1"]]},
  {name: "boost_rc.input", pads: [["U26", "11"], ["R66", "1"]]},
  {name: "boost_rc.output", pads: [["U7", "2"], ["R66", "2"], ["C79", "1"]]},
  {name: "conv_en_pull.io", pads: [["U29", "6"], ["U31", "5"], ["R71", "2"]]},
  {name: "conv_ovp.output", pads: [["U30", "4"], ["U31", "1"], ["R72", "2"]]},
  {name: "conv_latch.out", pads: [["U29", "7"], ["U31", "7"], ["U31", "6"], ["U6", "3"], ["U7", "3"]]},
  {name: "conv_sense.output", pads: [["U26", "12"], ["R73", "2"], ["R74", "1"]]},
  {name: "enc.a", pads: [["U26", "35"], ["SW1", "A"]]},
  {name: "enc.b", pads: [["U26", "34"], ["SW1", "B"]]},
  {name: "enc.sw", pads: [["U26", "33"], ["SW1", "S1"]]},
  {name: "dir.a", pads: [["U34", "4"], ["SW2", "1"]]},
  {name: "dir.b", pads: [["U34", "12"], ["SW2", "4"]]},
  {name: "dir.c", pads: [["U34", "6"], ["SW2", "3"]]},
  {name: "dir.d", pads: [["U34", "7"], ["SW2", "6"]]},
  {name: "dir.center", pads: [["U34", "5"], ["SW2", "2"]]},
  {name: "ioe_ui.io.irange_0", pads: [["U34", "11"], ["U17", "3"], ["U18", "1"]]},
  {name: "ioe_ui.io.irange_1", pads: [["U34", "9"], ["U19", "3"], ["U20", "1"]]},
  {name: "ioe_ui.io.irange_2", pads: [["U34", "10"], ["U21", "3"], ["U22", "1"]]},
  {name: "qwiic_pull.i2c.scl", pads: [["U26", "39"], ["R75", "2"], ["J6", "4"]]},
  {name: "qwiic_pull.i2c.sda", pads: [["U26", "38"], ["J6", "3"], ["R76", "2"]]},
  {name: "dutio.io0", pads: [["J7", "2"], ["R77", "1"]]},
  {name: "dut0_clamp.signal_out", pads: [["U26", "24"], ["R77", "2"]]},
  {name: "dutio.io1", pads: [["J7", "3"], ["R78", "1"]]},
  {name: "dut1_clamp.signal_out", pads: [["U26", "25"], ["R78", "2"]]},
  {name: "touch_duck.pad", pads: [["U26", "21"], ["U35", "1"]]},
  {name: "rgb_shift.input", pads: [["U26", "31"], ["U36", "2"]]},
  {name: "rgb_shift.output", pads: [["U36", "4"], ["D13", "1"]]},
  {name: "fan_drv.control", pads: [["U26", "32"], ["Q15", "1"]]},
  {name: "fan.pwr", pads: [["J8", "2"], ["Q16", "3"]]},
  {name: "spk_drv.i2s.sck", pads: [["U26", "5"], ["U37", "16"]]},
  {name: "spk_drv.i2s.ws", pads: [["U26", "6"], ["U37", "14"]]},
  {name: "spk_drv.i2s.sd", pads: [["U26", "4"], ["U37", "1"]]},
  {name: "spk_drv.out.a", pads: [["U37", "9"], ["J9", "1"]]},
  {name: "spk_drv.out.b", pads: [["U37", "10"], ["J9", "2"]]},
  {name: "dac_ferrite.pwr_out", pads: [["FB3", "2"], ["U38", "1"], ["U38", "4"], ["C89", "1"], ["C90", "1"]]},
  {name: "dac.out0", pads: [["U38", "6"], ["R26", "1"], ["C91", "1"]]},
  {name: "dac.out2", pads: [["U38", "8"], ["R29", "1"], ["C93", "1"]]},
  {name: "dac.out1", pads: [["U38", "7"], ["R32", "1"], ["C92", "1"]]},
  {name: "dac.out3", pads: [["U38", "9"], ["R30", "1"], ["C94", "1"]]},
  {name: "adc.spi.sck", pads: [["U39", "14"], ["U26", "17"]]},
  {name: "adc.spi.mosi", pads: [["U39", "15"], ["U26", "18"]]},
  {name: "adc.spi.miso", pads: [["U39", "16"], ["U26", "19"]]},
  {name: "adc.cs", pads: [["U39", "13"], ["U26", "15"]]},
  {name: "adc.mclkin", pads: [["U39", "18"], ["U26", "20"]]},
  {name: "vcen_rc.output", pads: [["U39", "7"], ["R82", "2"], ["C100", "1"]]},
  {name: "control.meas_v", pads: [["J11", "1"], ["R83", "1"], ["Q10", "2"], ["R27", "1"]]},
  {name: "mv_rc.output", pads: [["U39", "5"], ["R83", "2"], ["C101", "1"]]},
  {name: "control.meas_i", pads: [["J12", "1"], ["R84", "1"], ["Q12", "2"], ["R31", "1"], ["R33", "1"]]},
  {name: "mi_rc.output", pads: [["U39", "6"], ["R84", "2"], ["C102", "1"]]},
  {name: "control.limit_source", pads: [["U12", "4"], ["U26", "22"]]},
  {name: "control.limit_sink", pads: [["U13", "4"], ["U26", "23"]]},
  {name: "outp.port", pads: [["J14", "1"], ["J15", "2"], ["Q13", "1"], ["R56", "1"], ["R35", "1"], ["U18", "6"], ["U20", "4"], ["U22", "4"]]},
  {name: "vimeas_amps.inn.0", pads: [["U40", "2"], ["R36", "2"], ["R37", "1"]]},
  {name: "control.drive", pads: [["U40", "1"], ["R36", "1"], ["R23", "1"], ["R38", "1"]]},
  {name: "vimeas_amps.inp.1", pads: [["U40", "5"], ["R35", "2"]]},
  {name: "control.outa", pads: [["U40", "6"], ["U40", "7"], ["R22", "1"], ["R43", "1"]]},
  {name: "cv_amps.inp.1", pads: [["U41", "5"], ["R26", "2"], ["R27", "2"], ["R29", "2"], ["C46", "1"]]},
  {name: "cv_amps.inn.1", pads: [["U41", "6"], ["R28", "2"], ["U12", "3"], ["U13", "1"], ["U14", "3"], ["U42", "6"], ["U42", "2"], ["D8", "1"], ["D9", "2"]]},
  {name: "cv_amps.out.1", pads: [["U41", "7"], ["R28", "1"]]},
  {name: "ci_amps.inp.0", pads: [["U42", "3"], ["R32", "2"], ["R33", "2"], ["C48", "1"]]},
  {name: "ci_amps.out.0", pads: [["U42", "1"], ["D9", "1"], ["U13", "3"]]},
  {name: "ci_amps.inp.1", pads: [["U42", "5"], ["R30", "2"], ["R31", "2"], ["C47", "1"]]},
  {name: "ci_amps.out.1", pads: [["U42", "7"], ["D8", "2"], ["U12", "1"]]},
  {name: "cintref_amps.inn.0", pads: [["U43", "2"], ["R34", "2"], ["C52", "2"]]},
  {name: "cintref_amps.inp.1", pads: [["U43", "5"], ["R23", "2"], ["R25", "2"]]},
  {name: "cintref_amps.inn.1", pads: [["U43", "6"], ["R22", "2"], ["R24", "2"]]},
  {name: "cintref_amps.out.1", pads: [["U43", "7"], ["R24", "1"], ["U14", "1"]]},
  {name: "ramp.ctl_fet.drain", pads: [["Q2", "3"], ["R3", "2"]]},
  {name: "ramp.div.center", pads: [["C3", "2"], ["Q1", "4"], ["C2", "2"], ["R2", "2"], ["R3", "1"]]},
  {name: "reg_v5.fb.output", pads: [["U2", "4"], ["R4", "2"], ["R5", "1"]]},
  {name: "reg_v5.boot_cap.neg", pads: [["C6", "2"], ["U2", "2"], ["L1", "1"]]},
  {name: "reg_v5.boot_cap.pos", pads: [["C6", "1"], ["U2", "6"]]},
  {name: "reg_v5.en_res.b", pads: [["R6", "2"], ["U2", "5"]]},
  {name: "reg_3v3.fb.output", pads: [["U3", "4"], ["R7", "2"], ["R8", "1"]]},
  {name: "reg_3v3.boot_cap.neg", pads: [["C10", "2"], ["U3", "2"], ["L2", "1"]]},
  {name: "reg_3v3.boot_cap.pos", pads: [["C10", "1"], ["U3", "6"]]},
  {name: "reg_3v3.en_res.b", pads: [["R9", "2"], ["U3", "5"]]},
  {name: "reg_v12.fb.output", pads: [["U4", "3"], ["C16", "2"], ["R10", "2"], ["R11", "1"]]},
  {name: "reg_v12.power_path.switch", pads: [["U4", "1"], ["L3", "2"], ["D3", "2"]]},
  {name: "conv.l1", pads: [["L4", "1"], ["Q3", "5"], ["Q4", "1"], ["Q4", "2"], ["Q4", "3"], ["U6", "7"], ["C34", "2"]]},
  {name: "conv.l2", pads: [["L4", "2"], ["Q5", "5"], ["Q6", "1"], ["Q6", "2"], ["Q6", "3"], ["U7", "7"], ["C36", "2"]]},
  {name: "conv.buck_sw.low_gate_res.a", pads: [["R13", "1"], ["U6", "5"]]},
  {name: "conv.buck_sw.low_gate_res.b", pads: [["R13", "2"], ["Q3", "4"]]},
  {name: "conv.buck_sw.high_gate_res.a", pads: [["R14", "1"], ["U6", "8"]]},
  {name: "conv.buck_sw.high_gate_res.b", pads: [["R14", "2"], ["Q4", "4"]]},
  {name: "conv.buck_sw.driver.ic.bst", pads: [["U6", "1"], ["D4", "1"], ["C34", "1"]]},
  {name: "conv.boost_sw.low_gate_res.a", pads: [["R15", "1"], ["U7", "5"]]},
  {name: "conv.boost_sw.low_gate_res.b", pads: [["R15", "2"], ["Q5", "4"]]},
  {name: "conv.boost_sw.high_gate_res.a", pads: [["R16", "1"], ["U7", "8"]]},
  {name: "conv.boost_sw.high_gate_res.b", pads: [["R16", "2"], ["Q6", "4"]]},
  {name: "conv.boost_sw.driver.ic.bst", pads: [["U7", "1"], ["D5", "1"], ["C36", "1"]]},
  {name: "reg_vcontrol.fb.output", pads: [["U10", "3"], ["C43", "2"], ["R20", "2"], ["R21", "1"]]},
  {name: "reg_vcontrol.power_path.switch", pads: [["U10", "1"], ["L5", "2"], ["D7", "2"]]},
  {name: "reg_vcontroln.cf.neg", pads: [["C44", "2"], ["U11", "3"]]},
  {name: "reg_vcontroln.cf.pos", pads: [["C44", "1"], ["U11", "6"]]},
  {name: "control.driver.out", pads: [["R41", "2"], ["Q7", "3"], ["D11", "2"], ["Q8", "3"], ["R42", "2"], ["R45", "1"], ["R47", "1"], ["R49", "1"], ["R51", "1"]]},
  {name: "control.vdiv.output", pads: [["U23", "4"], ["C58", "1"], ["R43", "2"], ["R44", "1"]]},
  {name: "control.isense.sense_out", pads: [["R52", "1"], ["U17", "6"], ["U19", "6"], ["U21", "6"]]},
  {name: "control.ifilt.outp", pads: [["U24", "4"], ["R51", "2"], ["C62", "1"]]},
  {name: "control.ifilt.outn", pads: [["U24", "1"], ["R52", "2"], ["C62", "2"]]},
  {name: "control.vmeas.output", pads: [["U23", "7"], ["Q9", "2"]]},
  {name: "control.imeas.output", pads: [["U24", "7"], ["Q11", "2"]]},
  {name: "control.snub_r.pwr_out", pads: [["R56", "2"], ["C65", "1"]]},
  {name: "control.Q1.ports.2", pads: [["Q13", "2"], ["Q14", "2"]]},
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
  {name: "control.vclamp.r.a", pads: [["Q9", "1"], ["R55", "1"], ["Q10", "3"]]},
  {name: "control.vclamp.r.b", pads: [["Q9", "3"], ["R55", "2"], ["Q10", "1"]]},
  {name: "control.iclamp.r.a", pads: [["Q11", "1"], ["R57", "1"], ["Q12", "3"]]},
  {name: "control.iclamp.r.b", pads: [["Q11", "3"], ["R57", "2"], ["Q12", "1"]]},
  {name: "pd.ic.vconn", pads: [["U25", "12"], ["U25", "13"]]},
  {name: "mcu.program_uart_node.a_tx", pads: [["U26", "37"], ["J4", "3"]]},
  {name: "mcu.program_uart_node.b_tx", pads: [["U26", "36"], ["J4", "4"]]},
  {name: "mcu.program_en_node", pads: [["U26", "3"], ["J4", "6"], ["R58", "2"], ["C70", "1"]]},
  {name: "led.res.a", pads: [["R59", "1"], ["D12", "1"]]},
  {name: "oled.iref_res.a", pads: [["R62", "1"], ["J5", "4"]]},
  {name: "oled.device.vcomh", pads: [["J5", "3"], ["C71", "1"]]},
  {name: "conv_ovp.comp.inp", pads: [["U30", "1"], ["R69", "2"], ["R70", "1"]]},
  {name: "conv_ovp.comp.inn", pads: [["U30", "3"], ["R67", "2"], ["R68", "1"]]},
  {name: "conv_latch.ic.out2", pads: [["U31", "3"], ["U31", "2"]]},
  {name: "pass_temp.alert", pads: [["U32", "3"]]},
  {name: "conv_temp.alert", pads: [["U33", "3"]]},
  {name: "rgbs.led[0].dout", pads: [["D13", "3"], ["D14", "1"]]},
  {name: "rgbs.led[1].dout", pads: [["D14", "3"], ["D15", "1"]]},
  {name: "rgbs.led[2].dout", pads: [["D15", "3"], ["D16", "1"]]},
  {name: "rgbs.led[3].dout", pads: [["D16", "3"], ["D17", "1"]]},
  {name: "rgbs.led[4].dout", pads: [["D17", "3"], ["D18", "1"]]},
  {name: "rgbs.dout", pads: [["D18", "3"]]},
  {name: "fan_drv.pre.drain", pads: [["Q15", "3"], ["R79", "2"], ["Q16", "1"]]},
  {name: "dac.rdy", pads: [["U38", "5"]]},
  {name: "adc.vins.3", pads: [["U39", "8"]]},
  {name: "adc.vins.4", pads: [["U39", "9"]]},
  {name: "adc.vins.5", pads: [["U39", "10"]]},
  {name: "adc.vins.6", pads: [["U39", "11"]]},
  {name: "adc.vins.7", pads: [["U39", "12"]]},
  {name: "adc.ic.avdd", pads: [["U39", "1"], ["R80", "2"], ["C95", "1"], ["C96", "1"]]},
  {name: "adc.ic.dvdd", pads: [["U39", "20"], ["R81", "2"], ["C97", "1"], ["C98", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(6.745669291338583, 5.219685039370078);
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


