const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.195, 1.634), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.234, 1.634), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.195, 1.673), rotate: 0,
  id: 'H3'
})
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 0.958), rotate: 0,
  id: 'J1'
})
// usb.esd
const U1 = board.add(SOT_23, {
  translate: pt(0.534, 0.861), rotate: 0,
  id: 'U1'
})
// usb.cc_pull.cc1
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.517, 0.996), rotate: 0,
  id: 'R1'
})
// usb.cc_pull.cc2
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(0.517, 1.093), rotate: 0,
  id: 'R2'
})
// can.conn
const J2 = board.add(Molex_SL_171971_0005_1x05_P2_54mm_Vertical, {
  translate: pt(1.802, 0.973), rotate: 0,
  id: 'J2'
})
// tp_vusb.tp
const TP1 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.085, 1.687), rotate: 0,
  id: 'TP1'
})
// tp_gnd.tp
const TP2 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.372, 1.687), rotate: 0,
  id: 'TP2'
})
// reg_3v3.ic
const U2 = board.add(SOT_223_3_TabPin2, {
  translate: pt(1.956, 0.142), rotate: 0,
  id: 'U2'
})
// reg_3v3.in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(2.014, 0.352), rotate: 0,
  id: 'C1'
})
// reg_3v3.out_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(1.850, 0.361), rotate: 0,
  id: 'C2'
})
// tp_3v3.tp
const TP3 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.659, 1.687), rotate: 0,
  id: 'TP3'
})
// prot_3v3.diode
const D1 = board.add(D_SOD_323, {
  translate: pt(1.500, 1.671), rotate: 0,
  id: 'D1'
})
// mcu.ic
const U3 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'U3'
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
// mcu.crystal.package
const X1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(0.083, 0.512), rotate: 0,
  id: 'X1'
})
// mcu.crystal.cap_a
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.647), rotate: 0,
  id: 'C9'
})
// mcu.crystal.cap_b
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.647), rotate: 0,
  id: 'C10'
})
// mcu.swd.conn
const J3 = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(0.612, 0.167), rotate: 0,
  id: 'J3'
})
// mcu.usb_pull.dp
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(0.682, 0.647), rotate: 0,
  id: 'R3'
})
// sw1.package
const SW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.133, 1.376), rotate: 0,
  id: 'SW1'
})
// leds.led[0].package
const D2 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 1.292), rotate: 0,
  id: 'D2'
})
// leds.led[1].package
const D3 = board.add(LED_0603_1608Metric, {
  translate: pt(0.215, 1.292), rotate: 0,
  id: 'D3'
})
// leds.led[2].package
const D4 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 1.390), rotate: 0,
  id: 'D4'
})
// leds.led[3].package
const D5 = board.add(LED_0603_1608Metric, {
  translate: pt(0.215, 1.390), rotate: 0,
  id: 'D5'
})
// leds.led[4].package
const D6 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 1.487), rotate: 0,
  id: 'D6'
})
// tof.elt[0].ic
const U4 = board.add(ST_VL53L0X, {
  translate: pt(1.021, 0.057), rotate: 0,
  id: 'U4'
})
// tof.elt[0].vdd_cap[0].cap
const C11 = board.add(C_0603_1608Metric, {
  translate: pt(0.983, 0.452), rotate: 0,
  id: 'C11'
})
// tof.elt[0].vdd_cap[1].cap
const C12 = board.add(C_0805_2012Metric, {
  translate: pt(1.456, 0.192), rotate: 0,
  id: 'C12'
})
// tof.elt[1].ic
const U5 = board.add(ST_VL53L0X, {
  translate: pt(1.253, 0.057), rotate: 0,
  id: 'U5'
})
// tof.elt[1].vdd_cap[0].cap
const C13 = board.add(C_0603_1608Metric, {
  translate: pt(1.139, 0.452), rotate: 0,
  id: 'C13'
})
// tof.elt[1].vdd_cap[1].cap
const C14 = board.add(C_0805_2012Metric, {
  translate: pt(0.991, 0.346), rotate: 0,
  id: 'C14'
})
// tof.elt[2].ic
const U6 = board.add(ST_VL53L0X, {
  translate: pt(1.485, 0.057), rotate: 0,
  id: 'U6'
})
// tof.elt[2].vdd_cap[0].cap
const C15 = board.add(C_0603_1608Metric, {
  translate: pt(1.294, 0.452), rotate: 0,
  id: 'C15'
})
// tof.elt[2].vdd_cap[1].cap
const C16 = board.add(C_0805_2012Metric, {
  translate: pt(1.165, 0.346), rotate: 0,
  id: 'C16'
})
// tof.elt[3].ic
const U7 = board.add(ST_VL53L0X, {
  translate: pt(1.021, 0.211), rotate: 0,
  id: 'U7'
})
// tof.elt[3].vdd_cap[0].cap
const C17 = board.add(C_0603_1608Metric, {
  translate: pt(1.450, 0.452), rotate: 0,
  id: 'C17'
})
// tof.elt[3].vdd_cap[1].cap
const C18 = board.add(C_0805_2012Metric, {
  translate: pt(1.338, 0.346), rotate: 0,
  id: 'C18'
})
// tof.elt[4].ic
const U8 = board.add(ST_VL53L0X, {
  translate: pt(1.253, 0.211), rotate: 0,
  id: 'U8'
})
// tof.elt[4].vdd_cap[0].cap
const C19 = board.add(C_0603_1608Metric, {
  translate: pt(1.606, 0.452), rotate: 0,
  id: 'C19'
})
// tof.elt[4].vdd_cap[1].cap
const C20 = board.add(C_0805_2012Metric, {
  translate: pt(1.511, 0.346), rotate: 0,
  id: 'C20'
})
// i2c_pull.scl_res.res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(1.867, 1.292), rotate: 0,
  id: 'R4'
})
// i2c_pull.sda_res.res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(1.867, 1.389), rotate: 0,
  id: 'R5'
})
// i2c_tp.tp_scl.tp
const TP4 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.476, 1.317), rotate: 0,
  id: 'TP4'
})
// i2c_tp.tp_sda.tp
const TP5 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.476, 1.462), rotate: 0,
  id: 'TP5'
})
// tp_can.tp_txd.tp
const TP6 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.763, 1.317), rotate: 0,
  id: 'TP6'
})
// tp_can.tp_rxd.tp
const TP7 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.763, 1.462), rotate: 0,
  id: 'TP7'
})
// xcvr.ic
const U9 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.420, 0.900), rotate: 0,
  id: 'U9'
})
// xcvr.vdd_cap.cap
const C21 = board.add(C_0603_1608Metric, {
  translate: pt(1.332, 1.074), rotate: 0,
  id: 'C21'
})
// can_esd
const U10 = board.add(SOT_23, {
  translate: pt(2.080, 1.701), rotate: 0,
  id: 'U10'
})
// tp_spk.tp
const TP8 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.947, 1.687), rotate: 0,
  id: 'TP8'
})
// spk_dac.rc.r
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(2.101, 1.292), rotate: 0,
  id: 'R6'
})
// spk_dac.rc.c
const C22 = board.add(C_0603_1608Metric, {
  translate: pt(2.101, 1.389), rotate: 0,
  id: 'C22'
})
// tp_spk_in.tp
const TP9 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(1.234, 1.687), rotate: 0,
  id: 'TP9'
})
// spk_drv.ic
const U11 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(0.850, 0.863), rotate: 0,
  id: 'U11'
})
// spk_drv.pwr_cap.cap
const C23 = board.add(C_0603_1608Metric, {
  translate: pt(0.786, 1.000), rotate: 0,
  id: 'C23'
})
// spk_drv.bulk_cap.cap
const C24 = board.add(C_0805_2012Metric, {
  translate: pt(1.080, 0.832), rotate: 0,
  id: 'C24'
})
// spk_drv.inp_res.res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(0.942, 1.000), rotate: 0,
  id: 'R7'
})
// spk_drv.inp_cap.cap
const C25 = board.add(C_0603_1608Metric, {
  translate: pt(1.098, 1.000), rotate: 0,
  id: 'C25'
})
// spk_drv.inn_res.res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(0.786, 1.096), rotate: 0,
  id: 'R8'
})
// spk_drv.inn_cap.cap
const C26 = board.add(C_0603_1608Metric, {
  translate: pt(0.942, 1.096), rotate: 0,
  id: 'C26'
})
// spk.conn
const J4 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.515, 1.393), rotate: 0,
  id: 'J4'
})
// res1
const RN1 = board.add(R_Array_Concave_4x0603, {
  translate: pt(1.743, 1.707), rotate: 0,
  id: 'RN1'
})
// res2
const RN2 = board.add(R_Array_Concave_4x0603, {
  translate: pt(1.904, 1.707), rotate: 0,
  id: 'RN2'
})
// rgb.device.package
const D7 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(2.319, 1.319), rotate: 0,
  id: 'D7'
})

board.setNetlist([
  {name: "vusb", pads: [["J1", "A4"], ["J1", "A9"], ["J1", "B4"], ["J1", "B9"], ["TP1", "1"], ["U2", "3"], ["C1", "1"], ["U11", "1"], ["U11", "6"], ["C23", "1"], ["C24", "1"]]},
  {name: "gnd", pads: [["J1", "A1"], ["J1", "A12"], ["J1", "B1"], ["J1", "B12"], ["J1", "S1"], ["U1", "3"], ["R1", "1"], ["R2", "1"], ["J2", "3"], ["TP2", "1"], ["U2", "1"], ["C1", "2"], ["C2", "2"], ["D1", "2"], ["U3", "23"], ["U3", "35"], ["U3", "44"], ["U3", "47"], ["U3", "8"], ["C3", "2"], ["C4", "2"], ["C5", "2"], ["C6", "2"], ["C7", "2"], ["C8", "2"], ["X1", "2"], ["X1", "4"], ["C9", "2"], ["C10", "2"], ["J3", "5"], ["SW1", "2"], ["U4", "12"], ["U4", "2"], ["U4", "3"], ["U4", "4"], ["U4", "6"], ["C11", "2"], ["C12", "2"], ["U5", "12"], ["U5", "2"], ["U5", "3"], ["U5", "4"], ["U5", "6"], ["C13", "2"], ["C14", "2"], ["U6", "12"], ["U6", "2"], ["U6", "3"], ["U6", "4"], ["U6", "6"], ["C15", "2"], ["C16", "2"], ["U7", "12"], ["U7", "2"], ["U7", "3"], ["U7", "4"], ["U7", "6"], ["C17", "2"], ["C18", "2"], ["U8", "12"], ["U8", "2"], ["U8", "3"], ["U8", "4"], ["U8", "6"], ["C19", "2"], ["C20", "2"], ["U9", "2"], ["U9", "8"], ["C21", "2"], ["U10", "3"], ["C22", "2"], ["U11", "7"], ["U11", "9"], ["C23", "2"], ["C24", "2"], ["C26", "2"]]},
  {name: "v3v3", pads: [["U2", "2"], ["C2", "1"], ["TP3", "1"], ["D1", "1"], ["U3", "1"], ["U3", "24"], ["U3", "36"], ["U3", "48"], ["U3", "9"], ["C3", "1"], ["C4", "1"], ["C5", "1"], ["C6", "1"], ["C7", "1"], ["C8", "1"], ["J3", "1"], ["R3", "1"], ["D2", "2"], ["D3", "2"], ["D4", "2"], ["D5", "2"], ["D6", "2"], ["U4", "1"], ["U4", "11"], ["C11", "1"], ["C12", "1"], ["U5", "1"], ["U5", "11"], ["C13", "1"], ["C14", "1"], ["U6", "1"], ["U6", "11"], ["C15", "1"], ["C16", "1"], ["U7", "1"], ["U7", "11"], ["C17", "1"], ["C18", "1"], ["U8", "1"], ["U8", "11"], ["C19", "1"], ["C20", "1"], ["R4", "1"], ["R5", "1"], ["U9", "3"], ["C21", "1"], ["D7", "2"]]},
  {name: "sw1_chain_0", pads: [["U3", "19"], ["SW1", "1"]]},
  {name: "leds_chain_0.0", pads: [["U3", "20"], ["RN1", "8"]]},
  {name: "leds_chain_0.1", pads: [["U3", "25"], ["RN1", "7"]]},
  {name: "leds_chain_0.2", pads: [["U3", "29"], ["RN2", "7"]]},
  {name: "leds_chain_0.3", pads: [["U3", "30"], ["RN2", "6"]]},
  {name: "leds_chain_0.4", pads: [["U3", "31"], ["RN2", "5"]]},
  {name: "leds_chain_0.5", pads: [["U3", "26"], ["RN1", "6"]]},
  {name: "leds_chain_0.6", pads: [["U3", "27"], ["RN1", "5"]]},
  {name: "leds_chain_0.7", pads: [["U3", "28"], ["RN2", "8"]]},
  {name: "i2c_chain_0.scl", pads: [["U3", "21"], ["U4", "10"], ["U5", "10"], ["U6", "10"], ["U7", "10"], ["U8", "10"], ["R4", "2"], ["TP4", "1"]]},
  {name: "i2c_chain_0.sda", pads: [["U3", "22"], ["U4", "9"], ["U5", "9"], ["U6", "9"], ["U7", "9"], ["U8", "9"], ["R5", "2"], ["TP5", "1"]]},
  {name: "can_chain_0.txd", pads: [["U3", "46"], ["TP6", "1"], ["U9", "1"]]},
  {name: "can_chain_0.rxd", pads: [["U3", "45"], ["TP7", "1"], ["U9", "4"]]},
  {name: "can_chain_1.canh", pads: [["J2", "4"], ["U9", "7"], ["U10", "2"]]},
  {name: "can_chain_1.canl", pads: [["J2", "5"], ["U9", "6"], ["U10", "1"]]},
  {name: "spk_chain_0", pads: [["U3", "11"], ["TP8", "1"], ["R6", "1"]]},
  {name: "spk_chain_1", pads: [["R6", "2"], ["C22", "1"], ["TP9", "1"], ["C25", "2"]]},
  {name: "spk_chain_2.a", pads: [["U11", "8"], ["J4", "1"]]},
  {name: "spk_chain_2.b", pads: [["U11", "5"], ["J4", "2"]]},
  {name: "usb.usb.dp", pads: [["J1", "A6"], ["J1", "B6"], ["U1", "2"], ["U3", "33"], ["R3", "2"]]},
  {name: "usb.usb.dm", pads: [["J1", "A7"], ["J1", "B7"], ["U1", "1"], ["U3", "32"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "can.pwr", pads: [["J2", "2"]]},
  {name: "mcu.gpio.tof_reset_0", pads: [["U3", "42"], ["U4", "5"]]},
  {name: "mcu.gpio.tof_reset_1", pads: [["U3", "41"], ["U5", "5"]]},
  {name: "mcu.gpio.tof_reset_2", pads: [["U3", "4"], ["U6", "5"]]},
  {name: "mcu.gpio.tof_reset_3", pads: [["U3", "3"], ["U7", "5"]]},
  {name: "mcu.gpio.tof_reset_4", pads: [["U3", "2"], ["U8", "5"]]},
  {name: "mcu.xtal_node.xi", pads: [["U3", "5"], ["X1", "1"], ["C9", "1"]]},
  {name: "mcu.xtal_node.xo", pads: [["U3", "6"], ["X1", "3"], ["C10", "1"]]},
  {name: "mcu.swd_node.swdio", pads: [["U3", "34"], ["J3", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["U3", "37"], ["J3", "4"]]},
  {name: "mcu.reset_node", pads: [["U3", "7"], ["J3", "3"]]},
  {name: "mcu.swd.swo", pads: [["U3", "39"], ["J3", "6"]]},
  {name: "tof.elt[0].ic.gpio1", pads: [["U4", "7"]]},
  {name: "tof.elt[1].ic.gpio1", pads: [["U5", "7"]]},
  {name: "tof.elt[2].ic.gpio1", pads: [["U6", "7"]]},
  {name: "tof.elt[3].ic.gpio1", pads: [["U7", "7"]]},
  {name: "tof.elt[4].ic.gpio1", pads: [["U8", "7"]]},
  {name: "spk_drv.ic.inp", pads: [["U11", "4"], ["R7", "2"]]},
  {name: "spk_drv.ic.inn", pads: [["U11", "3"], ["R8", "2"]]},
  {name: "spk_drv.inp_res.input", pads: [["R7", "1"], ["C25", "1"]]},
  {name: "spk_drv.inn_res.input", pads: [["R8", "1"], ["C26", "1"]]},
  {name: "res1.a.0", pads: [["D2", "1"], ["RN1", "1"]]},
  {name: "res1.a.1", pads: [["D3", "1"], ["RN1", "2"]]},
  {name: "res1.a.2", pads: [["RN1", "3"], ["D7", "3"]]},
  {name: "res1.a.3", pads: [["RN1", "4"], ["D7", "4"]]},
  {name: "res2.a.0", pads: [["RN2", "1"], ["D7", "1"]]},
  {name: "res2.a.1", pads: [["D4", "1"], ["RN2", "2"]]},
  {name: "res2.a.2", pads: [["D5", "1"], ["RN2", "3"]]},
  {name: "res2.a.3", pads: [["D6", "1"], ["RN2", "4"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.4783464566929134, 1.8582677165354333);
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


