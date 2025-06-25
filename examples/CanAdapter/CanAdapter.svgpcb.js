const board = new PCB();

// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 1.055), rotate: 0,
  id: 'J1'
})
// usb.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.310), rotate: 0,
  id: 'R1'
})
// usb.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 1.310), rotate: 0,
  id: 'R2'
})
// usb_reg.ic
const U1 = board.add(SOT_23_5, {
  translate: pt(1.133, 0.957), rotate: 0,
  id: 'U1'
})
// usb_reg.in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(1.284, 1.093), rotate: 0,
  id: 'C1'
})
// usb_reg.out_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(1.120, 1.102), rotate: 0,
  id: 'C2'
})
// mcu.swd.conn
const J2 = board.add(Tag_Connect_TC2050_IDC_NL_2x05_P1_27mm_Vertical, {
  translate: pt(0.690, 0.133), rotate: 0,
  id: 'J2'
})
// mcu.ic
const U2 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'U2'
})
// mcu.swd_pull.swdio.res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(0.609, 0.474), rotate: 0,
  id: 'R3'
})
// mcu.swd_pull.swclk.res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(0.765, 0.474), rotate: 0,
  id: 'R4'
})
// mcu.pwr_cap[0].cap
const C3 = board.add(C_0603_1608Metric, {
  translate: pt(0.921, 0.474), rotate: 0,
  id: 'C3'
})
// mcu.pwr_cap[1].cap
const C4 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.647), rotate: 0,
  id: 'C4'
})
// mcu.pwr_cap[2].cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 0.647), rotate: 0,
  id: 'C5'
})
// mcu.pwr_cap[3].cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.647), rotate: 0,
  id: 'C6'
})
// mcu.pwr_cap[4].cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.647), rotate: 0,
  id: 'C7'
})
// mcu.pwr_cap[5].cap
const C8 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 0.647), rotate: 0,
  id: 'C8'
})
// mcu.vbat_cap.cap
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 0.647), rotate: 0,
  id: 'C9'
})
// mcu.pwra_cap[0].cap
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.744), rotate: 0,
  id: 'C10'
})
// mcu.pwra_cap[1].cap
const C11 = board.add(C_0805_2012Metric, {
  translate: pt(0.272, 0.483), rotate: 0,
  id: 'C11'
})
// mcu.vref_cap[0].cap
const C12 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 0.744), rotate: 0,
  id: 'C12'
})
// mcu.vref_cap[1].cap
const C13 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.744), rotate: 0,
  id: 'C13'
})
// mcu.vref_cap[2].cap
const C14 = board.add(C_0805_2012Metric, {
  translate: pt(0.445, 0.483), rotate: 0,
  id: 'C14'
})
// mcu.crystal.package
const X1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(0.083, 0.512), rotate: 0,
  id: 'X1'
})
// mcu.crystal.cap_a
const C15 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.744), rotate: 0,
  id: 'C15'
})
// mcu.crystal.cap_b
const C16 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 0.744), rotate: 0,
  id: 'C16'
})
// usb_esd
const U3 = board.add(SOT_23, {
  translate: pt(1.761, 1.524), rotate: 0,
  id: 'U3'
})
// xcvr.ic
const U4 = board.add(SOP_8_6_62x9_15mm_P2_54mm, {
  translate: pt(1.332, 0.190), rotate: 0,
  id: 'U4'
})
// xcvr.logic_cap.cap
const C17 = board.add(C_0603_1608Metric, {
  translate: pt(1.156, 0.448), rotate: 0,
  id: 'C17'
})
// xcvr.can_cap.cap
const C18 = board.add(C_0603_1608Metric, {
  translate: pt(1.312, 0.448), rotate: 0,
  id: 'C18'
})
// sw_usb.package
const SW1 = board.add(SW_SPST_EVQP7C, {
  translate: pt(0.889, 1.550), rotate: 0,
  id: 'SW1'
})
// sw_can.package
const SW2 = board.add(SW_SPST_EVQP7C, {
  translate: pt(1.224, 1.550), rotate: 0,
  id: 'SW2'
})
// lcd.device.conn
const J3 = board.add(Hirose_FH12_8S_0_5SH_1x08_1MP_P0_50mm_Horizontal, {
  translate: pt(0.736, 1.083), rotate: 0,
  id: 'J3'
})
// lcd.led_res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(0.595, 1.270), rotate: 0,
  id: 'R5'
})
// lcd.vdd_cap.cap
const C19 = board.add(C_0603_1608Metric, {
  translate: pt(0.751, 1.270), rotate: 0,
  id: 'C19'
})
// rgb_usb.package
const D1 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(0.041, 1.512), rotate: 0,
  id: 'D1'
})
// rgb_usb.red_res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(0.180, 1.486), rotate: 0,
  id: 'R6'
})
// rgb_usb.green_res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.635), rotate: 0,
  id: 'R7'
})
// rgb_usb.blue_res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 1.635), rotate: 0,
  id: 'R8'
})
// rgb_can.package
const D2 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(0.432, 1.512), rotate: 0,
  id: 'D2'
})
// rgb_can.red_res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(0.571, 1.486), rotate: 0,
  id: 'R9'
})
// rgb_can.green_res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(0.449, 1.635), rotate: 0,
  id: 'R10'
})
// rgb_can.blue_res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(0.605, 1.635), rotate: 0,
  id: 'R11'
})
// can
const J4 = board.add(Molex_DuraClik_502352_1x05_P2_00mm_Horizontal, {
  translate: pt(2.066, 1.457), rotate: 0,
  id: 'J4'
})
// can_reg.ic
const U5 = board.add(SOT_23_5, {
  translate: pt(1.541, 0.957), rotate: 0,
  id: 'U5'
})
// can_reg.in_cap.cap
const C20 = board.add(C_0603_1608Metric, {
  translate: pt(1.692, 1.093), rotate: 0,
  id: 'C20'
})
// can_reg.out_cap.cap
const C21 = board.add(C_0805_2012Metric, {
  translate: pt(1.528, 1.102), rotate: 0,
  id: 'C21'
})
// led_can.package
const D3 = board.add(LED_0603_1608Metric, {
  translate: pt(1.509, 1.486), rotate: 0,
  id: 'D3'
})
// led_can.res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(1.509, 1.583), rotate: 0,
  id: 'R12'
})
// can_esd
const U6 = board.add(SOT_23, {
  translate: pt(1.951, 1.524), rotate: 0,
  id: 'U6'
})

board.setNetlist([
  {name: "vusb", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["U1", "1"], ["U1", "3"], ["C1", "1"]]},
  {name: "gnd", pads: [["U3", "3"], ["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["U1", "2"], ["U2", "17"], ["U2", "11"], ["U2", "20"], ["U2", "40"], ["U2", "41"], ["U4", "4"], ["SW1", "2"], ["SW2", "2"], ["J1", "S1"], ["C1", "2"], ["C2", "2"], ["C3", "2"], ["C4", "2"], ["C5", "2"], ["C6", "2"], ["C7", "2"], ["C8", "2"], ["C9", "2"], ["C10", "2"], ["C11", "2"], ["C12", "2"], ["C13", "2"], ["C14", "2"], ["X1", "2"], ["X1", "4"], ["C17", "2"], ["J3", "2"], ["C19", "2"], ["R4", "1"], ["R1", "1"], ["R2", "1"], ["J2", "2"], ["J2", "3"], ["J2", "5"], ["C15", "2"], ["C16", "2"]]},
  {name: "v3v3", pads: [["U1", "5"], ["U2", "16"], ["U2", "10"], ["U2", "14"], ["U2", "30"], ["U2", "27"], ["U2", "39"], ["U2", "42"], ["U4", "1"], ["D1", "2"], ["D2", "2"], ["C2", "1"], ["J2", "1"], ["C3", "1"], ["C4", "1"], ["C5", "1"], ["C6", "1"], ["C7", "1"], ["C8", "1"], ["C9", "1"], ["C10", "1"], ["C11", "1"], ["C12", "1"], ["C13", "1"], ["C14", "1"], ["C17", "1"], ["J3", "7"], ["C19", "1"], ["R3", "1"]]},
  {name: "can_vcan", pads: [["J4", "2"], ["U5", "1"], ["U5", "3"], ["C20", "1"]]},
  {name: "can_gnd", pads: [["J4", "3"], ["U6", "3"], ["U5", "2"], ["R12", "2"], ["U4", "5"], ["C20", "2"], ["C21", "2"], ["C18", "2"]]},
  {name: "can_v5v", pads: [["U5", "5"], ["D3", "2"], ["U4", "8"], ["C21", "1"], ["C18", "1"]]},
  {name: "usb.usb.dp", pads: [["J1", "A6"], ["J1", "B6"], ["U3", "2"], ["U2", "35"]]},
  {name: "usb.usb.dm", pads: [["J1", "A7"], ["J1", "B7"], ["U3", "1"], ["U2", "36"]]},
  {name: "can_chain_0.txd", pads: [["U2", "8"], ["U4", "3"]]},
  {name: "can_chain_0.rxd", pads: [["U2", "12"], ["U4", "2"]]},
  {name: "sw_usb.out", pads: [["U2", "28"], ["SW1", "1"]]},
  {name: "sw_can.out", pads: [["U2", "48"], ["SW2", "1"]]},
  {name: "lcd.led", pads: [["U2", "23"], ["R5", "1"]]},
  {name: "lcd.reset", pads: [["U2", "13"], ["J3", "3"]]},
  {name: "lcd.rs", pads: [["U2", "15"], ["J3", "4"]]},
  {name: "lcd.spi.sck", pads: [["U2", "21"], ["J3", "6"]]},
  {name: "lcd.spi.mosi", pads: [["U2", "18"], ["J3", "5"]]},
  {name: "lcd.cs", pads: [["U2", "22"], ["J3", "8"]]},
  {name: "mcu.gpio.rgb_usb_red", pads: [["U2", "2"], ["R6", "2"]]},
  {name: "mcu.gpio.rgb_usb_green", pads: [["U2", "1"], ["R7", "2"]]},
  {name: "mcu.gpio.rgb_usb_blue", pads: [["U2", "3"], ["R8", "2"]]},
  {name: "mcu.gpio.rgb_can_red", pads: [["U2", "6"], ["R9", "2"]]},
  {name: "mcu.gpio.rgb_can_green", pads: [["U2", "4"], ["R10", "2"]]},
  {name: "mcu.gpio.rgb_can_blue", pads: [["U2", "7"], ["R11", "2"]]},
  {name: "xcvr.can.canh", pads: [["U4", "7"], ["U6", "2"], ["J4", "4"]]},
  {name: "xcvr.can.canl", pads: [["U4", "6"], ["U6", "1"], ["J4", "5"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "mcu.xtal_node.xi", pads: [["U2", "26"], ["X1", "1"], ["C15", "1"]]},
  {name: "mcu.xtal_node.xo", pads: [["U2", "25"], ["X1", "3"], ["C16", "1"]]},
  {name: "mcu.swd_node.swdio", pads: [["U2", "33"], ["J2", "10"], ["R3", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["U2", "29"], ["J2", "9"], ["R4", "2"]]},
  {name: "mcu.reset_node", pads: [["U2", "34"], ["J2", "6"]]},
  {name: "mcu.swd.swo", pads: [["U2", "9"], ["J2", "8"]]},
  {name: "mcu.swd.tdi", pads: [["J2", "7"]]},
  {name: "mcu.ic.xtal_rtc.xtal_in", pads: [["U2", "31"]]},
  {name: "mcu.ic.xtal_rtc.xtal_out", pads: [["U2", "32"]]},
  {name: "lcd.led_res.b", pads: [["R5", "2"], ["J3", "1"]]},
  {name: "rgb_usb.red_res.a", pads: [["R6", "1"], ["D1", "3"]]},
  {name: "rgb_usb.green_res.a", pads: [["R7", "1"], ["D1", "4"]]},
  {name: "rgb_usb.blue_res.a", pads: [["R8", "1"], ["D1", "1"]]},
  {name: "rgb_can.red_res.a", pads: [["R9", "1"], ["D2", "3"]]},
  {name: "rgb_can.green_res.a", pads: [["R10", "1"], ["D2", "4"]]},
  {name: "rgb_can.blue_res.a", pads: [["R11", "1"], ["D2", "1"]]},
  {name: "led_can.res.a", pads: [["R12", "1"], ["D3", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.1057086614173235, 1.7822834645669294);
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


