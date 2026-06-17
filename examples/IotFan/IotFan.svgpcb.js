const board = new PCB();

// jlc_th.th1
const FH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.236, 1.664), rotate: 0,
  id: 'FH1'
})
// jlc_th.th2
const FH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.276, 1.664), rotate: 0,
  id: 'FH2'
})
// jlc_th.th3
const FH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.236, 1.703), rotate: 0,
  id: 'FH3'
})
// pwr
const FJ1 = board.add(BarrelJack_CUI_PJ_036AH_SMT_Horizontal, {
  translate: pt(1.650, 0.413), rotate: 0,
  id: 'FJ1'
})
// usb.conn
const FJ2 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.635, 0.972), rotate: 0,
  id: 'FJ2'
})
// tp_vin.tp
const FTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 1.701), rotate: 0,
  id: 'FTP1'
})
// tp_gnd.tp
const FTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 1.701), rotate: 0,
  id: 'FTP2'
})
// vin_sense.ic
const FU1 = board.add(SOT_23_8, {
  translate: pt(0.081, 1.382), rotate: 0,
  id: 'FU1'
})
// vin_sense.Rs.res.res
const FR1 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.517), rotate: 0,
  id: 'FR1'
})
// vin_sense.vs_cap.cap
const FC1 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.517), rotate: 0,
  id: 'FC1'
})
// reg_5v.ic
const FU2 = board.add(SOT_23_6, {
  translate: pt(2.380, 0.067), rotate: 0,
  id: 'FU2'
})
// reg_5v.fb.div.top_res
const FR2 = board.add(R_0603_1608Metric, {
  translate: pt(2.444, 0.285), rotate: 0,
  id: 'FR2'
})
// reg_5v.fb.div.bottom_res
const FR3 = board.add(R_0603_1608Metric, {
  translate: pt(2.098, 0.401), rotate: 0,
  id: 'FR3'
})
// reg_5v.hf_in_cap.cap
const FC2 = board.add(C_0603_1608Metric, {
  translate: pt(2.254, 0.401), rotate: 0,
  id: 'FC2'
})
// reg_5v.boot_cap.cap
const FC3 = board.add(C_0603_1608Metric, {
  translate: pt(2.409, 0.401), rotate: 0,
  id: 'FC3'
})
// reg_5v.power_path.inductor
const FL1 = board.add(L_Taiyo_Yuden_NR_50xx, {
  translate: pt(2.150, 0.108), rotate: 0,
  id: 'FL1'
})
// reg_5v.power_path.in_cap.cap
const FC4 = board.add(C_0805_2012Metric, {
  translate: pt(2.106, 0.294), rotate: 0,
  id: 'FC4'
})
// reg_5v.power_path.out_cap.cap
const FC5 = board.add(C_0805_2012Metric, {
  translate: pt(2.280, 0.294), rotate: 0,
  id: 'FC5'
})
// reg_5v.en_res.res
const FR4 = board.add(R_0603_1608Metric, {
  translate: pt(2.098, 0.498), rotate: 0,
  id: 'FR4'
})
// tp_5v.tp
const FTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.567, 1.701), rotate: 0,
  id: 'FTP3'
})
// prot_5v.diode
const FD1 = board.add(D_SOD_123, {
  translate: pt(1.980, 1.360), rotate: 0,
  id: 'FD1'
})
// reg_3v3.ic
const FU3 = board.add(SOT_23_6, {
  translate: pt(1.043, 0.874), rotate: 0,
  id: 'FU3'
})
// reg_3v3.fb.div.top_res
const FR5 = board.add(R_0603_1608Metric, {
  translate: pt(1.198, 1.009), rotate: 0,
  id: 'FR5'
})
// reg_3v3.fb.div.bottom_res
const FR6 = board.add(R_0603_1608Metric, {
  translate: pt(1.354, 1.009), rotate: 0,
  id: 'FR6'
})
// reg_3v3.hf_in_cap.cap
const FC6 = board.add(C_0603_1608Metric, {
  translate: pt(1.020, 1.115), rotate: 0,
  id: 'FC6'
})
// reg_3v3.boot_cap.cap
const FC7 = board.add(C_0603_1608Metric, {
  translate: pt(1.176, 1.115), rotate: 0,
  id: 'FC7'
})
// reg_3v3.power_path.inductor
const FL2 = board.add(L_0805_2012Metric, {
  translate: pt(1.031, 1.014), rotate: 0,
  id: 'FL2'
})
// reg_3v3.power_path.in_cap.cap
const FC8 = board.add(C_0805_2012Metric, {
  translate: pt(1.230, 0.846), rotate: 0,
  id: 'FC8'
})
// reg_3v3.power_path.out_cap.cap
const FC9 = board.add(C_0805_2012Metric, {
  translate: pt(1.403, 0.846), rotate: 0,
  id: 'FC9'
})
// reg_3v3.en_res.res
const FR7 = board.add(R_0603_1608Metric, {
  translate: pt(1.332, 1.115), rotate: 0,
  id: 'FR7'
})
// tp_3v3.tp
const FTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.817, 1.701), rotate: 0,
  id: 'FTP4'
})
// prot_3v3.diode
const FD2 = board.add(D_SOD_123, {
  translate: pt(2.283, 1.360), rotate: 0,
  id: 'FD2'
})
// control.conn1.ext
const FJ6 = board.add(PinSocket_1x08_P2_00mm_Vertical, {
  translate: pt(0.965, 0.610), rotate: 0,
  id: 'FJ6'
})
// control.conn2.ext
const FJ8 = board.add(PinSocket_1x08_P2_00mm_Vertical, {
  translate: pt(1.122, 0.610), rotate: 0,
  id: 'FJ8'
})
// enc.package
const FSW1 = board.add(RotaryEncoder_Alps_EC11J15_Switch, {
  translate: pt(0.394, 0.344), rotate: 0,
  id: 'FSW1'
})
// pd.ic
const FU8 = board.add(WQFN_14_1EP_2_5x2_5mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(2.207, 0.880), rotate: 0,
  id: 'FU8'
})
// pd.vdd_cap[0].cap
const FC24 = board.add(C_0603_1608Metric, {
  translate: pt(2.366, 1.021), rotate: 0,
  id: 'FC24'
})
// pd.vdd_cap[1].cap
const FC25 = board.add(C_0805_2012Metric, {
  translate: pt(2.202, 1.031), rotate: 0,
  id: 'FC25'
})
// spk_dac.rc.r
const FR19 = board.add(R_0603_1608Metric, {
  translate: pt(1.441, 1.344), rotate: 0,
  id: 'FR19'
})
// spk_dac.rc.c
const FC26 = board.add(C_0603_1608Metric, {
  translate: pt(1.441, 1.441), rotate: 0,
  id: 'FC26'
})
// spk_drv.ic
const FU9 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(1.711, 0.876), rotate: 0,
  id: 'FU9'
})
// spk_drv.pwr_cap.cap
const FC27 = board.add(C_0603_1608Metric, {
  translate: pt(1.646, 1.013), rotate: 0,
  id: 'FC27'
})
// spk_drv.bulk_cap.cap
const FC28 = board.add(C_0805_2012Metric, {
  translate: pt(1.940, 0.846), rotate: 0,
  id: 'FC28'
})
// spk_drv.inp_res.res
const FR20 = board.add(R_0603_1608Metric, {
  translate: pt(1.802, 1.013), rotate: 0,
  id: 'FR20'
})
// spk_drv.inp_cap.cap
const FC29 = board.add(C_0603_1608Metric, {
  translate: pt(1.958, 1.013), rotate: 0,
  id: 'FC29'
})
// spk_drv.inn_res.res
const FR21 = board.add(R_0603_1608Metric, {
  translate: pt(1.646, 1.110), rotate: 0,
  id: 'FR21'
})
// spk_drv.inn_cap.cap
const FC30 = board.add(C_0603_1608Metric, {
  translate: pt(1.802, 1.110), rotate: 0,
  id: 'FC30'
})
// spk.conn
const FJ10 = board.add(PinHeader_1x02_P2_00mm_Vertical, {
  translate: pt(0.729, 1.453), rotate: 0,
  id: 'FJ10'
})
// npx_shift.ic
const FU10 = board.add(SOT_23_5, {
  translate: pt(0.471, 1.382), rotate: 0,
  id: 'FU10'
})
// npx_shift.vdd_cap.cap
const FC31 = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 1.517), rotate: 0,
  id: 'FC31'
})
// npx_res.res
const FR22 = board.add(R_0603_1608Metric, {
  translate: pt(1.060, 1.693), rotate: 0,
  id: 'FR22'
})
// fan
const FJ11 = board.add(FanPinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.975, 1.465), rotate: 0,
  id: 'FJ11'
})
// fan_drv.pre
const FQ1 = board.add(SOT_23, {
  translate: pt(0.076, 1.130), rotate: 0,
  id: 'FQ1'
})
// fan_drv.pull
const FR23 = board.add(R_0603_1608Metric, {
  translate: pt(0.249, 1.092), rotate: 0,
  id: 'FR23'
})
// fan_drv.drv
const FQ2 = board.add(PQFN_8_EP_6x5mm_P1_27mm_Generic, {
  translate: pt(0.130, 0.915), rotate: 0,
  id: 'FQ2'
})
// fan_ctl.drv
const FQ3 = board.add(SOT_23, {
  translate: pt(1.693, 1.382), rotate: 0,
  id: 'FQ3'
})

board.setNetlist([
  {name: "Fgnd", pads: [["FJ1", "2"], ["FJ2", "A1"], ["FJ2", "A12"], ["FJ2", "B1"], ["FJ2", "B12"], ["FJ2", "S1"], ["FTP2", "1"], ["FU1", "3"], ["FU1", "7"], ["FU1", "8"], ["FC1", "2"], ["FU2", "1"], ["FR3", "2"], ["FC2", "2"], ["FC4", "2"], ["FC5", "2"], ["FD1", "2"], ["FU3", "1"], ["FR6", "2"], ["FC6", "2"], ["FC8", "2"], ["FC9", "2"], ["FD2", "2"], ["FJ6", "8"], ["FJ8", "8"], ["FSW1", "C"], ["FSW1", "S2"], ["FU8", "15"], ["FU8", "8"], ["FU8", "9"], ["FC24", "2"], ["FC25", "2"], ["FC26", "2"], ["FU9", "7"], ["FU9", "9"], ["FC27", "2"], ["FC28", "2"], ["FC30", "2"], ["FU10", "3"], ["FC31", "2"], ["FJ11", "1"], ["FQ1", "2"], ["FQ3", "2"]]},
  {name: "Fvin", pads: [["FU1", "2"], ["FR1", "2"], ["FU2", "3"], ["FC2", "1"], ["FC4", "1"], ["FR4", "1"], ["FR23", "1"], ["FQ2", "1"], ["FQ2", "2"], ["FQ2", "3"]]},
  {name: "Fv5", pads: [["FR2", "1"], ["FL1", "2"], ["FC5", "1"], ["FTP3", "1"], ["FD1", "1"], ["FU3", "3"], ["FC6", "1"], ["FC8", "1"], ["FR7", "1"], ["FJ8", "1"], ["FU9", "1"], ["FU9", "6"], ["FC27", "1"], ["FC28", "1"], ["FU10", "5"], ["FC31", "1"]]},
  {name: "Fv3v3", pads: [["FU1", "4"], ["FC1", "1"], ["FR5", "1"], ["FL2", "2"], ["FC9", "1"], ["FTP4", "1"], ["FD2", "1"], ["FJ6", "1"], ["FU8", "3"], ["FU8", "4"], ["FC24", "1"], ["FC25", "1"]]},
  {name: "Fpwr.pwr", pads: [["FJ1", "1"], ["FJ2", "A4"], ["FJ2", "A9"], ["FJ2", "B4"], ["FJ2", "B9"], ["FTP1", "1"], ["FU1", "1"], ["FR1", "1"], ["FU8", "2"]]},
  {name: "Fusb.usb.dp", pads: [["FJ2", "A6"], ["FJ2", "B6"]]},
  {name: "Fusb.usb.dm", pads: [["FJ2", "A7"], ["FJ2", "B7"]]},
  {name: "Fusb.cc.cc1", pads: [["FJ2", "A5"], ["FU8", "10"], ["FU8", "11"]]},
  {name: "Fusb.cc.cc2", pads: [["FJ2", "B5"], ["FU8", "1"], ["FU8", "14"]]},
  {name: "Fvin_sense.i2c.scl", pads: [["FU1", "5"], ["FJ6", "6"], ["FU8", "6"]]},
  {name: "Fvin_sense.i2c.sda", pads: [["FU1", "6"], ["FJ6", "7"], ["FU8", "7"]]},
  {name: "Freg_5v.ic.sw", pads: [["FU2", "2"], ["FC3", "2"], ["FL1", "1"]]},
  {name: "Freg_5v.ic.fb", pads: [["FU2", "4"], ["FR2", "2"], ["FR3", "1"]]},
  {name: "Freg_5v.ic.boot", pads: [["FU2", "6"], ["FC3", "1"]]},
  {name: "Freg_5v.ic.en", pads: [["FU2", "5"], ["FR4", "2"]]},
  {name: "Freg_3v3.ic.sw", pads: [["FU3", "2"], ["FC7", "2"], ["FL2", "1"]]},
  {name: "Freg_3v3.ic.fb", pads: [["FU3", "4"], ["FR5", "2"], ["FR6", "1"]]},
  {name: "Freg_3v3.ic.boot", pads: [["FU3", "6"], ["FC7", "1"]]},
  {name: "Freg_3v3.ic.en", pads: [["FU3", "5"], ["FR7", "2"]]},
  {name: "Fcontrol.pd_int", pads: [["FJ6", "5"], ["FU8", "5"]]},
  {name: "Fcontrol.spk", pads: [["FJ6", "4"], ["FR19", "1"]]},
  {name: "Fcontrol.drv", pads: [["FJ8", "3"], ["FQ1", "1"]]},
  {name: "Fcontrol.tach", pads: [["FJ8", "2"], ["FJ11", "3"]]},
  {name: "Fcontrol.pwm", pads: [["FJ6", "3"], ["FU10", "2"], ["FQ3", "1"]]},
  {name: "Fcontrol.npx_en", pads: [["FJ6", "2"], ["FU10", "1"]]},
  {name: "Fcontrol.enc_a", pads: [["FJ8", "5"], ["FSW1", "A"]]},
  {name: "Fcontrol.enc_b", pads: [["FJ8", "6"], ["FSW1", "B"]]},
  {name: "Fcontrol.enc_sw", pads: [["FJ8", "7"], ["FSW1", "S1"]]},
  {name: "Fcontrol.extra1", pads: [["FJ8", "4"]]},
  {name: "Fpd.ic.vconn", pads: [["FU8", "12"], ["FU8", "13"]]},
  {name: "Fspk_dac.output", pads: [["FR19", "2"], ["FC26", "1"], ["FC29", "2"]]},
  {name: "Fspk_drv.spk.a", pads: [["FU9", "8"], ["FJ10", "1"]]},
  {name: "Fspk_drv.spk.b", pads: [["FU9", "5"], ["FJ10", "2"]]},
  {name: "Fspk_drv.ic.inp", pads: [["FU9", "4"], ["FR20", "2"]]},
  {name: "Fspk_drv.ic.inn", pads: [["FU9", "3"], ["FR21", "2"]]},
  {name: "Fspk_drv.inp_res.input", pads: [["FR20", "1"], ["FC29", "1"]]},
  {name: "Fspk_drv.inn_res.input", pads: [["FR21", "1"], ["FC30", "1"]]},
  {name: "Fnpx_shift.output", pads: [["FU10", "4"], ["FR22", "1"]]},
  {name: "Fnpx_res.output", pads: [["FR22", "2"], ["FJ11", "4"], ["FQ3", "3"]]},
  {name: "Ffan.pwr", pads: [["FJ11", "2"], ["FQ2", "5"]]},
  {name: "Ffan_drv.pre.drain", pads: [["FQ1", "3"], ["FR23", "2"], ["FQ2", "4"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.6204724409448823, 1.8566929133858268);
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


