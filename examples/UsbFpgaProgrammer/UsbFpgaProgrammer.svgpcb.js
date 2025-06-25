const board = new PCB();

// jlc_th.th1
const FH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.000, 1.224), rotate: 0,
  id: 'FH1'
})
// jlc_th.th2
const FH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.039, 1.224), rotate: 0,
  id: 'FH2'
})
// jlc_th.th3
const FH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.000, 1.263), rotate: 0,
  id: 'FH3'
})
// usb.conn
const FJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.224, 0.165), rotate: 0,
  id: 'FJ1'
})
// usb.cc_pull.cc1.res
const FR1 = board.add(R_0603_1608Metric, {
  translate: pt(1.072, 0.420), rotate: 0,
  id: 'FR1'
})
// usb.cc_pull.cc2.res
const FR2 = board.add(R_0603_1608Metric, {
  translate: pt(1.228, 0.420), rotate: 0,
  id: 'FR2'
})
// vusb_protect.diode
const FD1 = board.add(D_SOD_323, {
  translate: pt(1.225, 0.852), rotate: 0,
  id: 'FD1'
})
// ft232.ic
const FU1 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'FU1'
})
// ft232.vbus_fb.fb
const FFB1 = board.add(L_0603_1608Metric, {
  translate: pt(0.676, 0.202), rotate: 0,
  id: 'FFB1'
})
// ft232.vregin_cap0.cap
const FC1 = board.add(C_0805_2012Metric, {
  translate: pt(0.512, 0.212), rotate: 0,
  id: 'FC1'
})
// ft232.vregin_cap1.cap
const FC2 = board.add(C_0603_1608Metric, {
  translate: pt(0.832, 0.202), rotate: 0,
  id: 'FC2'
})
// ft232.vphy_fb.fb
const FFB2 = board.add(L_0603_1608Metric, {
  translate: pt(0.503, 0.319), rotate: 0,
  id: 'FFB2'
})
// ft232.vphy_cap.cap
const FC3 = board.add(C_0603_1608Metric, {
  translate: pt(0.659, 0.319), rotate: 0,
  id: 'FC3'
})
// ft232.vpll_fb.fb
const FFB3 = board.add(L_0603_1608Metric, {
  translate: pt(0.815, 0.319), rotate: 0,
  id: 'FFB3'
})
// ft232.vpll_cap.cap
const FC4 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.474), rotate: 0,
  id: 'FC4'
})
// ft232.vcccore_cap.cap
const FC5 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 0.474), rotate: 0,
  id: 'FC5'
})
// ft232.vcca_cap.cap
const FC6 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.474), rotate: 0,
  id: 'FC6'
})
// ft232.vccd_cap.cap
const FC7 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.474), rotate: 0,
  id: 'FC7'
})
// ft232.vccio_cap0.cap
const FC8 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 0.474), rotate: 0,
  id: 'FC8'
})
// ft232.vccio_cap1.cap
const FC9 = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 0.474), rotate: 0,
  id: 'FC9'
})
// ft232.vccio_cap2.cap
const FC10 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.570), rotate: 0,
  id: 'FC10'
})
// ft232.ref_res
const FR3 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 0.570), rotate: 0,
  id: 'FR3'
})
// ft232.crystal.package
const FX1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(0.528, 0.067), rotate: 0,
  id: 'FX1'
})
// ft232.crystal.cap_a
const FC11 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.570), rotate: 0,
  id: 'FC11'
})
// ft232.crystal.cap_b
const FC12 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.570), rotate: 0,
  id: 'FC12'
})
// ft232.eeprom.ic
const FU2 = board.add(SOT_23_6, {
  translate: pt(0.730, 0.067), rotate: 0,
  id: 'FU2'
})
// ft232.eeprom.vcc_cap.cap
const FC13 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 0.570), rotate: 0,
  id: 'FC13'
})
// ft232.eeprom_spi.do_pull.res
const FR4 = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 0.570), rotate: 0,
  id: 'FR4'
})
// ft232.eeprom_spi.do_res
const FR5 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 0.667), rotate: 0,
  id: 'FR5'
})
// usb_esd
const FU3 = board.add(SOT_23, {
  translate: pt(1.481, 0.881), rotate: 0,
  id: 'FU3'
})
// led0.package
const FD2 = board.add(LED_0603_1608Metric, {
  translate: pt(0.985, 0.843), rotate: 0,
  id: 'FD2'
})
// led0.res
const FR6 = board.add(R_0603_1608Metric, {
  translate: pt(0.985, 0.940), rotate: 0,
  id: 'FR6'
})
// led1.package
const FD3 = board.add(LED_0603_1608Metric, {
  translate: pt(0.515, 0.843), rotate: 0,
  id: 'FD3'
})
// led1.res
const FR7 = board.add(R_0603_1608Metric, {
  translate: pt(0.515, 0.940), rotate: 0,
  id: 'FR7'
})
// led2.package
const FD4 = board.add(LED_0603_1608Metric, {
  translate: pt(0.750, 0.843), rotate: 0,
  id: 'FD4'
})
// led2.res
const FR8 = board.add(R_0603_1608Metric, {
  translate: pt(0.750, 0.940), rotate: 0,
  id: 'FR8'
})
// out.conn
const FJ2 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(0.169, 0.960), rotate: 0,
  id: 'FJ2'
})

board.setNetlist([
  {name: "Fvusb", pads: [["FJ1", "A4"], ["FJ1", "B9"], ["FJ1", "B4"], ["FJ1", "A9"], ["FD1", "1"], ["FFB1", "1"]]},
  {name: "Fgnd", pads: [["FU3", "3"], ["FJ1", "A1"], ["FJ1", "B12"], ["FJ1", "B1"], ["FJ1", "A12"], ["FD1", "2"], ["FU1", "4"], ["FU1", "9"], ["FU1", "41"], ["FU1", "10"], ["FU1", "11"], ["FU1", "22"], ["FU1", "23"], ["FU1", "35"], ["FU1", "36"], ["FU1", "47"], ["FU1", "48"], ["FU1", "42"], ["FR6", "2"], ["FR7", "2"], ["FR8", "2"], ["FJ1", "S1"], ["FR3", "2"], ["FJ2", "3"], ["FJ2", "5"], ["FJ2", "9"], ["FC1", "2"], ["FC2", "2"], ["FC3", "2"], ["FC4", "2"], ["FC5", "2"], ["FC6", "2"], ["FC7", "2"], ["FC8", "2"], ["FC9", "2"], ["FC10", "2"], ["FX1", "2"], ["FX1", "4"], ["FU2", "2"], ["FR1", "1"], ["FR2", "1"], ["FC11", "2"], ["FC12", "2"], ["FC13", "2"]]},
  {name: "Fusb_chain_0.d_P", pads: [["FJ1", "A6"], ["FJ1", "B6"], ["FU3", "2"], ["FU1", "7"]]},
  {name: "Fusb_chain_0.d_N", pads: [["FJ1", "A7"], ["FJ1", "B7"], ["FU3", "1"], ["FU1", "6"]]},
  {name: "Fled0.signal", pads: [["FU1", "21"], ["FD2", "2"]]},
  {name: "Fled1.signal", pads: [["FU1", "27"], ["FD3", "2"]]},
  {name: "Fled2.signal", pads: [["FU1", "28"], ["FD4", "2"]]},
  {name: "Fft232.mpsse.sck", pads: [["FU1", "13"], ["FJ2", "4"]]},
  {name: "Fft232.mpsse.mosi", pads: [["FU1", "14"], ["FJ2", "6"]]},
  {name: "Fft232.mpsse.miso", pads: [["FU1", "15"], ["FJ2", "8"]]},
  {name: "Fout.cs", pads: [["FU1", "17"], ["FJ2", "2"]]},
  {name: "Fout.reset", pads: [["FU1", "20"], ["FJ2", "10"]]},
  {name: "Fusb.conn.cc.cc1", pads: [["FJ1", "A5"], ["FR1", "2"]]},
  {name: "Fusb.conn.cc.cc2", pads: [["FJ1", "B5"], ["FR2", "2"]]},
  {name: "Fft232.acbus.1", pads: [["FU1", "25"]]},
  {name: "Fft232.acbus.2", pads: [["FU1", "26"]]},
  {name: "Fft232.acbus.5", pads: [["FU1", "29"]]},
  {name: "Fft232.acbus.6", pads: [["FU1", "30"]]},
  {name: "Fft232.acbus.7", pads: [["FU1", "31"]]},
  {name: "Fft232.acbus.8", pads: [["FU1", "32"]]},
  {name: "Fft232.acbus.9", pads: [["FU1", "33"]]},
  {name: "Fft232.ic.vregin", pads: [["FU1", "40"], ["FFB1", "2"], ["FC1", "1"], ["FC2", "1"]]},
  {name: "Fft232.ic.vccd", pads: [["FU1", "39"], ["FU1", "12"], ["FU1", "24"], ["FU1", "46"], ["FU1", "34"], ["FFB2", "1"], ["FFB3", "1"], ["FC7", "1"], ["FC8", "1"], ["FC9", "1"], ["FC10", "1"], ["FU2", "6"], ["FR4", "1"], ["FC13", "1"]]},
  {name: "Fft232.ic.vphy", pads: [["FU1", "3"], ["FFB2", "2"], ["FC3", "1"]]},
  {name: "Fft232.ic.vpll", pads: [["FU1", "8"], ["FFB3", "2"], ["FC4", "1"]]},
  {name: "Fft232.ic.vcccore", pads: [["FU1", "38"], ["FC5", "1"]]},
  {name: "Fft232.ic.vcca", pads: [["FU1", "37"], ["FC6", "1"]]},
  {name: "Fft232.ref_res.a", pads: [["FR3", "1"], ["FU1", "5"]]},
  {name: "Fft232.crystal.crystal.xtal_in", pads: [["FX1", "1"], ["FC11", "1"], ["FU1", "1"]]},
  {name: "Fft232.crystal.crystal.xtal_out", pads: [["FX1", "3"], ["FC12", "1"], ["FU1", "2"]]},
  {name: "Fft232.eeprom.cs", pads: [["FU1", "45"], ["FU2", "5"]]},
  {name: "Fft232.eeprom_spi.eeclk", pads: [["FU1", "44"], ["FU2", "4"]]},
  {name: "Fft232.eeprom_spi.eedata", pads: [["FU1", "43"], ["FR5", "2"], ["FU2", "3"]]},
  {name: "Fft232.eeprom_spi.spi.miso", pads: [["FU2", "1"], ["FR5", "1"], ["FR4", "2"]]},
  {name: "Fft232.ic.adbus.3", pads: [["FU1", "16"]]},
  {name: "Fft232.ic.adbus.5", pads: [["FU1", "18"]]},
  {name: "Fft232.ic.adbus.6", pads: [["FU1", "19"]]},
  {name: "Fled0.res.a", pads: [["FR6", "1"], ["FD2", "1"]]},
  {name: "Fled1.res.a", pads: [["FR7", "1"], ["FD3", "1"]]},
  {name: "Fled2.res.a", pads: [["FR8", "1"], ["FD4", "1"]]},
  {name: "Fout.pwr", pads: [["FJ2", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.5962598425196852, 1.3811023622047247);
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


