const board = new PCB();

// jlc_th.th1
const SH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.635, 1.158), rotate: 0,
  id: 'SH1'
})
// jlc_th.th2
const SH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.674, 1.158), rotate: 0,
  id: 'SH2'
})
// jlc_th.th3
const SH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.635, 1.198), rotate: 0,
  id: 'SH3'
})
// usb.conn
const SJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.111, 0.165), rotate: 0,
  id: 'SJ1'
})
// usb.cc_pull.cc1.res
const SR1 = board.add(R_0402_1005Metric, {
  translate: pt(1.396, 0.019), rotate: 0,
  id: 'SR1'
})
// usb.cc_pull.cc2.res
const SR2 = board.add(R_0402_1005Metric, {
  translate: pt(1.396, 0.095), rotate: 0,
  id: 'SR2'
})
// vusb_protect.diode
const SD1 = board.add(D_SOD_323, {
  translate: pt(1.263, 1.196), rotate: 0,
  id: 'SD1'
})
// usb_reg.ic
const SU1 = board.add(SOT_23_5, {
  translate: pt(0.537, 0.816), rotate: 0,
  id: 'SU1'
})
// usb_reg.in_cap.cap
const SC1 = board.add(C_0402_1005Metric, {
  translate: pt(0.666, 0.940), rotate: 0,
  id: 'SC1'
})
// usb_reg.out_cap.cap
const SC2 = board.add(C_0805_2012Metric, {
  translate: pt(0.524, 0.961), rotate: 0,
  id: 'SC2'
})
// target_reg.ic
const SU2 = board.add(SOT_23_5, {
  translate: pt(0.900, 0.816), rotate: 0,
  id: 'SU2'
})
// target_reg.in_cap.cap
const SC3 = board.add(C_0402_1005Metric, {
  translate: pt(1.029, 0.940), rotate: 0,
  id: 'SC3'
})
// target_reg.out_cap.cap
const SC4 = board.add(C_0805_2012Metric, {
  translate: pt(0.887, 0.961), rotate: 0,
  id: 'SC4'
})
// mcu.swd.conn
const SJ2 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(0.614, 0.146), rotate: 0,
  id: 'SJ2'
})
// mcu.ic
const SU3 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'SU3'
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
// mcu.usb_pull.dp
const SR3 = board.add(R_0402_1005Metric, {
  translate: pt(0.399, 0.463), rotate: 0,
  id: 'SR3'
})
// mcu.crystal
const SU4 = board.add(Resonator_SMD_Murata_CSTxExxV_3Pin_3_0x1_1mm, {
  translate: pt(0.079, 0.508), rotate: 0,
  id: 'SU4'
})
// usb_esd
const SU5 = board.add(SOT_23, {
  translate: pt(1.520, 1.225), rotate: 0,
  id: 'SU5'
})
// led_tgt.package
const SD2 = board.add(LED_0603_1608Metric, {
  translate: pt(0.362, 1.187), rotate: 0,
  id: 'SD2'
})
// led_tgt.res
const SR4 = board.add(R_0402_1005Metric, {
  translate: pt(0.341, 1.274), rotate: 0,
  id: 'SR4'
})
// led_usb.package
const SD3 = board.add(LED_0603_1608Metric, {
  translate: pt(0.597, 1.187), rotate: 0,
  id: 'SD3'
})
// led_usb.res
const SR5 = board.add(R_0402_1005Metric, {
  translate: pt(0.575, 1.274), rotate: 0,
  id: 'SR5'
})
// en_pull.res
const SR6 = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.485), rotate: 0,
  id: 'SR6'
})
// target_drv.swclk_res
const SR7 = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.177), rotate: 0,
  id: 'SR7'
})
// target_drv.swdio_res
const SR8 = board.add(R_0402_1005Metric, {
  translate: pt(0.149, 1.177), rotate: 0,
  id: 'SR8'
})
// target_drv.swdio_drv_res
const SR9 = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.253), rotate: 0,
  id: 'SR9'
})
// target_drv.reset_res
const SR10 = board.add(R_0402_1005Metric, {
  translate: pt(0.149, 1.253), rotate: 0,
  id: 'SR10'
})
// target_drv.swo_res
const SR11 = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.330), rotate: 0,
  id: 'SR11'
})
// reset_pull.res
const SR12 = board.add(R_0402_1005Metric, {
  translate: pt(0.228, 1.485), rotate: 0,
  id: 'SR12'
})
// reset_sw.package
const SSW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.350, 0.861), rotate: 0,
  id: 'SSW1'
})
// target.conn
const SJ3 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(0.169, 0.894), rotate: 0,
  id: 'SJ3'
})
// led_target.package
const SD4 = board.add(LED_0603_1608Metric, {
  translate: pt(0.832, 1.187), rotate: 0,
  id: 'SD4'
})
// led_target.res
const SR13 = board.add(R_0402_1005Metric, {
  translate: pt(0.810, 1.274), rotate: 0,
  id: 'SR13'
})
// target_sense.div.top_res
const SR14 = board.add(R_0402_1005Metric, {
  translate: pt(1.045, 1.177), rotate: 0,
  id: 'SR14'
})
// target_sense.div.bottom_res
const SR15 = board.add(R_0402_1005Metric, {
  translate: pt(1.045, 1.253), rotate: 0,
  id: 'SR15'
})

board.setNetlist([
  {name: "Svusb", pads: [["SJ1", "A4"], ["SJ1", "B9"], ["SJ1", "B4"], ["SJ1", "A9"], ["SD1", "1"], ["SU1", "1"], ["SU2", "1"], ["SU1", "3"], ["SC1", "1"], ["SC3", "1"]]},
  {name: "Sgnd", pads: [["SU5", "3"], ["SJ1", "A1"], ["SJ1", "B12"], ["SJ1", "B1"], ["SJ1", "A12"], ["SD1", "2"], ["SU1", "2"], ["SU2", "2"], ["SU3", "8"], ["SU3", "23"], ["SU3", "35"], ["SU3", "47"], ["SU3", "44"], ["SU4", "2"], ["SR4", "2"], ["SR5", "2"], ["SSW1", "2"], ["SR13", "2"], ["SR15", "2"], ["SJ1", "S1"], ["SJ3", "3"], ["SJ3", "5"], ["SJ3", "9"], ["SC1", "2"], ["SC2", "2"], ["SC3", "2"], ["SC4", "2"], ["SC5", "2"], ["SC6", "2"], ["SC7", "2"], ["SC8", "2"], ["SC9", "2"], ["SC10", "2"], ["SR1", "1"], ["SR2", "1"], ["SJ2", "3"], ["SJ2", "5"], ["SJ2", "9"]]},
  {name: "Sv3v3", pads: [["SU1", "5"], ["SU3", "1"], ["SU3", "9"], ["SU3", "24"], ["SU3", "36"], ["SU3", "48"], ["SR6", "1"], ["SR12", "1"], ["SC2", "1"], ["SJ2", "1"], ["SC5", "1"], ["SC6", "1"], ["SC7", "1"], ["SC8", "1"], ["SC9", "1"], ["SC10", "1"], ["SR3", "1"]]},
  {name: "Svtarget", pads: [["SU2", "5"], ["SJ3", "1"], ["SD4", "2"], ["SR14", "1"], ["SC4", "1"]]},
  {name: "Susb_chain_0.d_P", pads: [["SJ1", "A6"], ["SJ1", "B6"], ["SU5", "2"], ["SU3", "33"], ["SR3", "2"]]},
  {name: "Susb_chain_0.d_N", pads: [["SJ1", "A7"], ["SJ1", "B7"], ["SU5", "1"], ["SU3", "32"]]},
  {name: "Sled_tgt.signal", pads: [["SU3", "30"], ["SD2", "2"]]},
  {name: "Sled_usb.signal", pads: [["SU3", "42"], ["SD3", "2"]]},
  {name: "Sen_pull.io", pads: [["SU3", "28"], ["SU2", "3"], ["SR6", "2"]]},
  {name: "Starget_drv.swclk_in", pads: [["SU3", "26"], ["SR7", "1"]]},
  {name: "Starget_drv.swdio_out", pads: [["SU3", "27"], ["SR8", "1"], ["SR9", "2"]]},
  {name: "Starget_drv.swdio_in", pads: [["SU3", "25"], ["SR9", "1"]]},
  {name: "Sreset_pull.io", pads: [["SU3", "18"], ["SR12", "2"], ["SSW1", "1"], ["SR10", "1"]]},
  {name: "Starget_drv.swo_out", pads: [["SU3", "31"], ["SR11", "1"]]},
  {name: "Starget_drv.swd.swdio", pads: [["SJ3", "2"], ["SR8", "2"]]},
  {name: "Starget_drv.swd.swclk", pads: [["SR7", "2"], ["SJ3", "4"]]},
  {name: "Starget_drv.swo_in", pads: [["SR11", "2"], ["SJ3", "6"]]},
  {name: "Starget_drv.reset_out", pads: [["SR10", "2"], ["SJ3", "10"]]},
  {name: "Starget_sense.output", pads: [["SU3", "10"], ["SR14", "2"], ["SR15", "1"]]},
  {name: "Susb.conn.cc.cc1", pads: [["SJ1", "A5"], ["SR1", "2"]]},
  {name: "Susb.conn.cc.cc2", pads: [["SJ1", "B5"], ["SR2", "2"]]},
  {name: "Smcu.xtal_node.xi", pads: [["SU3", "5"], ["SU4", "1"]]},
  {name: "Smcu.xtal_node.xo", pads: [["SU3", "6"], ["SU4", "3"]]},
  {name: "Smcu.swd_node.swdio", pads: [["SU3", "34"], ["SJ2", "2"]]},
  {name: "Smcu.swd_node.swclk", pads: [["SU3", "37"], ["SJ2", "4"]]},
  {name: "Smcu.reset_node", pads: [["SU3", "7"], ["SJ2", "10"]]},
  {name: "Smcu.swd.swo", pads: [["SU3", "39"], ["SJ2", "6"]]},
  {name: "Smcu.swd.tdi", pads: [["SJ2", "8"]]},
  {name: "Sled_tgt.res.a", pads: [["SR4", "1"], ["SD2", "1"]]},
  {name: "Sled_usb.res.a", pads: [["SR5", "1"], ["SD3", "1"]]},
  {name: "Starget.tdi", pads: [["SJ3", "8"]]},
  {name: "Sled_target.res.a", pads: [["SR13", "1"], ["SD4", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.792322834645669, 1.6212598425196851);
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


