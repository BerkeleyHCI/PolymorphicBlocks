const board = new PCB();

// jlc_th.th1
const SH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.906, 1.117), rotate: 0,
  id: 'SH1'
})
// jlc_th.th2
const SH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.945, 1.117), rotate: 0,
  id: 'SH2'
})
// jlc_th.th3
const SH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.906, 1.157), rotate: 0,
  id: 'SH3'
})
// usb.conn
const SJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.111, 0.165), rotate: 0,
  id: 'SJ1'
})
// usb.esd
const SU1 = board.add(SOT_23, {
  translate: pt(0.977, 0.458), rotate: 0,
  id: 'SU1'
})
// usb.cc_pull.cc1
const SR1 = board.add(R_0402_1005Metric, {
  translate: pt(1.129, 0.409), rotate: 0,
  id: 'SR1'
})
// usb.cc_pull.cc2
const SR2 = board.add(R_0402_1005Metric, {
  translate: pt(1.241, 0.409), rotate: 0,
  id: 'SR2'
})
// vusb_protect.diode
const SD1 = board.add(D_SOD_323, {
  translate: pt(0.724, 1.155), rotate: 0,
  id: 'SD1'
})
// usb_reg.ic
const SU2 = board.add(SOT_23_5, {
  translate: pt(0.081, 0.816), rotate: 0,
  id: 'SU2'
})
// usb_reg.in_cap.cap
const SC1 = board.add(C_0402_1005Metric, {
  translate: pt(0.209, 0.940), rotate: 0,
  id: 'SC1'
})
// usb_reg.out_cap.cap
const SC2 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 0.961), rotate: 0,
  id: 'SC2'
})
// target_reg.ic
const SU3 = board.add(SOT_23_5, {
  translate: pt(0.444, 0.816), rotate: 0,
  id: 'SU3'
})
// target_reg.in_cap.cap
const SC3 = board.add(C_0402_1005Metric, {
  translate: pt(0.572, 0.940), rotate: 0,
  id: 'SC3'
})
// target_reg.out_cap.cap
const SC4 = board.add(C_0805_2012Metric, {
  translate: pt(0.430, 0.961), rotate: 0,
  id: 'SC4'
})
// mcu.ic
const SU4 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'SU4'
})
// mcu.pwr_cap[0].cap
const SC5 = board.add(C_0805_2012Metric, {
  translate: pt(0.256, 0.483), rotate: 0,
  id: 'SC5'
})
// mcu.pwr_cap[1].cap
const SC6 = board.add(C_0402_1005Metric, {
  translate: pt(0.511, 0.463), rotate: 0,
  id: 'SC6'
})
// mcu.pwr_cap[2].cap
const SC7 = board.add(C_0402_1005Metric, {
  translate: pt(0.622, 0.463), rotate: 0,
  id: 'SC7'
})
// mcu.pwr_cap[3].cap
const SC8 = board.add(C_0402_1005Metric, {
  translate: pt(0.733, 0.463), rotate: 0,
  id: 'SC8'
})
// mcu.vdda_cap_0.cap
const SC9 = board.add(C_0402_1005Metric, {
  translate: pt(0.036, 0.613), rotate: 0,
  id: 'SC9'
})
// mcu.vdda_cap_1.cap
const SC10 = board.add(C_0402_1005Metric, {
  translate: pt(0.147, 0.613), rotate: 0,
  id: 'SC10'
})
// mcu.crystal
const SU5 = board.add(Resonator_SMD_Murata_CSTxExxV_3Pin_3_0x1_1mm, {
  translate: pt(0.079, 0.508), rotate: 0,
  id: 'SU5'
})
// mcu.swd.conn
const SJ2 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(0.614, 0.146), rotate: 0,
  id: 'SJ2'
})
// mcu.usb_pull.dp
const SR3 = board.add(R_0402_1005Metric, {
  translate: pt(0.399, 0.463), rotate: 0,
  id: 'SR3'
})
// led_tgt.package
const SD2 = board.add(LED_0603_1608Metric, {
  translate: pt(1.541, 0.778), rotate: 0,
  id: 'SD2'
})
// led_tgt.res
const SR4 = board.add(R_0402_1005Metric, {
  translate: pt(1.519, 0.865), rotate: 0,
  id: 'SR4'
})
// led_usb.package
const SD3 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 1.146), rotate: 0,
  id: 'SD3'
})
// led_usb.res
const SR5 = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.233), rotate: 0,
  id: 'SR5'
})
// en_pull.res
const SR6 = board.add(R_0402_1005Metric, {
  translate: pt(1.100, 1.136), rotate: 0,
  id: 'SR6'
})
// target_drv.swclk_res.res
const SR7 = board.add(R_0402_1005Metric, {
  translate: pt(1.215, 0.767), rotate: 0,
  id: 'SR7'
})
// target_drv.swdio_res.res
const SR8 = board.add(R_0402_1005Metric, {
  translate: pt(1.328, 0.767), rotate: 0,
  id: 'SR8'
})
// target_drv.swdio_drv_res.res
const SR9 = board.add(R_0402_1005Metric, {
  translate: pt(1.215, 0.844), rotate: 0,
  id: 'SR9'
})
// target_drv.reset_res.res
const SR10 = board.add(R_0402_1005Metric, {
  translate: pt(1.328, 0.844), rotate: 0,
  id: 'SR10'
})
// target_drv.swo_res.res
const SR11 = board.add(R_0402_1005Metric, {
  translate: pt(1.215, 0.920), rotate: 0,
  id: 'SR11'
})
// reset_pull.res
const SR12 = board.add(R_0402_1005Metric, {
  translate: pt(1.291, 1.136), rotate: 0,
  id: 'SR12'
})
// reset_sw.package
const SSW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(0.893, 0.861), rotate: 0,
  id: 'SSW1'
})
// target.conn
const SJ3 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(1.608, 0.146), rotate: 0,
  id: 'SJ3'
})
// led_target.package
const SD4 = board.add(LED_0603_1608Metric, {
  translate: pt(0.293, 1.146), rotate: 0,
  id: 'SD4'
})
// led_target.res
const SR13 = board.add(R_0402_1005Metric, {
  translate: pt(0.271, 1.233), rotate: 0,
  id: 'SR13'
})
// target_sense.div.top_res
const SR14 = board.add(R_0402_1005Metric, {
  translate: pt(0.506, 1.136), rotate: 0,
  id: 'SR14'
})
// target_sense.div.bottom_res
const SR15 = board.add(R_0402_1005Metric, {
  translate: pt(0.506, 1.212), rotate: 0,
  id: 'SR15'
})

board.setNetlist([
  {name: "vusb", pads: [["SJ1", "A4"], ["SJ1", "A9"], ["SJ1", "B4"], ["SJ1", "B9"], ["SD1", "1"], ["SU2", "1"], ["SU2", "3"], ["SC1", "1"], ["SU3", "1"], ["SC3", "1"]]},
  {name: "gnd", pads: [["SJ1", "A1"], ["SJ1", "A12"], ["SJ1", "B1"], ["SJ1", "B12"], ["SJ1", "S1"], ["SU1", "3"], ["SR1", "1"], ["SR2", "1"], ["SD1", "2"], ["SU2", "2"], ["SC1", "2"], ["SC2", "2"], ["SU3", "2"], ["SC3", "2"], ["SC4", "2"], ["SU4", "23"], ["SU4", "35"], ["SU4", "44"], ["SU4", "47"], ["SU4", "8"], ["SC5", "2"], ["SC6", "2"], ["SC7", "2"], ["SC8", "2"], ["SC9", "2"], ["SC10", "2"], ["SU5", "2"], ["SJ2", "3"], ["SJ2", "5"], ["SJ2", "9"], ["SR4", "2"], ["SR5", "2"], ["SSW1", "2"], ["SJ3", "3"], ["SJ3", "5"], ["SJ3", "9"], ["SR13", "2"], ["SR15", "2"]]},
  {name: "v3v3", pads: [["SU2", "5"], ["SC2", "1"], ["SU4", "1"], ["SU4", "24"], ["SU4", "36"], ["SU4", "48"], ["SU4", "9"], ["SC5", "1"], ["SC6", "1"], ["SC7", "1"], ["SC8", "1"], ["SC9", "1"], ["SC10", "1"], ["SJ2", "1"], ["SR3", "1"], ["SR6", "1"], ["SR12", "1"]]},
  {name: "vtarget", pads: [["SU3", "5"], ["SC4", "1"], ["SJ3", "1"], ["SD4", "2"], ["SR14", "1"]]},
  {name: "usb.usb.dp", pads: [["SJ1", "A6"], ["SJ1", "B6"], ["SU1", "2"], ["SU4", "33"], ["SR3", "2"]]},
  {name: "usb.usb.dm", pads: [["SJ1", "A7"], ["SJ1", "B7"], ["SU1", "1"], ["SU4", "32"]]},
  {name: "usb.conn.cc.cc1", pads: [["SJ1", "A5"], ["SR1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["SJ1", "B5"], ["SR2", "2"]]},
  {name: "target_reg.reset", pads: [["SU3", "3"], ["SU4", "28"], ["SR6", "2"]]},
  {name: "mcu.xtal_node.xi", pads: [["SU4", "5"], ["SU5", "1"]]},
  {name: "mcu.xtal_node.xo", pads: [["SU4", "6"], ["SU5", "3"]]},
  {name: "mcu.swd_node.swdio", pads: [["SU4", "34"], ["SJ2", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["SU4", "37"], ["SJ2", "4"]]},
  {name: "mcu.reset_node", pads: [["SU4", "7"], ["SJ2", "10"]]},
  {name: "mcu.swd.tdi", pads: [["SJ2", "8"]]},
  {name: "mcu.swd.swo", pads: [["SU4", "39"], ["SJ2", "6"]]},
  {name: "led_tgt.signal", pads: [["SU4", "30"], ["SD2", "2"]]},
  {name: "led_tgt.package.k", pads: [["SD2", "1"], ["SR4", "1"]]},
  {name: "led_usb.signal", pads: [["SU4", "42"], ["SD3", "2"]]},
  {name: "led_usb.package.k", pads: [["SD3", "1"], ["SR5", "1"]]},
  {name: "target_drv.reset_in", pads: [["SU4", "18"], ["SR10", "1"], ["SR12", "2"], ["SSW1", "1"]]},
  {name: "target_drv.swclk_in", pads: [["SU4", "26"], ["SR7", "1"]]},
  {name: "target_drv.swdio_in", pads: [["SU4", "25"], ["SR9", "1"]]},
  {name: "target_drv.swdio_out", pads: [["SU4", "27"], ["SR8", "1"], ["SR9", "2"]]},
  {name: "target_drv.reset_out", pads: [["SR10", "2"], ["SJ3", "10"]]},
  {name: "target_drv.swo_out", pads: [["SU4", "31"], ["SR11", "2"]]},
  {name: "target_drv.swd.swdio", pads: [["SR8", "2"], ["SJ3", "2"]]},
  {name: "target_drv.swd.swclk", pads: [["SR7", "2"], ["SJ3", "4"]]},
  {name: "target_drv.swo_in", pads: [["SR11", "1"], ["SJ3", "6"]]},
  {name: "target.tdi", pads: [["SJ3", "8"]]},
  {name: "led_target.package.k", pads: [["SD4", "1"], ["SR13", "1"]]},
  {name: "target_sense.output", pads: [["SU4", "10"], ["SR14", "2"], ["SR15", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.8952755905511813, 1.369685039370079);
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


