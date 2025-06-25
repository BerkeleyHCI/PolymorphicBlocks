const board = new PCB();

// jlc_th.th1
const TH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.421, 2.307), rotate: 0,
  id: 'TH1'
})
// jlc_th.th2
const TH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.460, 2.307), rotate: 0,
  id: 'TH2'
})
// jlc_th.th3
const TH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.421, 2.346), rotate: 0,
  id: 'TH3'
})
// usb.conn
const TJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 1.905), rotate: 0,
  id: 'TJ1'
})
// usb.cc_pull.cc1.res
const TR1 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.160), rotate: 0,
  id: 'TR1'
})
// usb.cc_pull.cc2.res
const TR2 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.160), rotate: 0,
  id: 'TR2'
})
// tp_gnd.tp
const TTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.311, 2.344), rotate: 0,
  id: 'TTP1'
})
// choke.fb
const TFB1 = board.add(L_0603_1608Metric, {
  translate: pt(1.054, 2.335), rotate: 0,
  id: 'TFB1'
})
// tp_pwr.tp
const TTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.561, 2.344), rotate: 0,
  id: 'TTP2'
})
// reg_3v3.ic
const TU1 = board.add(SOT_23_6, {
  translate: pt(2.841, 0.746), rotate: 0,
  id: 'TU1'
})
// reg_3v3.fb.div.top_res
const TR3 = board.add(R_0603_1608Metric, {
  translate: pt(2.945, 0.926), rotate: 0,
  id: 'TR3'
})
// reg_3v3.fb.div.bottom_res
const TR4 = board.add(R_0603_1608Metric, {
  translate: pt(2.598, 1.042), rotate: 0,
  id: 'TR4'
})
// reg_3v3.hf_in_cap.cap
const TC1 = board.add(C_0603_1608Metric, {
  translate: pt(2.754, 1.042), rotate: 0,
  id: 'TC1'
})
// reg_3v3.boot_cap
const TC2 = board.add(C_0603_1608Metric, {
  translate: pt(2.910, 1.042), rotate: 0,
  id: 'TC2'
})
// reg_3v3.power_path.inductor
const TL1 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(2.631, 0.769), rotate: 0,
  id: 'TL1'
})
// reg_3v3.power_path.in_cap.cap
const TC3 = board.add(C_0805_2012Metric, {
  translate: pt(2.607, 0.935), rotate: 0,
  id: 'TC3'
})
// reg_3v3.power_path.out_cap.cap
const TC4 = board.add(C_0805_2012Metric, {
  translate: pt(2.780, 0.935), rotate: 0,
  id: 'TC4'
})
// reg_3v3.en_res
const TR5 = board.add(R_0603_1608Metric, {
  translate: pt(2.598, 1.139), rotate: 0,
  id: 'TR5'
})
// tp_3v3.tp
const TTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.811, 2.344), rotate: 0,
  id: 'TTP3'
})
// prot_3v3.diode
const TD1 = board.add(D_SOD_323, {
  translate: pt(0.063, 2.344), rotate: 0,
  id: 'TD1'
})
// reg_3v0.ic
const TU2 = board.add(SOT_23_5, {
  translate: pt(1.852, 1.807), rotate: 0,
  id: 'TU2'
})
// reg_3v0.in_cap.cap
const TC5 = board.add(C_0603_1608Metric, {
  translate: pt(1.830, 1.942), rotate: 0,
  id: 'TC5'
})
// reg_3v0.out_cap.cap
const TC6 = board.add(C_0603_1608Metric, {
  translate: pt(1.986, 1.942), rotate: 0,
  id: 'TC6'
})
// reg_2v8.ic
const TU3 = board.add(SOT_23_5, {
  translate: pt(2.243, 1.807), rotate: 0,
  id: 'TU3'
})
// reg_2v8.in_cap.cap
const TC7 = board.add(C_0603_1608Metric, {
  translate: pt(2.220, 1.942), rotate: 0,
  id: 'TC7'
})
// reg_2v8.out_cap.cap
const TC8 = board.add(C_0603_1608Metric, {
  translate: pt(2.376, 1.942), rotate: 0,
  id: 'TC8'
})
// reg_1v2.ic
const TU4 = board.add(SOT_23_5, {
  translate: pt(1.462, 1.807), rotate: 0,
  id: 'TU4'
})
// reg_1v2.in_cap.cap
const TC9 = board.add(C_0603_1608Metric, {
  translate: pt(1.439, 1.942), rotate: 0,
  id: 'TC9'
})
// reg_1v2.out_cap.cap
const TC10 = board.add(C_0603_1608Metric, {
  translate: pt(1.595, 1.942), rotate: 0,
  id: 'TC10'
})
// mcu.ic
const TU5 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'TU5'
})
// mcu.vcc_cap0.cap
const TC11 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.419), rotate: 0,
  id: 'TC11'
})
// mcu.vcc_cap1.cap
const TC12 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.403), rotate: 0,
  id: 'TC12'
})
// mcu.prog.conn
const TJ2 = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(2.096, 0.167), rotate: 0,
  id: 'TJ2'
})
// mcu.en_pull.rc.r
const TR6 = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.403), rotate: 0,
  id: 'TR6'
})
// mcu.en_pull.rc.c
const TC13 = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.533), rotate: 0,
  id: 'TC13'
})
// usb_esd
const TU6 = board.add(SOT_23, {
  translate: pt(1.306, 2.374), rotate: 0,
  id: 'TU6'
})
// i2c_pull.scl_res.res
const TR7 = board.add(R_0603_1608Metric, {
  translate: pt(3.096, 1.769), rotate: 0,
  id: 'TR7'
})
// i2c_pull.sda_res.res
const TR8 = board.add(R_0603_1608Metric, {
  translate: pt(3.096, 1.866), rotate: 0,
  id: 'TR8'
})
// i2c_tp.tp_scl.tp
const TTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.619, 1.778), rotate: 0,
  id: 'TTP4'
})
// i2c_tp.tp_sda.tp
const TTP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.619, 1.892), rotate: 0,
  id: 'TTP5'
})
// touch_duck
const TU7 = board.add(Symbol_DucklingSolid, {
  translate: pt(1.578, 2.307), rotate: 0,
  id: 'TU7'
})
// ledr.package
const TD2 = board.add(LED_0603_1608Metric, {
  translate: pt(2.862, 1.769), rotate: 0,
  id: 'TD2'
})
// ledr.res
const TR9 = board.add(R_0603_1608Metric, {
  translate: pt(2.861, 1.866), rotate: 0,
  id: 'TR9'
})
// cam.device.conn.conn
const TJ3 = board.add(TE_2_1734839_4_1x24_1MP_P0_5mm_Horizontal, {
  translate: pt(0.900, 1.907), rotate: 0,
  id: 'TJ3'
})
// cam.dovdd_cap.cap
const TC14 = board.add(C_0603_1608Metric, {
  translate: pt(0.595, 2.070), rotate: 0,
  id: 'TC14'
})
// cam.reset_cap
const TC15 = board.add(C_0603_1608Metric, {
  translate: pt(0.751, 2.070), rotate: 0,
  id: 'TC15'
})
// cam.pclk_cap
const TC16 = board.add(C_0603_1608Metric, {
  translate: pt(0.907, 2.070), rotate: 0,
  id: 'TC16'
})
// flir.ic
const TU8 = board.add(Molex_1050281001, {
  translate: pt(2.772, 0.232), rotate: 0,
  id: 'TU8'
})
// flir.vddc_cap.cap
const TC17 = board.add(C_0603_1608Metric, {
  translate: pt(3.102, 0.202), rotate: 0,
  id: 'TC17'
})
// flir.vddio_cap.cap
const TC18 = board.add(C_0603_1608Metric, {
  translate: pt(3.102, 0.299), rotate: 0,
  id: 'TC18'
})
// flir.vdd_cap.cap
const TC19 = board.add(C_0603_1608Metric, {
  translate: pt(3.102, 0.396), rotate: 0,
  id: 'TC19'
})
// flir.mclk.device
const TX1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(3.127, 0.067), rotate: 0,
  id: 'TX1'
})
// flir.mclk.cap.cap
const TC20 = board.add(C_0603_1608Metric, {
  translate: pt(2.598, 0.533), rotate: 0,
  id: 'TC20'
})

board.setNetlist([
  {name: "Tgnd", pads: [["TU6", "3"], ["TJ1", "A1"], ["TJ1", "B12"], ["TJ1", "B1"], ["TJ1", "A12"], ["TTP1", "1"], ["TU1", "1"], ["TD1", "2"], ["TU2", "2"], ["TU3", "2"], ["TU4", "2"], ["TU5", "1"], ["TU5", "40"], ["TU5", "41"], ["TR9", "2"], ["TU8", "1"], ["TU8", "6"], ["TU8", "8"], ["TU8", "9"], ["TU8", "10"], ["TU8", "15"], ["TU8", "18"], ["TU8", "20"], ["TU8", "25"], ["TU8", "27"], ["TU8", "30"], ["TU8", "33"], ["TJ1", "S1"], ["TC15", "2"], ["TC16", "2"], ["TC1", "2"], ["TC5", "2"], ["TC6", "2"], ["TC7", "2"], ["TC8", "2"], ["TC9", "2"], ["TC10", "2"], ["TC11", "2"], ["TC12", "2"], ["TJ2", "5"], ["TC14", "2"], ["TC17", "2"], ["TC18", "2"], ["TC19", "2"], ["TX1", "2"], ["TR4", "2"], ["TC13", "2"], ["TJ3", "15"], ["TJ3", "2"], ["TR1", "1"], ["TR2", "1"], ["TC3", "2"], ["TC4", "2"], ["TJ3", "8"], ["TC20", "2"]]},
  {name: "Tpwr", pads: [["TFB1", "2"], ["TTP2", "1"], ["TU1", "3"], ["TR5", "1"], ["TC1", "1"], ["TC3", "1"]]},
  {name: "Tv3v3", pads: [["TTP3", "1"], ["TD1", "1"], ["TU2", "1"], ["TU3", "1"], ["TU4", "1"], ["TU5", "2"], ["TR3", "1"], ["TU2", "3"], ["TU3", "3"], ["TU4", "3"], ["TC5", "1"], ["TC7", "1"], ["TC9", "1"], ["TC11", "1"], ["TC12", "1"], ["TJ2", "1"], ["TR7", "1"], ["TR8", "1"], ["TR6", "1"], ["TL1", "2"], ["TC4", "1"]]},
  {name: "Tv3v0", pads: [["TU2", "5"], ["TU8", "16"], ["TC6", "1"], ["TC14", "1"], ["TC18", "1"], ["TX1", "1"], ["TX1", "4"], ["TJ3", "11"], ["TC20", "1"]]},
  {name: "Tv2v8", pads: [["TU3", "5"], ["TU8", "19"], ["TJ3", "4"], ["TC8", "1"], ["TC19", "1"]]},
  {name: "Tv1v2", pads: [["TU4", "5"], ["TU8", "7"], ["TJ3", "10"], ["TC10", "1"], ["TC17", "1"]]},
  {name: "Tusb.pwr", pads: [["TJ1", "A4"], ["TJ1", "B9"], ["TJ1", "B4"], ["TJ1", "A9"], ["TFB1", "1"]]},
  {name: "Tusb_chain_0.d_P", pads: [["TJ1", "A6"], ["TJ1", "B6"], ["TU6", "2"], ["TU5", "14"]]},
  {name: "Tusb_chain_0.d_N", pads: [["TJ1", "A7"], ["TJ1", "B7"], ["TU6", "1"], ["TU5", "13"]]},
  {name: "Ti2c_chain_0.scl", pads: [["TU5", "32"], ["TU8", "21"], ["TR7", "2"], ["TTP4", "1"], ["TJ3", "5"]]},
  {name: "Ti2c_chain_0.sda", pads: [["TU5", "31"], ["TU8", "22"], ["TR8", "2"], ["TJ3", "3"], ["TTP5", "1"]]},
  {name: "Ttouch_duck.pad", pads: [["TU5", "6"], ["TU7", "1"]]},
  {name: "Tmcu.program_boot_node", pads: [["TD2", "2"], ["TU5", "27"], ["TJ2", "2"]]},
  {name: "Tcam.dvp8.xclk", pads: [["TU5", "21"], ["TJ3", "13"]]},
  {name: "Tcam.dvp8.pclk", pads: [["TU5", "19"], ["TC16", "1"], ["TJ3", "17"]]},
  {name: "Tcam.dvp8.href", pads: [["TU5", "24"], ["TJ3", "9"]]},
  {name: "Tcam.dvp8.vsync", pads: [["TU5", "25"], ["TJ3", "7"]]},
  {name: "Tcam.dvp8.y0", pads: [["TU5", "18"], ["TJ3", "19"]]},
  {name: "Tcam.dvp8.y1", pads: [["TU5", "17"], ["TJ3", "21"]]},
  {name: "Tcam.dvp8.y2", pads: [["TU5", "11"], ["TJ3", "22"]]},
  {name: "Tcam.dvp8.y3", pads: [["TU5", "10"], ["TJ3", "20"]]},
  {name: "Tcam.dvp8.y4", pads: [["TU5", "12"], ["TJ3", "18"]]},
  {name: "Tcam.dvp8.y5", pads: [["TU5", "15"], ["TJ3", "16"]]},
  {name: "Tcam.dvp8.y6", pads: [["TU5", "20"], ["TJ3", "14"]]},
  {name: "Tcam.dvp8.y7", pads: [["TU5", "22"], ["TJ3", "12"]]},
  {name: "Tcam.reset", pads: [["TU5", "23"], ["TC15", "1"], ["TJ3", "6"]]},
  {name: "Tflir.spi.sck", pads: [["TU8", "13"], ["TU5", "39"]]},
  {name: "Tflir.spi.mosi", pads: [["TU8", "11"], ["TU5", "5"]]},
  {name: "Tflir.spi.miso", pads: [["TU8", "12"], ["TU5", "4"]]},
  {name: "Tflir.reset", pads: [["TU8", "24"], ["TU5", "34"]]},
  {name: "Tflir.shutdown", pads: [["TU8", "23"], ["TU5", "33"]]},
  {name: "Tflir.cs", pads: [["TU8", "14"], ["TU5", "38"]]},
  {name: "Tflir.vsync", pads: [["TU8", "2"], ["TU5", "7"]]},
  {name: "Tusb.conn.cc.cc1", pads: [["TJ1", "A5"], ["TR1", "2"]]},
  {name: "Tusb.conn.cc.cc2", pads: [["TJ1", "B5"], ["TR2", "2"]]},
  {name: "Treg_3v3.fb.output", pads: [["TU1", "4"], ["TR3", "2"], ["TR4", "1"]]},
  {name: "Treg_3v3.boot_cap.neg", pads: [["TC2", "2"], ["TU1", "2"], ["TL1", "1"]]},
  {name: "Treg_3v3.boot_cap.pos", pads: [["TC2", "1"], ["TU1", "6"]]},
  {name: "Treg_3v3.en_res.b", pads: [["TR5", "2"], ["TU1", "5"]]},
  {name: "Tmcu.program_uart_node.a_tx", pads: [["TU5", "37"], ["TJ2", "3"]]},
  {name: "Tmcu.program_uart_node.b_tx", pads: [["TU5", "36"], ["TJ2", "4"]]},
  {name: "Tmcu.program_en_node", pads: [["TU5", "3"], ["TJ2", "6"], ["TR6", "2"], ["TC13", "1"]]},
  {name: "Tledr.res.a", pads: [["TR9", "1"], ["TD2", "1"]]},
  {name: "Tcam.device.y.0", pads: [["TJ3", "24"]]},
  {name: "Tcam.device.y.1", pads: [["TJ3", "23"]]},
  {name: "Tflir.mclk.out", pads: [["TX1", "3"], ["TU8", "26"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.327559055118111, 2.4996062992125987);
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


