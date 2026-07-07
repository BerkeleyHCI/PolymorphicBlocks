const board = new PCB();

// jlc_th.th1
const JH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.593, 1.650), rotate: 0,
  id: 'JH1'
})
// jlc_th.th2
const JH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.633, 1.650), rotate: 0,
  id: 'JH2'
})
// jlc_th.th3
const JH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.593, 1.690), rotate: 0,
  id: 'JH3'
})
// bat.conn
const JJ1 = board.add(PinHeader_1x02_P2_00mm_Vertical, {
  translate: pt(1.109, 1.439), rotate: 0,
  id: 'JJ1'
})
// usb.conn
const JJ2 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.532, 0.165), rotate: 0,
  id: 'JJ2'
})
// usb.esd
const JU1 = board.add(SOT_23, {
  translate: pt(1.857, 0.067), rotate: 0,
  id: 'JU1'
})
// usb.cc_pull.cc1
const JR1 = board.add(R_0603_1608Metric, {
  translate: pt(1.839, 0.202), rotate: 0,
  id: 'JR1'
})
// usb.cc_pull.cc2
const JR2 = board.add(R_0603_1608Metric, {
  translate: pt(1.839, 0.299), rotate: 0,
  id: 'JR2'
})
// tp_usb.tp
const JTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.908, 1.688), rotate: 0,
  id: 'JTP1'
})
// tp_gnd.tp
const JTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.159, 1.688), rotate: 0,
  id: 'JTP2'
})
// vbat_sense.ic
const JU2 = board.add(SOT_23_8, {
  translate: pt(1.106, 0.067), rotate: 0,
  id: 'JU2'
})
// vbat_sense.Rs.res.res
const JR3 = board.add(R_1206_3216Metric, {
  translate: pt(1.115, 0.217), rotate: 0,
  id: 'JR3'
})
// vbat_sense.vs_cap.cap
const JC1 = board.add(C_0603_1608Metric, {
  translate: pt(1.083, 0.330), rotate: 0,
  id: 'JC1'
})
// gate.pull_res
const JR4 = board.add(R_0603_1608Metric, {
  translate: pt(0.860, 1.038), rotate: 0,
  id: 'JR4'
})
// gate.pwr_fet
const JQ1 = board.add(SOT_23, {
  translate: pt(0.546, 0.903), rotate: 0,
  id: 'JQ1'
})
// gate.amp_res
const JR5 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 1.152), rotate: 0,
  id: 'JR5'
})
// gate.amp_fet
const JQ2 = board.add(SOT_23, {
  translate: pt(0.736, 0.903), rotate: 0,
  id: 'JQ2'
})
// gate.ctl_diode
const JD1 = board.add(D_SOD_323, {
  translate: pt(0.533, 1.047), rotate: 0,
  id: 'JD1'
})
// gate.btn_diode
const JD2 = board.add(D_SOD_323, {
  translate: pt(0.699, 1.047), rotate: 0,
  id: 'JD2'
})
// reg_3v3.ic
const JU3 = board.add(SOT_23, {
  translate: pt(0.076, 1.369), rotate: 0,
  id: 'JU3'
})
// reg_3v3.in_cap.cap
const JC2 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.504), rotate: 0,
  id: 'JC2'
})
// reg_3v3.out_cap.cap
const JC3 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.504), rotate: 0,
  id: 'JC3'
})
// tp_3v3.tp
const JTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.409, 1.688), rotate: 0,
  id: 'JTP3'
})
// prot_3v3.diode
const JD3 = board.add(D_SOD_123, {
  translate: pt(0.631, 1.696), rotate: 0,
  id: 'JD3'
})
// chg.ic
const JU4 = board.add(SOT_23_5, {
  translate: pt(0.081, 0.903), rotate: 0,
  id: 'JU4'
})
// chg.vdd_cap.cap
const JC4 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 1.048), rotate: 0,
  id: 'JC4'
})
// chg.vbat_cap.cap
const JC5 = board.add(C_0805_2012Metric, {
  translate: pt(0.240, 1.048), rotate: 0,
  id: 'JC5'
})
// chg.prog_res.res
const JR6 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.155), rotate: 0,
  id: 'JR6'
})
// chg.prog_sw
const JQ3 = board.add(SOT_23, {
  translate: pt(0.276, 0.903), rotate: 0,
  id: 'JQ3'
})
// mcu.ic.device
const JU5 = board.add(Holyiot_18010_NRF52840, {
  translate: pt(0.290, 0.324), rotate: 0,
  id: 'JU5'
})
// mcu.vcc_cap.cap
const JC6 = board.add(C_0805_2012Metric, {
  translate: pt(0.667, 0.235), rotate: 0,
  id: 'JC6'
})
// mcu.swd.conn
const JJ3 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(0.738, 0.079), rotate: 0,
  id: 'JJ3'
})
// mcu.vbus_cap.cap
const JC7 = board.add(C_0805_2012Metric, {
  translate: pt(0.840, 0.235), rotate: 0,
  id: 'JC7'
})
// mcu.usb_res.dp
const JR7 = board.add(R_0603_1608Metric, {
  translate: pt(0.658, 0.342), rotate: 0,
  id: 'JR7'
})
// mcu.usb_res.dm
const JR8 = board.add(R_0603_1608Metric, {
  translate: pt(0.814, 0.342), rotate: 0,
  id: 'JR8'
})
// ledr.package
const JD4 = board.add(LED_0603_1608Metric, {
  translate: pt(1.930, 1.331), rotate: 0,
  id: 'JD4'
})
// ledr.res
const JR9 = board.add(R_0603_1608Metric, {
  translate: pt(1.930, 1.428), rotate: 0,
  id: 'JR9'
})
// bumper_sw.package
const JSW1 = board.add(SW_SPST_EVQP7C, {
  translate: pt(1.645, 1.394), rotate: 0,
  id: 'JSW1'
})
// i2c_pull.scl_res.res
const JR10 = board.add(R_0603_1608Metric, {
  translate: pt(2.165, 1.330), rotate: 0,
  id: 'JR10'
})
// i2c_pull.sda_res.res
const JR11 = board.add(R_0603_1608Metric, {
  translate: pt(2.165, 1.427), rotate: 0,
  id: 'JR11'
})
// tp_i2c.tp_scl.tp
const JTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.353, 1.339), rotate: 0,
  id: 'JTP4'
})
// tp_i2c.tp_sda.tp
const JTP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.353, 1.453), rotate: 0,
  id: 'JTP5'
})
// imu.ic
const JU6 = board.add(Bosch_LGA_14_3x2_5mm_P0_5mm, {
  translate: pt(0.733, 1.365), rotate: 0,
  id: 'JU6'
})
// imu.vdd_cap.cap
const JC8 = board.add(C_0603_1608Metric, {
  translate: pt(0.718, 1.496), rotate: 0,
  id: 'JC8'
})
// imu.vddio_cap.cap
const JC9 = board.add(C_0603_1608Metric, {
  translate: pt(0.874, 1.496), rotate: 0,
  id: 'JC9'
})
// mag.ic
const JU7 = board.add(LGA_16_3x3mm_P0_5mm, {
  translate: pt(2.137, 0.905), rotate: 0,
  id: 'JU7'
})
// mag.vdd_cap.cap
const JC10 = board.add(C_0603_1608Metric, {
  translate: pt(2.299, 1.042), rotate: 0,
  id: 'JC10'
})
// mag.c1.cap
const JC11 = board.add(C_0805_2012Metric, {
  translate: pt(2.135, 1.052), rotate: 0,
  id: 'JC11'
})
// stick.conn.ext
const JJ4 = board.add(Hirose_FH12_8S_0_5SH_1x08_1MP_P0_50mm_Horizontal, {
  translate: pt(1.235, 1.029), rotate: 0,
  id: 'JJ4'
})
// stick_gate.fet
const JQ4 = board.add(SOT_23, {
  translate: pt(0.076, 1.717), rotate: 0,
  id: 'JQ4'
})
// trig.ic
const JU9 = board.add(SOT_23, {
  translate: pt(0.466, 1.369), rotate: 0,
  id: 'JU9'
})
// trig.cbyp.cap
const JC12 = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 1.504), rotate: 0,
  id: 'JC12'
})
// trig_gate.fet
const JQ5 = board.add(SOT_23, {
  translate: pt(0.345, 1.717), rotate: 0,
  id: 'JQ5'
})
// btns.conn.ext
const JJ7 = board.add(Hirose_FH12_8S_0_5SH_1x08_1MP_P0_50mm_Horizontal, {
  translate: pt(1.751, 1.029), rotate: 0,
  id: 'JJ7'
})

board.setNetlist([
  {name: "vbat", pads: [["JJ1", "2"], ["JR4", "1"], ["JQ1", "2"], ["JU4", "3"], ["JC5", "1"]]},
  {name: "vusb", pads: [["JJ2", "A4"], ["JJ2", "A9"], ["JJ2", "B4"], ["JJ2", "B9"], ["JTP1", "1"], ["JU4", "4"], ["JC4", "1"], ["JU5", "22"], ["JC7", "1"]]},
  {name: "gnd", pads: [["JJ1", "1"], ["JJ2", "A1"], ["JJ2", "A12"], ["JJ2", "B1"], ["JJ2", "B12"], ["JJ2", "S1"], ["JU1", "3"], ["JR1", "1"], ["JR2", "1"], ["JTP2", "1"], ["JU2", "3"], ["JU2", "7"], ["JU2", "8"], ["JC1", "2"], ["JR5", "1"], ["JQ2", "2"], ["JU3", "1"], ["JC2", "2"], ["JC3", "2"], ["JD3", "2"], ["JU4", "2"], ["JC4", "2"], ["JC5", "2"], ["JQ3", "2"], ["JU5", "1"], ["JU5", "25"], ["JU5", "37"], ["JC6", "2"], ["JJ3", "5"], ["JC7", "2"], ["JR9", "2"], ["JSW1", "2"], ["JU6", "1"], ["JU6", "2"], ["JU6", "3"], ["JU6", "6"], ["JU6", "7"], ["JC8", "2"], ["JC9", "2"], ["JU7", "11"], ["JU7", "9"], ["JC10", "2"], ["JC11", "2"], ["JJ4", "1"], ["JJ4", "8"], ["JU9", "3"], ["JC12", "2"], ["JJ7", "1"], ["JJ7", "6"]]},
  {name: "vbat_gated", pads: [["JU2", "2"], ["JR3", "2"], ["JU3", "3"], ["JC2", "1"], ["JJ7", "7"], ["JJ7", "8"]]},
  {name: "v3v3", pads: [["JU2", "4"], ["JC1", "1"], ["JU3", "2"], ["JC3", "1"], ["JTP3", "1"], ["JD3", "1"], ["JU5", "14"], ["JC6", "1"], ["JJ3", "1"], ["JR10", "1"], ["JR11", "1"], ["JU6", "12"], ["JU6", "5"], ["JU6", "8"], ["JC8", "1"], ["JC9", "1"], ["JU7", "2"], ["JC10", "1"], ["JQ4", "2"], ["JQ5", "2"], ["JJ7", "2"]]},
  {name: "usb.usb.dp", pads: [["JJ2", "A6"], ["JJ2", "B6"], ["JU1", "2"], ["JR7", "1"]]},
  {name: "usb.usb.dm", pads: [["JJ2", "A7"], ["JJ2", "B7"], ["JU1", "1"], ["JR8", "1"]]},
  {name: "usb.conn.cc.cc1", pads: [["JJ2", "A5"], ["JR1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["JJ2", "B5"], ["JR2", "2"]]},
  {name: "vbat_sense.i2c.scl", pads: [["JU2", "5"], ["JU5", "26"], ["JR10", "2"], ["JTP4", "1"], ["JU6", "13"], ["JU7", "1"], ["JJ7", "3"]]},
  {name: "vbat_sense.i2c.sda", pads: [["JU2", "6"], ["JU5", "27"], ["JR11", "2"], ["JTP5", "1"], ["JU6", "14"], ["JU7", "16"], ["JJ7", "4"]]},
  {name: "vbat_sense.sense_pwr_in", pads: [["JU2", "1"], ["JR3", "1"], ["JQ1", "3"]]},
  {name: "gate.btn_out", pads: [["JD2", "2"], ["JU5", "13"]]},
  {name: "gate.btn_in", pads: [["JD1", "1"], ["JD2", "1"], ["JJ4", "6"]]},
  {name: "gate.control", pads: [["JR5", "2"], ["JQ2", "1"], ["JU5", "15"]]},
  {name: "gate.pull_res.b", pads: [["JR4", "2"], ["JQ1", "1"], ["JQ2", "3"], ["JD1", "2"]]},
  {name: "chg.stat", pads: [["JU4", "1"]]},
  {name: "chg.prog_ctl", pads: [["JQ3", "1"], ["JU5", "2"]]},
  {name: "chg.ic.prog", pads: [["JU4", "5"], ["JR6", "2"]]},
  {name: "chg.prog_res.gnd", pads: [["JR6", "1"], ["JQ3", "3"]]},
  {name: "mcu.swd_node.swdio", pads: [["JU5", "32"], ["JJ3", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["JU5", "31"], ["JJ3", "4"]]},
  {name: "mcu.reset_node", pads: [["JU5", "21"], ["JJ3", "3"]]},
  {name: "mcu.swd.swo", pads: [["JJ3", "6"]]},
  {name: "mcu.usb_res.interior.dp", pads: [["JU5", "24"], ["JR7", "2"]]},
  {name: "mcu.usb_res.interior.dm", pads: [["JU5", "23"], ["JR8", "2"]]},
  {name: "ledr.signal", pads: [["JU5", "10"], ["JD4", "2"]]},
  {name: "ledr.package.k", pads: [["JD4", "1"], ["JR9", "1"]]},
  {name: "bumper_sw.out", pads: [["JU5", "11"], ["JSW1", "1"]]},
  {name: "imu.int1", pads: [["JU6", "4"]]},
  {name: "imu.int2", pads: [["JU6", "9"]]},
  {name: "mag.ic.c1", pads: [["JU7", "10"], ["JC11", "1"]]},
  {name: "stick.pwr", pads: [["JJ4", "2"], ["JQ4", "3"]]},
  {name: "stick.ax1", pads: [["JU5", "8"], ["JJ4", "4"]]},
  {name: "stick.ax2", pads: [["JU5", "9"], ["JJ4", "3"]]},
  {name: "stick_gate.control", pads: [["JU5", "3"], ["JQ4", "1"]]},
  {name: "trig.pwr", pads: [["JU9", "1"], ["JC12", "1"], ["JQ5", "3"]]},
  {name: "trig.out", pads: [["JU5", "6"], ["JU9", "2"]]},
  {name: "trig_gate.control", pads: [["JU5", "12"], ["JQ5", "1"]]},
  {name: "btns.io0", pads: [["JU5", "20"], ["JJ7", "5"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.4755905511811025, 1.9023622047244095);
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


