const board = new PCB();

// jlc_th.th1
const SH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.861, 1.261), rotate: 0,
  id: 'SH1'
})
// jlc_th.th2
const SH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.901, 1.261), rotate: 0,
  id: 'SH2'
})
// jlc_th.th3
const SH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.861, 1.300), rotate: 0,
  id: 'SH3'
})
// usb.conn
const SJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 0.956), rotate: 0,
  id: 'SJ1'
})
// usb.cc_pull.cc1.res
const SR1 = board.add(R_0402_1005Metric, {
  translate: pt(0.495, 0.810), rotate: 0,
  id: 'SR1'
})
// usb.cc_pull.cc2.res
const SR2 = board.add(R_0402_1005Metric, {
  translate: pt(0.495, 0.886), rotate: 0,
  id: 'SR2'
})
// vusb_protect.diode
const SD1 = board.add(D_SOD_323, {
  translate: pt(0.490, 1.298), rotate: 0,
  id: 'SD1'
})
// usb_reg.ic
const SU1 = board.add(SOT_23_5, {
  translate: pt(0.730, 0.858), rotate: 0,
  id: 'SU1'
})
// usb_reg.in_cap.cap
const SC1 = board.add(C_0402_1005Metric, {
  translate: pt(0.859, 0.983), rotate: 0,
  id: 'SC1'
})
// usb_reg.out_cap.cap
const SC2 = board.add(C_0805_2012Metric, {
  translate: pt(0.717, 1.003), rotate: 0,
  id: 'SC2'
})
// target_reg.ic
const SU2 = board.add(SOT_23_5, {
  translate: pt(1.093, 0.858), rotate: 0,
  id: 'SU2'
})
// target_reg.in_cap.cap
const SC3 = board.add(C_0402_1005Metric, {
  translate: pt(1.222, 0.983), rotate: 0,
  id: 'SC3'
})
// target_reg.out_cap.cap
const SC4 = board.add(C_0805_2012Metric, {
  translate: pt(1.080, 1.003), rotate: 0,
  id: 'SC4'
})
// mcu.swd.conn
const SJ2 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(0.138, 0.443), rotate: 0,
  id: 'SJ2'
})
// mcu.ic
const SU3 = board.add(QFN_56_1EP_7x7mm_P0_4mm_EP3_2x3_2mm, {
  translate: pt(0.163, 0.163), rotate: 0,
  id: 'SU3'
})
// mcu.iovdd_cap[0].cap
const SC5 = board.add(C_0402_1005Metric, {
  translate: pt(0.036, 0.580), rotate: 0,
  id: 'SC5'
})
// mcu.iovdd_cap[1].cap
const SC6 = board.add(C_0402_1005Metric, {
  translate: pt(0.147, 0.580), rotate: 0,
  id: 'SC6'
})
// mcu.iovdd_cap[2].cap
const SC7 = board.add(C_0402_1005Metric, {
  translate: pt(0.258, 0.580), rotate: 0,
  id: 'SC7'
})
// mcu.iovdd_cap[3].cap
const SC8 = board.add(C_0402_1005Metric, {
  translate: pt(0.369, 0.580), rotate: 0,
  id: 'SC8'
})
// mcu.iovdd_cap[4].cap
const SC9 = board.add(C_0402_1005Metric, {
  translate: pt(0.480, 0.580), rotate: 0,
  id: 'SC9'
})
// mcu.iovdd_cap[5].cap
const SC10 = board.add(C_0402_1005Metric, {
  translate: pt(0.591, 0.580), rotate: 0,
  id: 'SC10'
})
// mcu.avdd_cap.cap
const SC11 = board.add(C_0402_1005Metric, {
  translate: pt(0.702, 0.580), rotate: 0,
  id: 'SC11'
})
// mcu.vreg_in_cap.cap
const SC12 = board.add(C_0402_1005Metric, {
  translate: pt(0.813, 0.580), rotate: 0,
  id: 'SC12'
})
// mcu.mem.ic
const SU4 = board.add(SOIC_8_5_23x5_23mm_P1_27mm, {
  translate: pt(0.548, 0.113), rotate: 0,
  id: 'SU4'
})
// mcu.mem.vcc_cap.cap
const SC13 = board.add(C_0402_1005Metric, {
  translate: pt(0.036, 0.655), rotate: 0,
  id: 'SC13'
})
// mcu.dvdd_cap[0].cap
const SC14 = board.add(C_0402_1005Metric, {
  translate: pt(0.147, 0.655), rotate: 0,
  id: 'SC14'
})
// mcu.dvdd_cap[1].cap
const SC15 = board.add(C_0402_1005Metric, {
  translate: pt(0.258, 0.655), rotate: 0,
  id: 'SC15'
})
// mcu.vreg_out_cap.cap
const SC16 = board.add(C_0402_1005Metric, {
  translate: pt(0.369, 0.655), rotate: 0,
  id: 'SC16'
})
// mcu.usb_res.dp_res
const SR3 = board.add(R_0603_1608Metric, {
  translate: pt(0.562, 0.393), rotate: 0,
  id: 'SR3'
})
// mcu.usb_res.dm_res
const SR4 = board.add(R_0603_1608Metric, {
  translate: pt(0.718, 0.393), rotate: 0,
  id: 'SR4'
})
// mcu.crystal
const SU5 = board.add(Resonator_SMD_Murata_CSTxExxV_3Pin_3_0x1_1mm, {
  translate: pt(0.394, 0.428), rotate: 0,
  id: 'SU5'
})
// usb_esd
const SU6 = board.add(SOT_23, {
  translate: pt(0.746, 1.328), rotate: 0,
  id: 'SU6'
})
// led_tgt.package
const SD2 = board.add(LED_0603_1608Metric, {
  translate: pt(1.434, 0.820), rotate: 0,
  id: 'SD2'
})
// led_tgt.res
const SR5 = board.add(R_0402_1005Metric, {
  translate: pt(1.412, 0.907), rotate: 0,
  id: 'SR5'
})
// led_usb.package
const SD3 = board.add(LED_0603_1608Metric, {
  translate: pt(1.669, 0.820), rotate: 0,
  id: 'SD3'
})
// led_usb.res
const SR6 = board.add(R_0402_1005Metric, {
  translate: pt(1.647, 0.907), rotate: 0,
  id: 'SR6'
})
// en_pull.res
const SR7 = board.add(R_0402_1005Metric, {
  translate: pt(1.055, 1.280), rotate: 0,
  id: 'SR7'
})
// target.conn
const SJ3 = board.add(PinHeader_2x03_P2_54mm_EdgeInline, {
  translate: pt(1.126, 0.321), rotate: 0,
  id: 'SJ3'
})
// led_target.package
const SD4 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 1.290), rotate: 0,
  id: 'SD4'
})
// led_target.res
const SR8 = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.377), rotate: 0,
  id: 'SR8'
})
// target_sense.div.top_res
const SR9 = board.add(R_0402_1005Metric, {
  translate: pt(0.271, 1.280), rotate: 0,
  id: 'SR9'
})
// target_sense.div.bottom_res
const SR10 = board.add(R_0402_1005Metric, {
  translate: pt(0.271, 1.356), rotate: 0,
  id: 'SR10'
})

board.setNetlist([
  {name: "Svusb", pads: [["SJ1", "A4"], ["SJ1", "B9"], ["SJ1", "B4"], ["SJ1", "A9"], ["SD1", "1"], ["SU1", "1"], ["SU2", "1"], ["SU1", "3"], ["SC1", "1"], ["SC3", "1"]]},
  {name: "Sgnd", pads: [["SU6", "3"], ["SJ1", "A1"], ["SJ1", "B12"], ["SJ1", "B1"], ["SJ1", "A12"], ["SD1", "2"], ["SU1", "2"], ["SU2", "2"], ["SU3", "19"], ["SU3", "57"], ["SU5", "2"], ["SR5", "2"], ["SR6", "2"], ["SJ3", "5"], ["SR8", "2"], ["SR10", "2"], ["SJ1", "S1"], ["SC1", "2"], ["SC2", "2"], ["SC3", "2"], ["SC4", "2"], ["SJ2", "5"], ["SC5", "2"], ["SC6", "2"], ["SC7", "2"], ["SC8", "2"], ["SC9", "2"], ["SC10", "2"], ["SC11", "2"], ["SC12", "2"], ["SU4", "4"], ["SC14", "2"], ["SC15", "2"], ["SC16", "2"], ["SR1", "1"], ["SR2", "1"], ["SC13", "2"]]},
  {name: "Sv3v3", pads: [["SU1", "5"], ["SU3", "1"], ["SU3", "10"], ["SU3", "22"], ["SU3", "33"], ["SU3", "42"], ["SU3", "49"], ["SU3", "44"], ["SU3", "43"], ["SU3", "48"], ["SR7", "1"], ["SC2", "1"], ["SJ2", "1"], ["SC5", "1"], ["SC6", "1"], ["SC7", "1"], ["SC8", "1"], ["SC9", "1"], ["SC10", "1"], ["SC11", "1"], ["SC12", "1"], ["SU4", "8"], ["SC13", "1"]]},
  {name: "Svtarget", pads: [["SU2", "5"], ["SJ3", "1"], ["SD4", "2"], ["SR9", "1"], ["SC4", "1"]]},
  {name: "Susb_chain_0.d_P", pads: [["SJ1", "A6"], ["SJ1", "B6"], ["SU6", "2"], ["SR3", "2"]]},
  {name: "Susb_chain_0.d_N", pads: [["SJ1", "A7"], ["SJ1", "B7"], ["SU6", "1"], ["SR4", "2"]]},
  {name: "Sled_tgt.signal", pads: [["SU3", "27"], ["SD2", "2"]]},
  {name: "Sled_usb.signal", pads: [["SU3", "37"], ["SD3", "2"]]},
  {name: "Sen_pull.io", pads: [["SU3", "17"], ["SU2", "3"], ["SR7", "2"]]},
  {name: "Starget_drv.swclk", pads: [["SU3", "4"], ["SJ3", "4"]]},
  {name: "Starget_drv.swdio", pads: [["SU3", "5"], ["SJ3", "2"]]},
  {name: "Starget.swo", pads: [["SU3", "3"], ["SJ3", "6"]]},
  {name: "Starget.reset", pads: [["SU3", "7"], ["SJ3", "3"]]},
  {name: "Starget_sense.output", pads: [["SU3", "40"], ["SR9", "2"], ["SR10", "1"]]},
  {name: "Susb.conn.cc.cc1", pads: [["SJ1", "A5"], ["SR1", "2"]]},
  {name: "Susb.conn.cc.cc2", pads: [["SJ1", "B5"], ["SR2", "2"]]},
  {name: "Smcu.xtal_node.xi", pads: [["SU3", "20"], ["SU5", "1"]]},
  {name: "Smcu.xtal_node.xo", pads: [["SU3", "21"], ["SU5", "3"]]},
  {name: "Smcu.swd_node.swdio", pads: [["SU3", "25"], ["SJ2", "2"]]},
  {name: "Smcu.swd_node.swclk", pads: [["SU3", "24"], ["SJ2", "4"]]},
  {name: "Smcu.reset_node", pads: [["SU3", "26"], ["SJ2", "3"]]},
  {name: "Smcu.ic.qspi.sck", pads: [["SU3", "52"], ["SU4", "6"]]},
  {name: "Smcu.ic.qspi.mosi", pads: [["SU3", "53"], ["SU4", "5"]]},
  {name: "Smcu.ic.qspi.miso", pads: [["SU3", "55"], ["SU4", "2"]]},
  {name: "Smcu.ic.qspi_cs", pads: [["SU3", "56"], ["SU4", "1"]]},
  {name: "Smcu.ic.qspi_sd2", pads: [["SU3", "54"], ["SU4", "3"]]},
  {name: "Smcu.ic.qspi_sd3", pads: [["SU3", "51"], ["SU4", "7"]]},
  {name: "Smcu.ic.vreg_vout", pads: [["SU3", "45"], ["SU3", "23"], ["SU3", "50"], ["SC14", "1"], ["SC15", "1"], ["SC16", "1"]]},
  {name: "Smcu.usb_chain_0.d_P", pads: [["SU3", "47"], ["SR3", "1"]]},
  {name: "Smcu.usb_chain_0.d_N", pads: [["SU3", "46"], ["SR4", "1"]]},
  {name: "Smcu.swd.swo", pads: [["SU3", "15"], ["SJ2", "6"]]},
  {name: "Sled_tgt.res.a", pads: [["SR5", "1"], ["SD2", "1"]]},
  {name: "Sled_usb.res.a", pads: [["SR6", "1"], ["SD3", "1"]]},
  {name: "Sled_target.res.a", pads: [["SR8", "1"], ["SD4", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.8452755905511813, 1.5133858267716536);
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


