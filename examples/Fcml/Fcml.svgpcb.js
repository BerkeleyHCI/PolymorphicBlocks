const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.599, 2.702), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.638, 2.702), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.599, 2.742), rotate: 0,
  id: 'H3'
})
// usb_mcu.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.774, 1.501), rotate: 0,
  id: 'J1'
})
// usb_mcu.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(1.623, 1.756), rotate: 0,
  id: 'R1'
})
// usb_mcu.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(1.779, 1.756), rotate: 0,
  id: 'R2'
})
// usb_fpga.conn
const J2 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.237, 1.501), rotate: 0,
  id: 'J2'
})
// usb_fpga.cc_pull.cc1.res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(1.086, 1.756), rotate: 0,
  id: 'R3'
})
// usb_fpga.cc_pull.cc2.res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(1.242, 1.756), rotate: 0,
  id: 'R4'
})
// conv_in.conn
const J3 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.596, 2.365), rotate: 0,
  id: 'J3'
})
// tp_vusb.tp
const TP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.780, 2.740), rotate: 0,
  id: 'TP1'
})
// tp_gnd.tp
const TP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.533, 2.740), rotate: 0,
  id: 'TP2'
})
// reg_3v3.ic
const U1 = board.add(SOT_223_3_TabPin2, {
  translate: pt(2.275, 1.478), rotate: 0,
  id: 'U1'
})
// reg_3v3.in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(2.333, 1.688), rotate: 0,
  id: 'C1'
})
// reg_3v3.out_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(2.169, 1.698), rotate: 0,
  id: 'C2'
})
// tp_3v3.tp
const TP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.033, 2.740), rotate: 0,
  id: 'TP3'
})
// prot_3v3.diode
const D1 = board.add(D_SOD_323, {
  translate: pt(0.533, 2.740), rotate: 0,
  id: 'D1'
})
// reg_vgate.ic
const U2 = board.add(SOT_23_5, {
  translate: pt(2.828, 1.403), rotate: 0,
  id: 'U2'
})
// reg_vgate.fb.div.top_res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(2.624, 1.659), rotate: 0,
  id: 'R5'
})
// reg_vgate.fb.div.bottom_res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(2.780, 1.659), rotate: 0,
  id: 'R6'
})
// reg_vgate.power_path.inductor
const L1 = board.add(L_Sunlord_SWPA3012S, {
  translate: pt(2.637, 1.406), rotate: 0,
  id: 'L1'
})
// reg_vgate.power_path.in_cap.cap
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(2.633, 1.553), rotate: 0,
  id: 'C3'
})
// reg_vgate.power_path.out_cap.cap
const C4 = board.add(C_0805_2012Metric, {
  translate: pt(2.806, 1.553), rotate: 0,
  id: 'C4'
})
// reg_vgate.rect
const D2 = board.add(D_SOD_323, {
  translate: pt(2.976, 1.552), rotate: 0,
  id: 'D2'
})
// tp_vgate.tp
const TP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.281, 2.740), rotate: 0,
  id: 'TP4'
})
// conv.power_path.inductor
const L2 = board.add(L_Sunlord_SWRB1207S, {
  translate: pt(0.262, 0.256), rotate: 0,
  id: 'L2'
})
// conv.power_path.in_cap.cap.c[0]
const C5 = board.add(C_1206_3216Metric, {
  translate: pt(1.484, 0.597), rotate: 0,
  id: 'C5'
})
// conv.power_path.in_cap.cap.c[1]
const C6 = board.add(C_1206_3216Metric, {
  translate: pt(1.705, 0.597), rotate: 0,
  id: 'C6'
})
// conv.power_path.in_cap.cap.c[2]
const C7 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 0.849), rotate: 0,
  id: 'C7'
})
// conv.power_path.in_cap.cap.c[3]
const C8 = board.add(C_1206_3216Metric, {
  translate: pt(0.311, 0.849), rotate: 0,
  id: 'C8'
})
// conv.power_path.in_cap.cap.c[4]
const C9 = board.add(C_1206_3216Metric, {
  translate: pt(0.531, 0.849), rotate: 0,
  id: 'C9'
})
// conv.power_path.out_cap.cap.c[0]
const C10 = board.add(C_1206_3216Metric, {
  translate: pt(0.752, 0.849), rotate: 0,
  id: 'C10'
})
// conv.power_path.out_cap.cap.c[1]
const C11 = board.add(C_1206_3216Metric, {
  translate: pt(0.972, 0.849), rotate: 0,
  id: 'C11'
})
// conv.power_path.out_cap.cap.c[2]
const C12 = board.add(C_1206_3216Metric, {
  translate: pt(1.193, 0.849), rotate: 0,
  id: 'C12'
})
// conv.sw[0].driver.ic
const U3 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.709, 0.106), rotate: 0,
  id: 'U3'
})
// conv.sw[0].driver.cap.cap
const C13 = board.add(C_0603_1608Metric, {
  translate: pt(1.769, 0.963), rotate: 0,
  id: 'C13'
})
// conv.sw[0].driver.high_cap.cap
const C14 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.093), rotate: 0,
  id: 'C14'
})
// conv.sw[0].high_gate_res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 1.093), rotate: 0,
  id: 'R7'
})
// conv.sw[0].low_gate_res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 1.093), rotate: 0,
  id: 'R8'
})
// conv.sw[0].high_fet
const Q1 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.039, 0.106), rotate: 0,
  id: 'Q1'
})
// conv.sw[0].low_fet
const Q2 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.370, 0.106), rotate: 0,
  id: 'Q2'
})
// conv.sw[0].high_boot_cap
const C15 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 1.093), rotate: 0,
  id: 'C15'
})
// conv.sw[0].high_boot_diode.diode
const D3 = board.add(D_SOD_323, {
  translate: pt(0.945, 0.971), rotate: 0,
  id: 'D3'
})
// conv.sw[1].ldo.ic
const U4 = board.add(SOT_23_5, {
  translate: pt(1.073, 0.619), rotate: 0,
  id: 'U4'
})
// conv.sw[1].ldo.in_cap.cap
const C16 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 1.093), rotate: 0,
  id: 'C16'
})
// conv.sw[1].ldo.out_cap.cap
const C17 = board.add(C_1206_3216Metric, {
  translate: pt(1.413, 0.849), rotate: 0,
  id: 'C17'
})
// conv.sw[1].iso.ic
const U5 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.701, 0.106), rotate: 0,
  id: 'U5'
})
// conv.sw[1].iso.cap_a.cap
const C18 = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 1.093), rotate: 0,
  id: 'C18'
})
// conv.sw[1].iso.cap_b.cap
const C19 = board.add(C_0603_1608Metric, {
  translate: pt(0.994, 1.093), rotate: 0,
  id: 'C19'
})
// conv.sw[1].driver.ic
const U6 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.709, 0.358), rotate: 0,
  id: 'U6'
})
// conv.sw[1].driver.cap.cap
const C20 = board.add(C_0603_1608Metric, {
  translate: pt(1.150, 1.093), rotate: 0,
  id: 'C20'
})
// conv.sw[1].driver.high_cap.cap
const C21 = board.add(C_0603_1608Metric, {
  translate: pt(1.306, 1.093), rotate: 0,
  id: 'C21'
})
// conv.sw[1].high_gate_res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(1.461, 1.093), rotate: 0,
  id: 'R9'
})
// conv.sw[1].cap.c[0]
const C22 = board.add(C_1206_3216Metric, {
  translate: pt(1.634, 0.849), rotate: 0,
  id: 'C22'
})
// conv.sw[1].cap.c[1]
const C23 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 0.979), rotate: 0,
  id: 'C23'
})
// conv.sw[1].low_gate_res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(1.617, 1.093), rotate: 0,
  id: 'R10'
})
// conv.sw[1].high_fet
const Q3 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.039, 0.358), rotate: 0,
  id: 'Q3'
})
// conv.sw[1].low_fet
const Q4 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.370, 0.358), rotate: 0,
  id: 'Q4'
})
// conv.sw[1].low_boot_diode.diode
const D4 = board.add(D_SOD_323, {
  translate: pt(1.111, 0.971), rotate: 0,
  id: 'D4'
})
// conv.sw[1].high_boot_cap
const C24 = board.add(C_0603_1608Metric, {
  translate: pt(1.773, 1.093), rotate: 0,
  id: 'C24'
})
// conv.sw[1].low_boot_cap
const C25 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.189), rotate: 0,
  id: 'C25'
})
// conv.sw[1].high_boot_diode.diode
const D5 = board.add(D_SOD_323, {
  translate: pt(1.277, 0.971), rotate: 0,
  id: 'D5'
})
// conv.sw[2].ldo.ic
const U7 = board.add(SOT_23_5, {
  translate: pt(1.274, 0.619), rotate: 0,
  id: 'U7'
})
// conv.sw[2].ldo.in_cap.cap
const C26 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.189), rotate: 0,
  id: 'C26'
})
// conv.sw[2].ldo.out_cap.cap
const C27 = board.add(C_1206_3216Metric, {
  translate: pt(0.311, 0.979), rotate: 0,
  id: 'C27'
})
// conv.sw[2].iso.ic
const U8 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.701, 0.358), rotate: 0,
  id: 'U8'
})
// conv.sw[2].iso.cap_a.cap
const C28 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 1.189), rotate: 0,
  id: 'C28'
})
// conv.sw[2].iso.cap_b.cap
const C29 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 1.189), rotate: 0,
  id: 'C29'
})
// conv.sw[2].driver.ic
const U9 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.146, 0.658), rotate: 0,
  id: 'U9'
})
// conv.sw[2].driver.cap.cap
const C30 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 1.189), rotate: 0,
  id: 'C30'
})
// conv.sw[2].driver.high_cap.cap
const C31 = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 1.189), rotate: 0,
  id: 'C31'
})
// conv.sw[2].high_gate_res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 1.189), rotate: 0,
  id: 'R11'
})
// conv.sw[2].cap.c[0]
const C32 = board.add(C_1206_3216Metric, {
  translate: pt(0.531, 0.979), rotate: 0,
  id: 'C32'
})
// conv.sw[2].cap.c[1]
const C33 = board.add(C_1206_3216Metric, {
  translate: pt(0.752, 0.979), rotate: 0,
  id: 'C33'
})
// conv.sw[2].low_gate_res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(1.150, 1.189), rotate: 0,
  id: 'R12'
})
// conv.sw[2].high_fet
const Q5 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.476, 0.658), rotate: 0,
  id: 'Q5'
})
// conv.sw[2].low_fet
const Q6 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.807, 0.658), rotate: 0,
  id: 'Q6'
})
// conv.sw[2].low_boot_diode.diode
const D6 = board.add(D_SOD_323, {
  translate: pt(1.443, 0.971), rotate: 0,
  id: 'D6'
})
// conv.sw[2].high_boot_cap
const C34 = board.add(C_0603_1608Metric, {
  translate: pt(1.306, 1.189), rotate: 0,
  id: 'C34'
})
// conv.sw[2].low_boot_cap
const C35 = board.add(C_0603_1608Metric, {
  translate: pt(1.461, 1.189), rotate: 0,
  id: 'C35'
})
// conv.sw[2].high_boot_diode.diode
const D7 = board.add(D_SOD_323, {
  translate: pt(1.608, 0.971), rotate: 0,
  id: 'D7'
})
// conv_out.conn
const J4 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.986, 2.365), rotate: 0,
  id: 'J4'
})
// tp_conv_out.tp
const TP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.282, 2.740), rotate: 0,
  id: 'TP5'
})
// tp_conv_gnd.tp
const TP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.531, 2.740), rotate: 0,
  id: 'TP6'
})
// fpga.ic
const U10 = board.add(QFN_48_1EP_7x7mm_P0_5mm_EP5_3x5_3mm, {
  translate: pt(0.161, 1.498), rotate: 0,
  id: 'U10'
})
// fpga.vcc_reg.ic
const U11 = board.add(SOT_23_5, {
  translate: pt(0.486, 1.765), rotate: 0,
  id: 'U11'
})
// fpga.vcc_reg.in_cap.cap
const C36 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.992), rotate: 0,
  id: 'C36'
})
// fpga.vcc_reg.out_cap.cap
const C37 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.992), rotate: 0,
  id: 'C37'
})
// fpga.reset_pu.res
const R13 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 1.992), rotate: 0,
  id: 'R13'
})
// fpga.mem.ic
const U12 = board.add(SOIC_8_5_23x5_23mm_P1_27mm, {
  translate: pt(0.183, 1.811), rotate: 0,
  id: 'U12'
})
// fpga.mem.vcc_cap.cap
const C38 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 1.992), rotate: 0,
  id: 'C38'
})
// fpga.prog.conn
const J5 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(0.531, 1.482), rotate: 0,
  id: 'J5'
})
// fpga.cs_jmp.device
const JP1 = board.add(SolderJumper_2_P1_3mm_Open_TrianglePad1_0x1_5mm, {
  translate: pt(0.671, 1.748), rotate: 0,
  id: 'JP1'
})
// fpga.mem_pu.res
const R14 = board.add(R_0603_1608Metric, {
  translate: pt(0.682, 1.992), rotate: 0,
  id: 'R14'
})
// fpga.vio_cap0.cap
const C39 = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 1.992), rotate: 0,
  id: 'C39'
})
// fpga.vio_cap1.cap
const C40 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.089), rotate: 0,
  id: 'C40'
})
// fpga.vio_cap2.cap
const C41 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 2.089), rotate: 0,
  id: 'C41'
})
// fpga.vpp_cap.cap
const C42 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 2.089), rotate: 0,
  id: 'C42'
})
// fpga.pll_res.res
const R15 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 2.089), rotate: 0,
  id: 'R15'
})
// fpga.vcc_cap.cap
const C43 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 2.089), rotate: 0,
  id: 'C43'
})
// fpga.pll_lf.cap
const C44 = board.add(C_0805_2012Metric, {
  translate: pt(0.843, 1.737), rotate: 0,
  id: 'C44'
})
// fpga.pll_hf.cap
const C45 = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 2.089), rotate: 0,
  id: 'C45'
})
// cdone.package
const D8 = board.add(LED_0603_1608Metric, {
  translate: pt(3.590, 2.264), rotate: 0,
  id: 'D8'
})
// cdone.res
const R16 = board.add(R_0603_1608Metric, {
  translate: pt(3.589, 2.361), rotate: 0,
  id: 'R16'
})
// fpga_osc.device
const X1 = board.add(Crystal_SMD_2520_4Pin_2_5x2_0mm, {
  translate: pt(3.346, 2.294), rotate: 0,
  id: 'X1'
})
// fpga_osc.cap.cap
const C46 = board.add(C_0603_1608Metric, {
  translate: pt(3.337, 2.422), rotate: 0,
  id: 'C46'
})
// fpga_sw.package
const SW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.761, 2.348), rotate: 0,
  id: 'SW1'
})
// fpga_led.led[0].package
const D9 = board.add(LED_0603_1608Metric, {
  translate: pt(3.216, 1.365), rotate: 0,
  id: 'D9'
})
// fpga_led.led[0].res
const R17 = board.add(R_0603_1608Metric, {
  translate: pt(3.215, 1.559), rotate: 0,
  id: 'R17'
})
// fpga_led.led[1].package
const D10 = board.add(LED_0603_1608Metric, {
  translate: pt(3.372, 1.365), rotate: 0,
  id: 'D10'
})
// fpga_led.led[1].res
const R18 = board.add(R_0603_1608Metric, {
  translate: pt(3.371, 1.559), rotate: 0,
  id: 'R18'
})
// fpga_led.led[2].package
const D11 = board.add(LED_0603_1608Metric, {
  translate: pt(3.216, 1.462), rotate: 0,
  id: 'D11'
})
// fpga_led.led[2].res
const R19 = board.add(R_0603_1608Metric, {
  translate: pt(3.215, 1.656), rotate: 0,
  id: 'R19'
})
// fpga_led.led[3].package
const D12 = board.add(LED_0603_1608Metric, {
  translate: pt(3.372, 1.462), rotate: 0,
  id: 'D12'
})
// fpga_led.led[3].res
const R20 = board.add(R_0603_1608Metric, {
  translate: pt(3.371, 1.656), rotate: 0,
  id: 'R20'
})
// usb_fpga_bitbang.dp_pull_res
const R21 = board.add(R_0603_1608Metric, {
  translate: pt(1.418, 2.264), rotate: 0,
  id: 'R21'
})
// usb_fpga_bitbang.dp_res
const R22 = board.add(R_0603_1608Metric, {
  translate: pt(1.418, 2.361), rotate: 0,
  id: 'R22'
})
// usb_fpga_bitbang.dm_res
const R23 = board.add(R_0603_1608Metric, {
  translate: pt(1.418, 2.458), rotate: 0,
  id: 'R23'
})
// usb_fpga_esd
const U13 = board.add(SOT_23, {
  translate: pt(3.293, 2.769), rotate: 0,
  id: 'U13'
})
// mcu.swd.conn
const J6 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(2.498, 0.146), rotate: 0,
  id: 'J6'
})
// mcu.ic
const U14 = board.add(QFN_56_1EP_7x7mm_P0_4mm_EP3_2x3_2mm, {
  translate: pt(2.127, 0.163), rotate: 0,
  id: 'U14'
})
// mcu.iovdd_cap[0].cap
const C47 = board.add(C_0603_1608Metric, {
  translate: pt(2.633, 0.393), rotate: 0,
  id: 'C47'
})
// mcu.iovdd_cap[1].cap
const C48 = board.add(C_0603_1608Metric, {
  translate: pt(2.789, 0.393), rotate: 0,
  id: 'C48'
})
// mcu.iovdd_cap[2].cap
const C49 = board.add(C_0603_1608Metric, {
  translate: pt(2.023, 0.658), rotate: 0,
  id: 'C49'
})
// mcu.iovdd_cap[3].cap
const C50 = board.add(C_0603_1608Metric, {
  translate: pt(2.179, 0.658), rotate: 0,
  id: 'C50'
})
// mcu.iovdd_cap[4].cap
const C51 = board.add(C_0603_1608Metric, {
  translate: pt(2.335, 0.658), rotate: 0,
  id: 'C51'
})
// mcu.iovdd_cap[5].cap
const C52 = board.add(C_0603_1608Metric, {
  translate: pt(2.491, 0.658), rotate: 0,
  id: 'C52'
})
// mcu.avdd_cap.cap
const C53 = board.add(C_0603_1608Metric, {
  translate: pt(2.646, 0.658), rotate: 0,
  id: 'C53'
})
// mcu.vreg_in_cap.cap
const C54 = board.add(C_0603_1608Metric, {
  translate: pt(2.802, 0.658), rotate: 0,
  id: 'C54'
})
// mcu.mem.ic
const U15 = board.add(SOIC_8_5_23x5_23mm_P1_27mm, {
  translate: pt(2.148, 0.477), rotate: 0,
  id: 'U15'
})
// mcu.mem.vcc_cap.cap
const C55 = board.add(C_0603_1608Metric, {
  translate: pt(2.023, 0.755), rotate: 0,
  id: 'C55'
})
// mcu.dvdd_cap[0].cap
const C56 = board.add(C_0603_1608Metric, {
  translate: pt(2.179, 0.755), rotate: 0,
  id: 'C56'
})
// mcu.dvdd_cap[1].cap
const C57 = board.add(C_0603_1608Metric, {
  translate: pt(2.335, 0.755), rotate: 0,
  id: 'C57'
})
// mcu.vreg_out_cap.cap
const C58 = board.add(C_0603_1608Metric, {
  translate: pt(2.491, 0.755), rotate: 0,
  id: 'C58'
})
// mcu.usb_res.dp_res
const R24 = board.add(R_0603_1608Metric, {
  translate: pt(2.646, 0.755), rotate: 0,
  id: 'R24'
})
// mcu.usb_res.dm_res
const R25 = board.add(R_0603_1608Metric, {
  translate: pt(2.802, 0.755), rotate: 0,
  id: 'R25'
})
// mcu.crystal.package
const X2 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(2.453, 0.431), rotate: 0,
  id: 'X2'
})
// mcu.crystal.cap_a
const C59 = board.add(C_0603_1608Metric, {
  translate: pt(2.023, 0.852), rotate: 0,
  id: 'C59'
})
// mcu.crystal.cap_b
const C60 = board.add(C_0603_1608Metric, {
  translate: pt(2.179, 0.852), rotate: 0,
  id: 'C60'
})
// mcu_sw.package
const SW2 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.214, 2.348), rotate: 0,
  id: 'SW2'
})
// mcu_leds.led[0].package
const D13 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 2.264), rotate: 0,
  id: 'D13'
})
// mcu_leds.led[0].res
const R26 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.459), rotate: 0,
  id: 'R26'
})
// mcu_leds.led[1].package
const D14 = board.add(LED_0603_1608Metric, {
  translate: pt(0.215, 2.264), rotate: 0,
  id: 'D14'
})
// mcu_leds.led[1].res
const R27 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.459), rotate: 0,
  id: 'R27'
})
// mcu_leds.led[2].package
const D15 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 2.362), rotate: 0,
  id: 'D15'
})
// mcu_leds.led[2].res
const R28 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.556), rotate: 0,
  id: 'R28'
})
// mcu_leds.led[3].package
const D16 = board.add(LED_0603_1608Metric, {
  translate: pt(0.215, 2.362), rotate: 0,
  id: 'D16'
})
// mcu_leds.led[3].res
const R29 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.556), rotate: 0,
  id: 'R29'
})
// usb_mcu_esd
const U16 = board.add(SOT_23, {
  translate: pt(3.484, 2.769), rotate: 0,
  id: 'U16'
})
// tp_fpga[0].tp
const TP7 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.783, 2.740), rotate: 0,
  id: 'TP7'
})
// tp_fpga[1].tp
const TP8 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.032, 2.740), rotate: 0,
  id: 'TP8'
})
// tp_fpga[2].tp
const TP9 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.781, 2.740), rotate: 0,
  id: 'TP9'
})
// tp_fpga[3].tp
const TP10 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.030, 2.740), rotate: 0,
  id: 'TP10'
})
// pwm_filter.tp[0L].tp
const TP11 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.004, 2.273), rotate: 0,
  id: 'TP11'
})
// pwm_filter.tp[0H].tp
const TP12 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.175, 2.273), rotate: 0,
  id: 'TP12'
})
// pwm_filter.tp[1L].tp
const TP13 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.004, 2.387), rotate: 0,
  id: 'TP13'
})
// pwm_filter.tp[1H].tp
const TP14 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.175, 2.387), rotate: 0,
  id: 'TP14'
})
// pwm_filter.tp[2L].tp
const TP15 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.004, 2.501), rotate: 0,
  id: 'TP15'
})
// pwm_filter.tp[2H].tp
const TP16 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.175, 2.501), rotate: 0,
  id: 'TP16'
})
// tp_pwm.elts[0L].rc.r
const R30 = board.add(R_0603_1608Metric, {
  translate: pt(0.449, 2.264), rotate: 0,
  id: 'R30'
})
// tp_pwm.elts[0L].rc.c
const C61 = board.add(C_0603_1608Metric, {
  translate: pt(0.605, 2.264), rotate: 0,
  id: 'C61'
})
// tp_pwm.elts[0H].rc.r
const R31 = board.add(R_0603_1608Metric, {
  translate: pt(0.761, 2.264), rotate: 0,
  id: 'R31'
})
// tp_pwm.elts[0H].rc.c
const C62 = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 2.361), rotate: 0,
  id: 'C62'
})
// tp_pwm.elts[1L].rc.r
const R32 = board.add(R_0603_1608Metric, {
  translate: pt(0.605, 2.361), rotate: 0,
  id: 'R32'
})
// tp_pwm.elts[1L].rc.c
const C63 = board.add(C_0603_1608Metric, {
  translate: pt(0.761, 2.361), rotate: 0,
  id: 'C63'
})
// tp_pwm.elts[1H].rc.r
const R33 = board.add(R_0603_1608Metric, {
  translate: pt(0.449, 2.458), rotate: 0,
  id: 'R33'
})
// tp_pwm.elts[1H].rc.c
const C64 = board.add(C_0603_1608Metric, {
  translate: pt(0.605, 2.458), rotate: 0,
  id: 'C64'
})
// tp_pwm.elts[2L].rc.r
const R34 = board.add(R_0603_1608Metric, {
  translate: pt(0.761, 2.458), rotate: 0,
  id: 'R34'
})
// tp_pwm.elts[2L].rc.c
const C65 = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 2.555), rotate: 0,
  id: 'C65'
})
// tp_pwm.elts[2H].rc.r
const R35 = board.add(R_0603_1608Metric, {
  translate: pt(0.605, 2.555), rotate: 0,
  id: 'R35'
})
// tp_pwm.elts[2H].rc.c
const C66 = board.add(C_0603_1608Metric, {
  translate: pt(0.761, 2.555), rotate: 0,
  id: 'C66'
})
// conv_in_sense.div.top_res
const R36 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.731), rotate: 0,
  id: 'R36'
})
// conv_in_sense.div.bottom_res
const R37 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.828), rotate: 0,
  id: 'R37'
})
// conv_out_sense.div.top_res
const R38 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 2.731), rotate: 0,
  id: 'R38'
})
// conv_out_sense.div.bottom_res
const R39 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 2.828), rotate: 0,
  id: 'R39'
})

board.setNetlist([
  {name: "vusb", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["J2", "A4"], ["J2", "B9"], ["J2", "B4"], ["J2", "A9"], ["TP1", "1"], ["U1", "3"], ["U2", "5"], ["U2", "4"], ["C1", "1"], ["L1", "1"], ["C3", "1"]]},
  {name: "gnd", pads: [["U13", "3"], ["U16", "3"], ["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["J2", "A1"], ["J2", "B12"], ["J2", "B1"], ["J2", "A12"], ["J3", "1"], ["TP2", "1"], ["U1", "1"], ["D1", "2"], ["U2", "2"], ["J4", "1"], ["TP6", "1"], ["U10", "49"], ["R16", "2"], ["X1", "2"], ["SW1", "2"], ["U14", "19"], ["U14", "57"], ["SW2", "2"], ["R37", "2"], ["R39", "2"], ["J1", "S1"], ["J2", "S1"], ["C1", "2"], ["C2", "2"], ["U11", "2"], ["U12", "4"], ["C39", "2"], ["C40", "2"], ["C41", "2"], ["C42", "2"], ["C43", "2"], ["C44", "2"], ["C45", "2"], ["C46", "2"], ["R17", "2"], ["R18", "2"], ["R19", "2"], ["R20", "2"], ["C47", "2"], ["C48", "2"], ["C49", "2"], ["C50", "2"], ["C51", "2"], ["C52", "2"], ["C53", "2"], ["C54", "2"], ["U15", "4"], ["C56", "2"], ["C57", "2"], ["C58", "2"], ["X2", "2"], ["X2", "4"], ["R26", "2"], ["R27", "2"], ["R28", "2"], ["R29", "2"], ["R6", "2"], ["U5", "4"], ["U8", "4"], ["C61", "2"], ["C62", "2"], ["C63", "2"], ["C64", "2"], ["C65", "2"], ["C66", "2"], ["R1", "1"], ["R2", "1"], ["Q2", "1"], ["Q2", "2"], ["Q2", "3"], ["J5", "3"], ["J5", "5"], ["J5", "9"], ["J6", "3"], ["J6", "5"], ["J6", "9"], ["C59", "2"], ["C60", "2"], ["R3", "1"], ["R4", "1"], ["C3", "2"], ["C4", "2"], ["U3", "4"], ["C36", "2"], ["C37", "2"], ["C38", "2"], ["C55", "2"], ["C18", "2"], ["C28", "2"], ["C5", "2"], ["C6", "2"], ["C7", "2"], ["C8", "2"], ["C9", "2"], ["C10", "2"], ["C11", "2"], ["C12", "2"], ["C13", "2"]]},
  {name: "v3v3", pads: [["U1", "2"], ["TP3", "1"], ["D1", "1"], ["U10", "22"], ["U10", "33"], ["U10", "1"], ["U10", "24"], ["X1", "1"], ["X1", "4"], ["U14", "1"], ["U14", "10"], ["U14", "22"], ["U14", "33"], ["U14", "42"], ["U14", "49"], ["U14", "44"], ["U14", "43"], ["U14", "48"], ["C2", "1"], ["U11", "1"], ["R13", "1"], ["U12", "8"], ["J5", "1"], ["R14", "1"], ["C39", "1"], ["C40", "1"], ["C41", "1"], ["C42", "1"], ["C46", "1"], ["J6", "1"], ["C47", "1"], ["C48", "1"], ["C49", "1"], ["C50", "1"], ["C51", "1"], ["C52", "1"], ["C53", "1"], ["C54", "1"], ["U15", "8"], ["U5", "1"], ["U8", "1"], ["U11", "3"], ["U12", "3"], ["U12", "7"], ["C36", "1"], ["C38", "1"], ["C55", "1"], ["C18", "1"], ["C28", "1"]]},
  {name: "vgate", pads: [["TP4", "1"], ["D2", "1"], ["R5", "1"], ["C4", "1"], ["U3", "1"], ["C13", "1"], ["D4", "2"]]},
  {name: "conv.pwr_in", pads: [["J3", "2"], ["R36", "1"], ["Q1", "5"], ["Q1", "6"], ["Q1", "7"], ["Q1", "8"], ["C5", "1"], ["C6", "1"], ["C7", "1"], ["C8", "1"], ["C9", "1"]]},
  {name: "conv.pwr_out", pads: [["J4", "2"], ["TP5", "1"], ["R38", "1"], ["L2", "2"], ["C10", "1"], ["C11", "1"], ["C12", "1"]]},
  {name: "fpga.cdone", pads: [["U10", "7"], ["D8", "2"]]},
  {name: "fpga_osc.out", pads: [["X1", "3"], ["U10", "37"]]},
  {name: "fpga_sw.out", pads: [["U10", "32"], ["SW1", "1"]]},
  {name: "fpga.gpio.led_0", pads: [["U10", "21"], ["D9", "2"]]},
  {name: "fpga.gpio.led_1", pads: [["U10", "20"], ["D10", "2"]]},
  {name: "fpga.gpio.led_2", pads: [["U10", "19"], ["D11", "2"]]},
  {name: "fpga.gpio.led_3", pads: [["U10", "18"], ["D12", "2"]]},
  {name: "usb_fpga_bitbang.dp_pull", pads: [["U10", "27"], ["R21", "1"]]},
  {name: "usb_fpga_bitbang.dp", pads: [["U10", "26"], ["R22", "1"]]},
  {name: "usb_fpga_bitbang.dm", pads: [["U10", "25"], ["R23", "1"]]},
  {name: "usb_fpga_chain_0.d_P", pads: [["U13", "2"], ["J2", "A6"], ["J2", "B6"], ["R22", "2"], ["R21", "2"]]},
  {name: "usb_fpga_chain_0.d_N", pads: [["U13", "1"], ["J2", "A7"], ["J2", "B7"], ["R23", "2"]]},
  {name: "mcu_sw.out", pads: [["U14", "29"], ["SW2", "1"]]},
  {name: "mcu.gpio.led_0", pads: [["U14", "34"], ["D13", "2"]]},
  {name: "mcu.gpio.led_1", pads: [["U14", "35"], ["D14", "2"]]},
  {name: "mcu.gpio.led_2", pads: [["U14", "36"], ["D15", "2"]]},
  {name: "mcu.gpio.led_3", pads: [["U14", "37"], ["D16", "2"]]},
  {name: "usb_mcu_chain_0.d_P", pads: [["U16", "2"], ["J1", "A6"], ["J1", "B6"], ["R24", "2"]]},
  {name: "usb_mcu_chain_0.d_N", pads: [["U16", "1"], ["J1", "A7"], ["J1", "B7"], ["R25", "2"]]},
  {name: "tp_fpga[0].io", pads: [["U14", "14"], ["U10", "2"], ["TP7", "1"]]},
  {name: "tp_fpga[1].io", pads: [["U14", "13"], ["U10", "3"], ["TP8", "1"]]},
  {name: "tp_fpga[2].io", pads: [["U14", "12"], ["U10", "4"], ["TP9", "1"]]},
  {name: "tp_fpga[3].io", pads: [["U14", "11"], ["U10", "6"], ["TP10", "1"]]},
  {name: "fpga.gpio.pwm_0L", pads: [["U10", "47"], ["TP11", "1"], ["R30", "1"]]},
  {name: "fpga.gpio.pwm_0H", pads: [["U10", "48"], ["TP12", "1"], ["R31", "1"]]},
  {name: "fpga.gpio.pwm_1L", pads: [["U10", "45"], ["TP13", "1"], ["R32", "1"]]},
  {name: "fpga.gpio.pwm_1H", pads: [["U10", "46"], ["TP14", "1"], ["R33", "1"]]},
  {name: "fpga.gpio.pwm_2L", pads: [["U10", "43"], ["TP15", "1"], ["R34", "1"]]},
  {name: "fpga.gpio.pwm_2H", pads: [["U10", "44"], ["TP16", "1"], ["R35", "1"]]},
  {name: "tp_pwm.output.0L", pads: [["U3", "3"], ["R30", "2"], ["C61", "1"]]},
  {name: "tp_pwm.output.0H", pads: [["U3", "2"], ["R31", "2"], ["C62", "1"]]},
  {name: "tp_pwm.output.1L", pads: [["U5", "3"], ["R32", "2"], ["C63", "1"]]},
  {name: "tp_pwm.output.1H", pads: [["U5", "2"], ["R33", "2"], ["C64", "1"]]},
  {name: "tp_pwm.output.2L", pads: [["U8", "3"], ["R34", "2"], ["C65", "1"]]},
  {name: "tp_pwm.output.2H", pads: [["U8", "2"], ["R35", "2"], ["C66", "1"]]},
  {name: "conv_in_sense.output", pads: [["U14", "38"], ["R36", "2"], ["R37", "1"]]},
  {name: "conv_out_sense.output", pads: [["U14", "39"], ["R38", "2"], ["R39", "1"]]},
  {name: "usb_mcu.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb_mcu.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "usb_fpga.conn.cc.cc1", pads: [["J2", "A5"], ["R3", "2"]]},
  {name: "usb_fpga.conn.cc.cc2", pads: [["J2", "B5"], ["R4", "2"]]},
  {name: "reg_vgate.fb.output", pads: [["U2", "3"], ["R5", "2"], ["R6", "1"]]},
  {name: "reg_vgate.power_path.switch", pads: [["U2", "1"], ["L1", "2"], ["D2", "2"]]},
  {name: "conv.sw[0].low_out", pads: [["Q2", "5"], ["Q2", "6"], ["Q2", "7"], ["Q2", "8"], ["Q4", "1"], ["Q4", "2"], ["Q4", "3"], ["C25", "2"], ["U4", "2"], ["U5", "5"], ["U6", "4"], ["C22", "2"], ["C23", "2"], ["C16", "2"], ["C17", "2"], ["C19", "2"], ["C20", "2"]]},
  {name: "conv.sw[1].high_in", pads: [["Q3", "5"], ["Q3", "6"], ["Q3", "7"], ["Q3", "8"], ["C22", "1"], ["C23", "1"], ["Q1", "1"], ["Q1", "2"], ["Q1", "3"], ["C15", "2"], ["U3", "6"], ["C14", "2"]]},
  {name: "conv.sw[1].high_boot_out", pads: [["D3", "2"], ["C24", "1"], ["D5", "1"], ["U6", "8"], ["C21", "1"]]},
  {name: "conv.sw[1].low_out", pads: [["Q4", "5"], ["Q4", "6"], ["Q4", "7"], ["Q4", "8"], ["Q6", "1"], ["Q6", "2"], ["Q6", "3"], ["C35", "2"], ["U7", "2"], ["U8", "5"], ["U9", "4"], ["C32", "2"], ["C33", "2"], ["C26", "2"], ["C27", "2"], ["C29", "2"], ["C30", "2"]]},
  {name: "conv.sw[2].high_in", pads: [["Q5", "5"], ["Q5", "6"], ["Q5", "7"], ["Q5", "8"], ["C32", "1"], ["C33", "1"], ["Q3", "1"], ["Q3", "2"], ["Q3", "3"], ["C24", "2"], ["U6", "6"], ["C21", "2"]]},
  {name: "conv.sw[2].low_boot_in", pads: [["D6", "2"], ["C25", "1"], ["D4", "1"], ["U4", "1"], ["U6", "1"], ["U4", "3"], ["C16", "1"], ["C20", "1"]]},
  {name: "conv.sw[2].high_boot_out", pads: [["D5", "2"], ["C34", "1"], ["D7", "1"], ["U9", "8"], ["C31", "1"]]},
  {name: "conv.sw[2].low_boot_out", pads: [["D7", "2"], ["C35", "1"], ["D6", "1"], ["U7", "1"], ["U9", "1"], ["U7", "3"], ["C26", "1"], ["C30", "1"]]},
  {name: "conv.sw_merge", pads: [["Q6", "5"], ["Q6", "6"], ["Q6", "7"], ["Q6", "8"], ["L2", "1"], ["Q5", "1"], ["Q5", "2"], ["Q5", "3"], ["C34", "2"], ["U9", "6"], ["C31", "2"]]},
  {name: "conv.sw[0].high_gate_res.a", pads: [["R7", "1"], ["U3", "7"]]},
  {name: "conv.sw[0].high_gate_res.b", pads: [["R7", "2"], ["Q1", "4"]]},
  {name: "conv.sw[0].low_gate_res.a", pads: [["R8", "1"], ["U3", "5"]]},
  {name: "conv.sw[0].low_gate_res.b", pads: [["R8", "2"], ["Q2", "4"]]},
  {name: "conv.sw[0].high_boot_cap.pos", pads: [["C15", "1"], ["D3", "1"], ["U3", "8"], ["C14", "1"]]},
  {name: "conv.sw[1].iso.pwr_b", pads: [["U5", "8"], ["U4", "5"], ["C19", "1"], ["C17", "1"]]},
  {name: "conv.sw[1].driver.high_in", pads: [["U6", "2"], ["U5", "7"]]},
  {name: "conv.sw[1].driver.low_in", pads: [["U6", "3"], ["U5", "6"]]},
  {name: "conv.sw[1].high_gate_res.a", pads: [["R9", "1"], ["U6", "7"]]},
  {name: "conv.sw[1].high_gate_res.b", pads: [["R9", "2"], ["Q3", "4"]]},
  {name: "conv.sw[1].low_gate_res.a", pads: [["R10", "1"], ["U6", "5"]]},
  {name: "conv.sw[1].low_gate_res.b", pads: [["R10", "2"], ["Q4", "4"]]},
  {name: "conv.sw[2].iso.pwr_b", pads: [["U8", "8"], ["U7", "5"], ["C29", "1"], ["C27", "1"]]},
  {name: "conv.sw[2].driver.high_in", pads: [["U9", "2"], ["U8", "7"]]},
  {name: "conv.sw[2].driver.low_in", pads: [["U9", "3"], ["U8", "6"]]},
  {name: "conv.sw[2].high_gate_res.a", pads: [["R11", "1"], ["U9", "7"]]},
  {name: "conv.sw[2].high_gate_res.b", pads: [["R11", "2"], ["Q5", "4"]]},
  {name: "conv.sw[2].low_gate_res.a", pads: [["R12", "1"], ["U9", "5"]]},
  {name: "conv.sw[2].low_gate_res.b", pads: [["R12", "2"], ["Q6", "4"]]},
  {name: "fpga.ic.creset_b", pads: [["U10", "8"], ["R13", "2"], ["J5", "10"]]},
  {name: "fpga.ic.spi_config.sck", pads: [["U10", "15"], ["U12", "6"], ["J5", "4"]]},
  {name: "fpga.ic.spi_config.mosi", pads: [["U10", "14"], ["U12", "5"], ["J5", "6"]]},
  {name: "fpga.ic.spi_config.miso", pads: [["U10", "17"], ["U12", "2"], ["J5", "8"]]},
  {name: "fpga.ic.spi_config_cs", pads: [["U10", "16"], ["J5", "2"], ["JP1", "1"]]},
  {name: "fpga.cs_jmp.output", pads: [["JP1", "2"], ["R14", "2"], ["U12", "1"]]},
  {name: "fpga.vcc_reg.pwr_out", pads: [["U10", "5"], ["U10", "30"], ["U11", "5"], ["R15", "1"], ["C43", "1"], ["C37", "1"]]},
  {name: "fpga.pll_res.pwr_out", pads: [["U10", "29"], ["R15", "2"], ["C44", "1"], ["C45", "1"]]},
  {name: "cdone.res.a", pads: [["R16", "1"], ["D8", "1"]]},
  {name: "fpga_led.led[0].res.a", pads: [["R17", "1"], ["D9", "1"]]},
  {name: "fpga_led.led[1].res.a", pads: [["R18", "1"], ["D10", "1"]]},
  {name: "fpga_led.led[2].res.a", pads: [["R19", "1"], ["D11", "1"]]},
  {name: "fpga_led.led[3].res.a", pads: [["R20", "1"], ["D12", "1"]]},
  {name: "mcu.xtal_node.xi", pads: [["U14", "20"], ["X2", "1"], ["C59", "1"]]},
  {name: "mcu.xtal_node.xo", pads: [["U14", "21"], ["X2", "3"], ["C60", "1"]]},
  {name: "mcu.swd_node.swdio", pads: [["U14", "25"], ["J6", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["U14", "24"], ["J6", "4"]]},
  {name: "mcu.reset_node", pads: [["U14", "26"], ["J6", "10"]]},
  {name: "mcu.ic.qspi.sck", pads: [["U14", "52"], ["U15", "6"]]},
  {name: "mcu.ic.qspi.mosi", pads: [["U14", "53"], ["U15", "5"]]},
  {name: "mcu.ic.qspi.miso", pads: [["U14", "55"], ["U15", "2"]]},
  {name: "mcu.ic.qspi_cs", pads: [["U14", "56"], ["U15", "1"]]},
  {name: "mcu.ic.qspi_sd2", pads: [["U14", "54"], ["U15", "3"]]},
  {name: "mcu.ic.qspi_sd3", pads: [["U14", "51"], ["U15", "7"]]},
  {name: "mcu.ic.vreg_vout", pads: [["U14", "45"], ["U14", "23"], ["U14", "50"], ["C56", "1"], ["C57", "1"], ["C58", "1"]]},
  {name: "mcu.usb_chain_0.d_P", pads: [["U14", "47"], ["R24", "1"]]},
  {name: "mcu.usb_chain_0.d_N", pads: [["U14", "46"], ["R25", "1"]]},
  {name: "mcu.swd.swo", pads: [["U14", "2"], ["J6", "6"]]},
  {name: "mcu.swd.tdi", pads: [["U14", "3"], ["J6", "8"]]},
  {name: "mcu_leds.led[0].res.a", pads: [["R26", "1"], ["D13", "1"]]},
  {name: "mcu_leds.led[1].res.a", pads: [["R27", "1"], ["D14", "1"]]},
  {name: "mcu_leds.led[2].res.a", pads: [["R28", "1"], ["D15", "1"]]},
  {name: "mcu_leds.led[3].res.a", pads: [["R29", "1"], ["D16", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.7659448818897645, 2.9748031496062994);
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


