const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.098, 1.682), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.137, 1.682), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.098, 1.721), rotate: 0,
  id: 'H3'
})
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(2.034, 0.165), rotate: 0,
  id: 'J1'
})
// usb.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(1.883, 0.420), rotate: 0,
  id: 'R1'
})
// usb.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(2.039, 0.420), rotate: 0,
  id: 'R2'
})
// can.conn
const J2 = board.add(Molex_SL_171971_0005_1x05_P2_54mm_Vertical, {
  translate: pt(1.539, 0.973), rotate: 0,
  id: 'J2'
})
// tp_vusb.tp
const TP1 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.947, 1.735), rotate: 0,
  id: 'TP1'
})
// tp_gnd.tp
const TP2 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.085, 1.735), rotate: 0,
  id: 'TP2'
})
// reg_3v3.ic
const U1 = board.add(SOT_223_3_TabPin2, {
  translate: pt(0.173, 0.935), rotate: 0,
  id: 'U1'
})
// reg_3v3.in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(0.231, 1.145), rotate: 0,
  id: 'C1'
})
// reg_3v3.out_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 1.155), rotate: 0,
  id: 'C2'
})
// tp_3v3.tp
const TP3 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.659, 1.735), rotate: 0,
  id: 'TP3'
})
// prot_3v3.diode
const D1 = board.add(D_SOD_323, {
  translate: pt(1.213, 1.719), rotate: 0,
  id: 'D1'
})
// mcu.swd.conn
const J3 = board.add(Tag_Connect_TC2050_IDC_FP_2x05_P1_27mm_Vertical, {
  translate: pt(0.661, 0.167), rotate: 0,
  id: 'J3'
})
// mcu.ic
const U2 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'U2'
})
// mcu.pwr_cap[0].cap
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(0.272, 0.483), rotate: 0,
  id: 'C3'
})
// mcu.pwr_cap[1].cap
const C4 = board.add(C_0603_1608Metric, {
  translate: pt(0.436, 0.474), rotate: 0,
  id: 'C4'
})
// mcu.pwr_cap[2].cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(0.592, 0.474), rotate: 0,
  id: 'C5'
})
// mcu.pwr_cap[3].cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(0.748, 0.474), rotate: 0,
  id: 'C6'
})
// mcu.vdda_cap_0.cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.647), rotate: 0,
  id: 'C7'
})
// mcu.vdda_cap_1.cap
const C8 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 0.647), rotate: 0,
  id: 'C8'
})
// mcu.usb_pull.dp
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 0.647), rotate: 0,
  id: 'R3'
})
// mcu.crystal.package
const X1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(0.083, 0.512), rotate: 0,
  id: 'X1'
})
// mcu.crystal.cap_a
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.647), rotate: 0,
  id: 'C9'
})
// mcu.crystal.cap_b
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 0.647), rotate: 0,
  id: 'C10'
})
// sw1.package
const SW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(0.742, 1.424), rotate: 0,
  id: 'SW1'
})
// leds.led[0].package
const D2 = board.add(LED_0603_1608Metric, {
  translate: pt(2.233, 0.823), rotate: 0,
  id: 'D2'
})
// leds.led[1].package
const D3 = board.add(LED_0603_1608Metric, {
  translate: pt(2.389, 0.823), rotate: 0,
  id: 'D3'
})
// leds.led[2].package
const D4 = board.add(LED_0603_1608Metric, {
  translate: pt(2.233, 0.920), rotate: 0,
  id: 'D4'
})
// leds.led[3].package
const D5 = board.add(LED_0603_1608Metric, {
  translate: pt(2.389, 0.920), rotate: 0,
  id: 'D5'
})
// leds.led[4].package
const D6 = board.add(LED_0603_1608Metric, {
  translate: pt(2.233, 1.017), rotate: 0,
  id: 'D6'
})
// tof.elt[0].ic
const U3 = board.add(ST_VL53L0X, {
  translate: pt(1.063, 0.057), rotate: 0,
  id: 'U3'
})
// tof.elt[0].vdd_cap[0].cap
const C11 = board.add(C_0603_1608Metric, {
  translate: pt(1.025, 0.452), rotate: 0,
  id: 'C11'
})
// tof.elt[0].vdd_cap[1].cap
const C12 = board.add(C_0805_2012Metric, {
  translate: pt(1.498, 0.192), rotate: 0,
  id: 'C12'
})
// tof.elt[1].ic
const U4 = board.add(ST_VL53L0X, {
  translate: pt(1.295, 0.057), rotate: 0,
  id: 'U4'
})
// tof.elt[1].vdd_cap[0].cap
const C13 = board.add(C_0603_1608Metric, {
  translate: pt(1.181, 0.452), rotate: 0,
  id: 'C13'
})
// tof.elt[1].vdd_cap[1].cap
const C14 = board.add(C_0805_2012Metric, {
  translate: pt(1.033, 0.346), rotate: 0,
  id: 'C14'
})
// tof.elt[2].ic
const U5 = board.add(ST_VL53L0X, {
  translate: pt(1.528, 0.057), rotate: 0,
  id: 'U5'
})
// tof.elt[2].vdd_cap[0].cap
const C15 = board.add(C_0603_1608Metric, {
  translate: pt(1.337, 0.452), rotate: 0,
  id: 'C15'
})
// tof.elt[2].vdd_cap[1].cap
const C16 = board.add(C_0805_2012Metric, {
  translate: pt(1.207, 0.346), rotate: 0,
  id: 'C16'
})
// tof.elt[3].ic
const U6 = board.add(ST_VL53L0X, {
  translate: pt(1.063, 0.211), rotate: 0,
  id: 'U6'
})
// tof.elt[3].vdd_cap[0].cap
const C17 = board.add(C_0603_1608Metric, {
  translate: pt(1.493, 0.452), rotate: 0,
  id: 'C17'
})
// tof.elt[3].vdd_cap[1].cap
const C18 = board.add(C_0805_2012Metric, {
  translate: pt(1.380, 0.346), rotate: 0,
  id: 'C18'
})
// tof.elt[4].ic
const U7 = board.add(ST_VL53L0X, {
  translate: pt(1.295, 0.211), rotate: 0,
  id: 'U7'
})
// tof.elt[4].vdd_cap[0].cap
const C19 = board.add(C_0603_1608Metric, {
  translate: pt(1.648, 0.452), rotate: 0,
  id: 'C19'
})
// tof.elt[4].vdd_cap[1].cap
const C20 = board.add(C_0805_2012Metric, {
  translate: pt(1.553, 0.346), rotate: 0,
  id: 'C20'
})
// i2c_pull.scl_res.res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(1.710, 1.341), rotate: 0,
  id: 'R4'
})
// i2c_pull.sda_res.res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(1.710, 1.437), rotate: 0,
  id: 'R5'
})
// i2c_tp.tp_scl.tp
const TP4 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.085, 1.365), rotate: 0,
  id: 'TP4'
})
// i2c_tp.tp_sda.tp
const TP5 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.085, 1.511), rotate: 0,
  id: 'TP5'
})
// usb_esd
const U8 = board.add(SOT_23, {
  translate: pt(1.793, 1.749), rotate: 0,
  id: 'U8'
})
// tp_can.tp_txd.tp
const TP6 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.372, 1.365), rotate: 0,
  id: 'TP6'
})
// tp_can.tp_rxd.tp
const TP7 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.372, 1.511), rotate: 0,
  id: 'TP7'
})
// xcvr.ic
const U9 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.157, 0.900), rotate: 0,
  id: 'U9'
})
// xcvr.vdd_cap.cap
const C21 = board.add(C_0603_1608Metric, {
  translate: pt(1.069, 1.074), rotate: 0,
  id: 'C21'
})
// can_esd
const U10 = board.add(SOT_23, {
  translate: pt(1.983, 1.749), rotate: 0,
  id: 'U10'
})
// tp_spk.tp
const TP8 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.372, 1.735), rotate: 0,
  id: 'TP8'
})
// spk_dac.rc.r
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(1.476, 1.341), rotate: 0,
  id: 'R6'
})
// spk_dac.rc.c
const C22 = board.add(C_0603_1608Metric, {
  translate: pt(1.476, 1.437), rotate: 0,
  id: 'C22'
})
// tp_spk_in.tp
const TP9 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(2.172, 1.365), rotate: 0,
  id: 'TP9'
})
// spk_drv.ic
const U11 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(0.587, 0.863), rotate: 0,
  id: 'U11'
})
// spk_drv.pwr_cap.cap
const C23 = board.add(C_0603_1608Metric, {
  translate: pt(0.523, 1.000), rotate: 0,
  id: 'C23'
})
// spk_drv.bulk_cap.cap
const C24 = board.add(C_0805_2012Metric, {
  translate: pt(0.817, 0.832), rotate: 0,
  id: 'C24'
})
// spk_drv.inp_res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(0.679, 1.000), rotate: 0,
  id: 'R7'
})
// spk_drv.inp_cap
const C25 = board.add(C_0603_1608Metric, {
  translate: pt(0.835, 1.000), rotate: 0,
  id: 'C25'
})
// spk_drv.inn_res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(0.523, 1.096), rotate: 0,
  id: 'R8'
})
// spk_drv.inn_cap
const C26 = board.add(C_0603_1608Metric, {
  translate: pt(0.679, 1.096), rotate: 0,
  id: 'C26'
})
// spk.conn
const J4 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.124, 1.442), rotate: 0,
  id: 'J4'
})
// res1
const RN1 = board.add(R_Array_Concave_4x0603, {
  translate: pt(1.455, 1.756), rotate: 0,
  id: 'RN1'
})
// res2
const RN2 = board.add(R_Array_Concave_4x0603, {
  translate: pt(1.617, 1.756), rotate: 0,
  id: 'RN2'
})
// rgb.device.package
const D7 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(1.928, 1.367), rotate: 0,
  id: 'D7'
})

board.setNetlist([
  {name: "vusb", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["TP1", "1"], ["U1", "3"], ["U11", "1"], ["U11", "6"], ["C1", "1"], ["C23", "1"], ["C24", "1"]]},
  {name: "gnd", pads: [["U8", "3"], ["U10", "3"], ["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["J2", "3"], ["TP2", "1"], ["U1", "1"], ["D1", "2"], ["U2", "8"], ["U2", "23"], ["U2", "35"], ["U2", "47"], ["U2", "44"], ["SW1", "2"], ["U9", "2"], ["U9", "8"], ["U11", "7"], ["U11", "9"], ["C22", "2"], ["J1", "S1"], ["C26", "2"], ["C1", "2"], ["C2", "2"], ["C3", "2"], ["C4", "2"], ["C5", "2"], ["C6", "2"], ["C7", "2"], ["C8", "2"], ["X1", "2"], ["X1", "4"], ["U3", "2"], ["U3", "3"], ["U3", "4"], ["U3", "6"], ["U3", "12"], ["U4", "2"], ["U4", "3"], ["U4", "4"], ["U4", "6"], ["U4", "12"], ["U5", "2"], ["U5", "3"], ["U5", "4"], ["U5", "6"], ["U5", "12"], ["U6", "2"], ["U6", "3"], ["U6", "4"], ["U6", "6"], ["U6", "12"], ["U7", "2"], ["U7", "3"], ["U7", "4"], ["U7", "6"], ["U7", "12"], ["C21", "2"], ["C23", "2"], ["C24", "2"], ["R1", "1"], ["R2", "1"], ["J3", "2"], ["J3", "3"], ["J3", "5"], ["C9", "2"], ["C10", "2"], ["C11", "2"], ["C12", "2"], ["C13", "2"], ["C14", "2"], ["C15", "2"], ["C16", "2"], ["C17", "2"], ["C18", "2"], ["C19", "2"], ["C20", "2"]]},
  {name: "v3v3", pads: [["U1", "2"], ["TP3", "1"], ["D1", "1"], ["U2", "1"], ["U2", "9"], ["U2", "24"], ["U2", "36"], ["U2", "48"], ["U9", "3"], ["C2", "1"], ["J3", "1"], ["C3", "1"], ["C4", "1"], ["C5", "1"], ["C6", "1"], ["C7", "1"], ["C8", "1"], ["R3", "1"], ["D2", "2"], ["D3", "2"], ["D4", "2"], ["D5", "2"], ["D6", "2"], ["U3", "1"], ["U3", "11"], ["U4", "1"], ["U4", "11"], ["U5", "1"], ["U5", "11"], ["U6", "1"], ["U6", "11"], ["U7", "1"], ["U7", "11"], ["R4", "1"], ["R5", "1"], ["C21", "1"], ["D7", "2"], ["C11", "1"], ["C12", "1"], ["C13", "1"], ["C14", "1"], ["C15", "1"], ["C16", "1"], ["C17", "1"], ["C18", "1"], ["C19", "1"], ["C20", "1"]]},
  {name: "sw1_chain_0", pads: [["U2", "19"], ["SW1", "1"]]},
  {name: "leds_chain_0.0", pads: [["U2", "20"], ["RN1", "8"]]},
  {name: "leds_chain_0.1", pads: [["U2", "25"], ["RN1", "7"]]},
  {name: "leds_chain_0.2", pads: [["U2", "29"], ["RN2", "7"]]},
  {name: "leds_chain_0.3", pads: [["U2", "30"], ["RN2", "6"]]},
  {name: "leds_chain_0.4", pads: [["U2", "31"], ["RN2", "5"]]},
  {name: "leds_chain_0.5", pads: [["U2", "26"], ["RN1", "6"]]},
  {name: "leds_chain_0.6", pads: [["U2", "27"], ["RN1", "5"]]},
  {name: "leds_chain_0.7", pads: [["U2", "28"], ["RN2", "8"]]},
  {name: "i2c_chain_0.scl", pads: [["U2", "21"], ["R4", "2"], ["TP4", "1"], ["U3", "10"], ["U4", "10"], ["U5", "10"], ["U6", "10"], ["U7", "10"]]},
  {name: "i2c_chain_0.sda", pads: [["U2", "22"], ["R5", "2"], ["U3", "9"], ["U4", "9"], ["U5", "9"], ["U6", "9"], ["U7", "9"], ["TP5", "1"]]},
  {name: "mcu.gpio.tof_reset_0", pads: [["U2", "42"], ["U3", "5"]]},
  {name: "mcu.gpio.tof_reset_1", pads: [["U2", "41"], ["U4", "5"]]},
  {name: "mcu.gpio.tof_reset_2", pads: [["U2", "4"], ["U5", "5"]]},
  {name: "mcu.gpio.tof_reset_3", pads: [["U2", "3"], ["U6", "5"]]},
  {name: "mcu.gpio.tof_reset_4", pads: [["U2", "2"], ["U7", "5"]]},
  {name: "usb_chain_0.d_P", pads: [["J1", "A6"], ["J1", "B6"], ["U8", "2"], ["U2", "33"], ["R3", "2"]]},
  {name: "usb_chain_0.d_N", pads: [["J1", "A7"], ["J1", "B7"], ["U8", "1"], ["U2", "32"]]},
  {name: "can_chain_0.txd", pads: [["U2", "46"], ["U9", "1"], ["TP6", "1"]]},
  {name: "can_chain_0.rxd", pads: [["U2", "45"], ["U9", "4"], ["TP7", "1"]]},
  {name: "can_chain_1.canh", pads: [["U9", "7"], ["U10", "2"], ["J2", "4"]]},
  {name: "can_chain_1.canl", pads: [["U9", "6"], ["U10", "1"], ["J2", "5"]]},
  {name: "spk_chain_0", pads: [["U2", "11"], ["TP8", "1"], ["R6", "1"]]},
  {name: "spk_chain_1", pads: [["TP9", "1"], ["C25", "2"], ["R6", "2"], ["C22", "1"]]},
  {name: "spk_chain_2.a", pads: [["U11", "8"], ["J4", "1"]]},
  {name: "spk_chain_2.b", pads: [["U11", "5"], ["J4", "2"]]},
  {name: "res1.a.0", pads: [["RN1", "1"], ["D2", "1"]]},
  {name: "res1.a.1", pads: [["RN1", "2"], ["D3", "1"]]},
  {name: "res1.a.2", pads: [["RN1", "3"], ["D7", "3"]]},
  {name: "res1.a.3", pads: [["RN1", "4"], ["D7", "4"]]},
  {name: "res2.a.0", pads: [["RN2", "1"], ["D7", "1"]]},
  {name: "res2.a.1", pads: [["RN2", "2"], ["D4", "1"]]},
  {name: "res2.a.2", pads: [["RN2", "3"], ["D5", "1"]]},
  {name: "res2.a.3", pads: [["RN2", "4"], ["D6", "1"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "can.pwr", pads: [["J2", "2"]]},
  {name: "mcu.xtal_node.xi", pads: [["U2", "5"], ["X1", "1"], ["C9", "1"]]},
  {name: "mcu.xtal_node.xo", pads: [["U2", "6"], ["X1", "3"], ["C10", "1"]]},
  {name: "mcu.swd_node.swdio", pads: [["U2", "34"], ["J3", "10"]]},
  {name: "mcu.swd_node.swclk", pads: [["U2", "37"], ["J3", "9"]]},
  {name: "mcu.reset_node", pads: [["U2", "7"], ["J3", "6"]]},
  {name: "mcu.swd.swo", pads: [["U2", "39"], ["J3", "8"]]},
  {name: "mcu.swd.tdi", pads: [["J3", "7"]]},
  {name: "tof.elt[0].ic.gpio1", pads: [["U3", "7"]]},
  {name: "tof.elt[1].ic.gpio1", pads: [["U4", "7"]]},
  {name: "tof.elt[2].ic.gpio1", pads: [["U5", "7"]]},
  {name: "tof.elt[3].ic.gpio1", pads: [["U6", "7"]]},
  {name: "tof.elt[4].ic.gpio1", pads: [["U7", "7"]]},
  {name: "spk_drv.inp_cap.pos", pads: [["C25", "1"], ["R7", "1"]]},
  {name: "spk_drv.inp_res.b", pads: [["R7", "2"], ["U11", "4"]]},
  {name: "spk_drv.inn_cap.pos", pads: [["C26", "1"], ["R8", "1"]]},
  {name: "spk_drv.inn_res.b", pads: [["R8", "2"], ["U11", "3"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.565748031496063, 1.9062992125984253);
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


