const board = new PCB();

// jlc_th.th1
const LH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.495, 1.563), rotate: 0,
  id: 'LH1'
})
// jlc_th.th2
const LH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.534, 1.563), rotate: 0,
  id: 'LH2'
})
// jlc_th.th3
const LH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.495, 1.602), rotate: 0,
  id: 'LH3'
})
// pwr.conn
const LJ1 = board.add(JST_SH_SM02B_SRSS_TB_1x02_1MP_P1_00mm_Horizontal, {
  translate: pt(1.614, 0.793), rotate: 0,
  id: 'LJ1'
})
// tp_v12.tp
const LTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.706, 1.224), rotate: 0,
  id: 'LTP1'
})
// tp_gnd.tp
const LTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.957, 1.224), rotate: 0,
  id: 'LTP2'
})
// reg_3v3.ic
const LU1 = board.add(SOT_23_6, {
  translate: pt(0.937, 0.067), rotate: 0,
  id: 'LU1'
})
// reg_3v3.fb.div.top_res
const LR1 = board.add(R_0603_1608Metric, {
  translate: pt(0.914, 0.332), rotate: 0,
  id: 'LR1'
})
// reg_3v3.fb.div.bottom_res
const LR2 = board.add(R_0603_1608Metric, {
  translate: pt(1.070, 0.332), rotate: 0,
  id: 'LR2'
})
// reg_3v3.hf_in_cap.cap
const LC1 = board.add(C_0402_1005Metric, {
  translate: pt(1.316, 0.321), rotate: 0,
  id: 'LC1'
})
// reg_3v3.boot_cap
const LC2 = board.add(C_0402_1005Metric, {
  translate: pt(0.892, 0.418), rotate: 0,
  id: 'LC2'
})
// reg_3v3.power_path.inductor
const LL1 = board.add(L_1210_3225Metric, {
  translate: pt(1.146, 0.062), rotate: 0,
  id: 'LL1'
})
// reg_3v3.power_path.in_cap.cap
const LC3 = board.add(C_1206_3216Metric, {
  translate: pt(0.946, 0.219), rotate: 0,
  id: 'LC3'
})
// reg_3v3.power_path.out_cap.cap
const LC4 = board.add(C_1206_3216Metric, {
  translate: pt(1.167, 0.219), rotate: 0,
  id: 'LC4'
})
// reg_3v3.en_res
const LR3 = board.add(R_0402_1005Metric, {
  translate: pt(1.204, 0.322), rotate: 0,
  id: 'LR3'
})
// tp_3v3.tp
const LTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 1.600), rotate: 0,
  id: 'LTP3'
})
// prot_3v3.diode
const LD1 = board.add(D_SOD_323, {
  translate: pt(0.314, 1.600), rotate: 0,
  id: 'LD1'
})
// mcu.ic
const LU2 = board.add(QFN_32_1EP_5x5mm_P0_5mm_EP3_65x3_65mm, {
  translate: pt(0.122, 0.122), rotate: 0,
  id: 'LU2'
})
// mcu.vdd_bulk_cap.cap
const LC5 = board.add(C_0805_2012Metric, {
  translate: pt(0.286, 0.322), rotate: 0,
  id: 'LC5'
})
// mcu.vdda_cap0.cap
const LC6 = board.add(C_0402_1005Metric, {
  translate: pt(0.417, 0.430), rotate: 0,
  id: 'LC6'
})
// mcu.vdda_cap1.cap
const LC7 = board.add(C_0402_1005Metric, {
  translate: pt(0.528, 0.430), rotate: 0,
  id: 'LC7'
})
// mcu.vddrtc_cap.cap
const LC8 = board.add(C_0402_1005Metric, {
  translate: pt(0.639, 0.430), rotate: 0,
  id: 'LC8'
})
// mcu.vddcpu_cap.cap
const LC9 = board.add(C_0402_1005Metric, {
  translate: pt(0.036, 0.527), rotate: 0,
  id: 'LC9'
})
// mcu.vddspi_cap.cap
const LC10 = board.add(C_0402_1005Metric, {
  translate: pt(0.147, 0.527), rotate: 0,
  id: 'LC10'
})
// mcu.ant
const LANT1 = board.add(D_1206_3216Metric, {
  translate: pt(0.090, 0.328), rotate: 0,
  id: 'LANT1'
})
// mcu.pi.c1
const LC11 = board.add(C_0603_1608Metric, {
  translate: pt(0.451, 0.312), rotate: 0,
  id: 'LC11'
})
// mcu.pi.c2
const LC12 = board.add(C_0603_1608Metric, {
  translate: pt(0.606, 0.312), rotate: 0,
  id: 'LC12'
})
// mcu.pi.l
const LL2 = board.add(L_0603_1608Metric, {
  translate: pt(0.058, 0.441), rotate: 0,
  id: 'LL2'
})
// mcu.vdd3p3_l_cap.cap
const LC13 = board.add(C_0402_1005Metric, {
  translate: pt(0.258, 0.527), rotate: 0,
  id: 'LC13'
})
// mcu.vdd3p3_cap.cap
const LC14 = board.add(C_0402_1005Metric, {
  translate: pt(0.369, 0.527), rotate: 0,
  id: 'LC14'
})
// mcu.vdd3p3_l.ind
const LL3 = board.add(L_0402_1005Metric, {
  translate: pt(0.193, 0.431), rotate: 0,
  id: 'LL3'
})
// mcu.crystal.package
const LX1 = board.add(Crystal_SMD_2520_4Pin_2_5x2_0mm, {
  translate: pt(0.665, 0.059), rotate: 0,
  id: 'LX1'
})
// mcu.crystal.cap_a
const LC15 = board.add(C_0402_1005Metric, {
  translate: pt(0.480, 0.527), rotate: 0,
  id: 'LC15'
})
// mcu.crystal.cap_b
const LC16 = board.add(C_0402_1005Metric, {
  translate: pt(0.591, 0.527), rotate: 0,
  id: 'LC16'
})
// mcu.prog.conn
const LJ2 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(0.421, 0.079), rotate: 0,
  id: 'LJ2'
})
// mcu.en_pull.rc.r
const LR4 = board.add(R_0402_1005Metric, {
  translate: pt(0.305, 0.431), rotate: 0,
  id: 'LR4'
})
// mcu.en_pull.rc.c
const LC17 = board.add(C_0402_1005Metric, {
  translate: pt(0.702, 0.527), rotate: 0,
  id: 'LC17'
})
// ledr.package
const LD2 = board.add(LED_0603_1608Metric, {
  translate: pt(1.081, 1.215), rotate: 0,
  id: 'LD2'
})
// ledr.res
const LR5 = board.add(R_0402_1005Metric, {
  translate: pt(1.059, 1.302), rotate: 0,
  id: 'LR5'
})
// v12_sense.div.top_res
const LR6 = board.add(R_0603_1608Metric, {
  translate: pt(0.846, 1.215), rotate: 0,
  id: 'LR6'
})
// v12_sense.div.bottom_res
const LR7 = board.add(R_0603_1608Metric, {
  translate: pt(0.846, 1.312), rotate: 0,
  id: 'LR7'
})
// qwiic.conn
const LJ3 = board.add(JST_SH_SM04B_SRSS_TB_1x04_1MP_P1_00mm_Horizontal, {
  translate: pt(0.154, 1.315), rotate: 0,
  id: 'LJ3'
})
// qwiic_pwr_res.res
const LR8 = board.add(R_0402_1005Metric, {
  translate: pt(0.689, 1.581), rotate: 0,
  id: 'LR8'
})
// qwiic_pull.scl_res.res
const LR9 = board.add(R_0402_1005Metric, {
  translate: pt(1.294, 1.205), rotate: 0,
  id: 'LR9'
})
// qwiic_pull.sda_res.res
const LR10 = board.add(R_0402_1005Metric, {
  translate: pt(1.294, 1.281), rotate: 0,
  id: 'LR10'
})
// tof.ic
const LU3 = board.add(ST_VL53L0X, {
  translate: pt(0.522, 1.244), rotate: 0,
  id: 'LU3'
})
// tof.vdd_cap[0].cap
const LC18 = board.add(C_0402_1005Metric, {
  translate: pt(0.634, 1.358), rotate: 0,
  id: 'LC18'
})
// tof.vdd_cap[1].cap
const LC19 = board.add(C_0805_2012Metric, {
  translate: pt(0.492, 1.378), rotate: 0,
  id: 'LC19'
})
// tof_pull.scl_res.res
const LR11 = board.add(R_0402_1005Metric, {
  translate: pt(1.486, 1.205), rotate: 0,
  id: 'LR11'
})
// tof_pull.sda_res.res
const LR12 = board.add(R_0402_1005Metric, {
  translate: pt(1.486, 1.281), rotate: 0,
  id: 'LR12'
})
// led_drv[0].ic
const LU4 = board.add(SOT_23_6, {
  translate: pt(1.771, 0.067), rotate: 0,
  id: 'LU4'
})
// led_drv[0].cap.cap
const LC20 = board.add(C_0402_1005Metric, {
  translate: pt(1.662, 0.365), rotate: 0,
  id: 'LC20'
})
// led_drv[0].boot_cap
const LC21 = board.add(C_0402_1005Metric, {
  translate: pt(1.773, 0.365), rotate: 0,
  id: 'LC21'
})
// led_drv[0].rsense.res.res
const LR13 = board.add(R_0603_1608Metric, {
  translate: pt(1.528, 0.376), rotate: 0,
  id: 'LR13'
})
// led_drv[0].power_path.inductor
const LL4 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(1.561, 0.089), rotate: 0,
  id: 'LL4'
})
// led_drv[0].power_path.in_cap.cap
const LC22 = board.add(C_0805_2012Metric, {
  translate: pt(1.757, 0.256), rotate: 0,
  id: 'LC22'
})
// led_drv[0].power_path.out_cap.cap
const LC23 = board.add(C_1206_3216Metric, {
  translate: pt(1.561, 0.263), rotate: 0,
  id: 'LC23'
})
// led_drv[1].ic
const LU5 = board.add(SOT_23_6, {
  translate: pt(0.301, 0.730), rotate: 0,
  id: 'LU5'
})
// led_drv[1].cap.cap
const LC24 = board.add(C_0402_1005Metric, {
  translate: pt(0.192, 1.029), rotate: 0,
  id: 'LC24'
})
// led_drv[1].boot_cap
const LC25 = board.add(C_0402_1005Metric, {
  translate: pt(0.303, 1.029), rotate: 0,
  id: 'LC25'
})
// led_drv[1].rsense.res.res
const LR14 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.039), rotate: 0,
  id: 'LR14'
})
// led_drv[1].power_path.inductor
const LL5 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(0.091, 0.752), rotate: 0,
  id: 'LL5'
})
// led_drv[1].power_path.in_cap.cap
const LC26 = board.add(C_0805_2012Metric, {
  translate: pt(0.287, 0.919), rotate: 0,
  id: 'LC26'
})
// led_drv[1].power_path.out_cap.cap
const LC27 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 0.926), rotate: 0,
  id: 'LC27'
})
// led_drv[2].ic
const LU6 = board.add(SOT_23_6, {
  translate: pt(0.801, 0.730), rotate: 0,
  id: 'LU6'
})
// led_drv[2].cap.cap
const LC28 = board.add(C_0402_1005Metric, {
  translate: pt(0.692, 1.029), rotate: 0,
  id: 'LC28'
})
// led_drv[2].boot_cap
const LC29 = board.add(C_0402_1005Metric, {
  translate: pt(0.803, 1.029), rotate: 0,
  id: 'LC29'
})
// led_drv[2].rsense.res.res
const LR15 = board.add(R_0603_1608Metric, {
  translate: pt(0.558, 1.039), rotate: 0,
  id: 'LR15'
})
// led_drv[2].power_path.inductor
const LL6 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(0.591, 0.752), rotate: 0,
  id: 'LL6'
})
// led_drv[2].power_path.in_cap.cap
const LC30 = board.add(C_0805_2012Metric, {
  translate: pt(0.787, 0.919), rotate: 0,
  id: 'LC30'
})
// led_drv[2].power_path.out_cap.cap
const LC31 = board.add(C_1206_3216Metric, {
  translate: pt(0.591, 0.926), rotate: 0,
  id: 'LC31'
})
// led_drv[3].ic
const LU7 = board.add(SOT_23_6, {
  translate: pt(1.301, 0.730), rotate: 0,
  id: 'LU7'
})
// led_drv[3].cap.cap
const LC32 = board.add(C_0402_1005Metric, {
  translate: pt(1.192, 1.029), rotate: 0,
  id: 'LC32'
})
// led_drv[3].boot_cap
const LC33 = board.add(C_0402_1005Metric, {
  translate: pt(1.303, 1.029), rotate: 0,
  id: 'LC33'
})
// led_drv[3].rsense.res.res
const LR16 = board.add(R_0603_1608Metric, {
  translate: pt(1.058, 1.039), rotate: 0,
  id: 'LR16'
})
// led_drv[3].power_path.inductor
const LL7 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(1.091, 0.752), rotate: 0,
  id: 'LL7'
})
// led_drv[3].power_path.in_cap.cap
const LC34 = board.add(C_0805_2012Metric, {
  translate: pt(1.287, 0.919), rotate: 0,
  id: 'LC34'
})
// led_drv[3].power_path.out_cap.cap
const LC35 = board.add(C_1206_3216Metric, {
  translate: pt(1.091, 0.926), rotate: 0,
  id: 'LC35'
})

board.setNetlist([
  {name: "Lgnd", pads: [["LJ1", "1"], ["LTP2", "1"], ["LU1", "1"], ["LD1", "2"], ["LU2", "33"], ["LR5", "2"], ["LJ3", "1"], ["LU3", "2"], ["LU3", "3"], ["LU3", "4"], ["LU3", "6"], ["LU3", "12"], ["LU4", "3"], ["LU5", "3"], ["LU6", "3"], ["LU7", "3"], ["LR7", "2"], ["LC1", "2"], ["LC5", "2"], ["LC6", "2"], ["LC7", "2"], ["LC8", "2"], ["LC9", "2"], ["LC10", "2"], ["LC13", "2"], ["LC14", "2"], ["LX1", "2"], ["LX1", "4"], ["LJ2", "5"], ["LC18", "2"], ["LC19", "2"], ["LC20", "2"], ["LC24", "2"], ["LC28", "2"], ["LC32", "2"], ["LR2", "2"], ["LC17", "2"], ["LC11", "2"], ["LC12", "2"], ["LC15", "2"], ["LC16", "2"], ["LC3", "2"], ["LC4", "2"], ["LR13", "1"], ["LC22", "2"], ["LC23", "2"], ["LR14", "1"], ["LC26", "2"], ["LC27", "2"], ["LR15", "1"], ["LC30", "2"], ["LC31", "2"], ["LR16", "1"], ["LC34", "2"], ["LC35", "2"]]},
  {name: "Lv12", pads: [["LJ1", "2"], ["LTP1", "1"], ["LU1", "3"], ["LU4", "4"], ["LU5", "4"], ["LU6", "4"], ["LU7", "4"], ["LR6", "1"], ["LR3", "1"], ["LC1", "1"], ["LC20", "1"], ["LC24", "1"], ["LC28", "1"], ["LC32", "1"], ["LC3", "1"], ["LC22", "1"], ["LC26", "1"], ["LC30", "1"], ["LC34", "1"]]},
  {name: "Lv3v3", pads: [["LTP3", "1"], ["LD1", "1"], ["LU2", "31"], ["LU2", "32"], ["LU2", "11"], ["LU2", "17"], ["LU2", "18"], ["LR8", "1"], ["LU3", "1"], ["LU3", "11"], ["LR1", "1"], ["LU2", "14"], ["LU2", "6"], ["LU3", "5"], ["LC5", "1"], ["LC6", "1"], ["LC7", "1"], ["LC8", "1"], ["LC9", "1"], ["LC10", "1"], ["LC13", "1"], ["LL3", "1"], ["LJ2", "1"], ["LR9", "1"], ["LR10", "1"], ["LC18", "1"], ["LC19", "1"], ["LR11", "1"], ["LR12", "1"], ["LR4", "1"], ["LL1", "2"], ["LC4", "1"]]},
  {name: "Lmcu.program_boot_node", pads: [["LD2", "2"], ["LU2", "15"], ["LJ2", "2"]]},
  {name: "Lv12_sense.output", pads: [["LU2", "4"], ["LR6", "2"], ["LR7", "1"]]},
  {name: "Lqwiic_pwr_res.pwr_out", pads: [["LR8", "2"], ["LJ3", "2"], ["LU2", "16"]]},
  {name: "Lqwiic_i2c.scl", pads: [["LU2", "25"], ["LR9", "2"], ["LJ3", "4"]]},
  {name: "Lqwiic_i2c.sda", pads: [["LU2", "26"], ["LJ3", "3"], ["LR10", "2"]]},
  {name: "Ltof_pull.i2c.scl", pads: [["LU2", "12"], ["LU3", "10"], ["LR11", "2"]]},
  {name: "Ltof_pull.i2c.sda", pads: [["LU2", "13"], ["LU3", "9"], ["LR12", "2"]]},
  {name: "Lled_drv[0].pwm", pads: [["LU2", "5"], ["LU4", "2"]]},
  {name: "Lled_drv[0].leda", pads: [["LL4", "2"], ["LC23", "1"]]},
  {name: "Lled_drv[0].ledk", pads: [["LR13", "2"], ["LU4", "1"]]},
  {name: "Lled_drv[1].pwm", pads: [["LU2", "8"], ["LU5", "2"]]},
  {name: "Lled_drv[1].leda", pads: [["LL5", "2"], ["LC27", "1"]]},
  {name: "Lled_drv[1].ledk", pads: [["LR14", "2"], ["LU5", "1"]]},
  {name: "Lled_drv[2].pwm", pads: [["LU2", "9"], ["LU6", "2"]]},
  {name: "Lled_drv[2].leda", pads: [["LL6", "2"], ["LC31", "1"]]},
  {name: "Lled_drv[2].ledk", pads: [["LR15", "2"], ["LU6", "1"]]},
  {name: "Lled_drv[3].pwm", pads: [["LU2", "10"], ["LU7", "2"]]},
  {name: "Lled_drv[3].leda", pads: [["LL7", "2"], ["LC35", "1"]]},
  {name: "Lled_drv[3].ledk", pads: [["LR16", "2"], ["LU7", "1"]]},
  {name: "Lreg_3v3.fb.output", pads: [["LU1", "4"], ["LR1", "2"], ["LR2", "1"]]},
  {name: "Lreg_3v3.boot_cap.neg", pads: [["LC2", "2"], ["LU1", "2"], ["LL1", "1"]]},
  {name: "Lreg_3v3.boot_cap.pos", pads: [["LC2", "1"], ["LU1", "6"]]},
  {name: "Lreg_3v3.en_res.b", pads: [["LR3", "2"], ["LU1", "5"]]},
  {name: "Lmcu.xtal_node.xi", pads: [["LU2", "30"], ["LX1", "1"], ["LC15", "1"]]},
  {name: "Lmcu.xtal_node.xo", pads: [["LU2", "29"], ["LX1", "3"], ["LC16", "1"]]},
  {name: "Lmcu.program_uart_node.a_tx", pads: [["LU2", "28"], ["LJ2", "3"]]},
  {name: "Lmcu.program_uart_node.b_tx", pads: [["LU2", "27"], ["LJ2", "4"]]},
  {name: "Lmcu.program_en_node", pads: [["LU2", "7"], ["LJ2", "6"], ["LR4", "2"], ["LC17", "1"]]},
  {name: "Lmcu.ic.lna_in", pads: [["LU2", "1"], ["LC11", "1"], ["LL2", "1"]]},
  {name: "Lmcu.pi.output", pads: [["LANT1", "1"], ["LL2", "2"], ["LC12", "1"]]},
  {name: "Lmcu.ic.vdd3p3", pads: [["LU2", "2"], ["LU2", "3"], ["LL3", "2"], ["LC14", "1"]]},
  {name: "Lledr.res.a", pads: [["LR5", "1"], ["LD2", "1"]]},
  {name: "Ltof.ic.gpio1", pads: [["LU3", "7"]]},
  {name: "Lled_drv[0].boot_cap.neg", pads: [["LC21", "2"], ["LU4", "5"], ["LL4", "1"]]},
  {name: "Lled_drv[0].boot_cap.pos", pads: [["LC21", "1"], ["LU4", "6"]]},
  {name: "Lled_drv[1].boot_cap.neg", pads: [["LC25", "2"], ["LU5", "5"], ["LL5", "1"]]},
  {name: "Lled_drv[1].boot_cap.pos", pads: [["LC25", "1"], ["LU5", "6"]]},
  {name: "Lled_drv[2].boot_cap.neg", pads: [["LC29", "2"], ["LU6", "5"], ["LL6", "1"]]},
  {name: "Lled_drv[2].boot_cap.pos", pads: [["LC29", "1"], ["LU6", "6"]]},
  {name: "Lled_drv[3].boot_cap.neg", pads: [["LC33", "2"], ["LU7", "5"], ["LL7", "1"]]},
  {name: "Lled_drv[3].boot_cap.pos", pads: [["LC33", "1"], ["LU7", "6"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.1411417322834647, 1.755511811023622);
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


