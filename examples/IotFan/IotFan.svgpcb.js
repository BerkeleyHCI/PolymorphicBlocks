const board = new PCB();

// jlc_th.th1
const FH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.475, 1.908), rotate: 0,
  id: 'FH1'
})
// jlc_th.th2
const FH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.514, 1.908), rotate: 0,
  id: 'FH2'
})
// jlc_th.th3
const FH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.475, 1.947), rotate: 0,
  id: 'FH3'
})
// pwr
const FJ1 = board.add(BarrelJack_CUI_PJ_036AH_SMT_Horizontal, {
  translate: pt(1.514, 0.413), rotate: 0,
  id: 'FJ1'
})
// usb.conn
const FJ2 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.439, 0.972), rotate: 0,
  id: 'FJ2'
})
// tp_vin.tp
const FTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.106, 1.596), rotate: 0,
  id: 'FTP1'
})
// tp_gnd.tp
const FTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.357, 1.596), rotate: 0,
  id: 'FTP2'
})
// vin_sense.ic
const FU1 = board.add(SOT_23_8, {
  translate: pt(0.081, 1.626), rotate: 0,
  id: 'FU1'
})
// vin_sense.vs_cap.cap
const FC1 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.761), rotate: 0,
  id: 'FC1'
})
// vin_sense.Rs.res.res
const FR1 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 1.761), rotate: 0,
  id: 'FR1'
})
// reg_5v.ic
const FU2 = board.add(SOT_23_6, {
  translate: pt(0.520, 0.874), rotate: 0,
  id: 'FU2'
})
// reg_5v.fb.div.top_res
const FR2 = board.add(R_0603_1608Metric, {
  translate: pt(0.316, 1.144), rotate: 0,
  id: 'FR2'
})
// reg_5v.fb.div.bottom_res
const FR3 = board.add(R_0603_1608Metric, {
  translate: pt(0.472, 1.144), rotate: 0,
  id: 'FR3'
})
// reg_5v.hf_in_cap.cap
const FC2 = board.add(C_0603_1608Metric, {
  translate: pt(0.628, 1.144), rotate: 0,
  id: 'FC2'
})
// reg_5v.boot_cap.cap
const FC3 = board.add(C_0603_1608Metric, {
  translate: pt(0.316, 1.241), rotate: 0,
  id: 'FC3'
})
// reg_5v.power_path.inductor
const FL1 = board.add(L_Sunlord_SWPA3015S, {
  translate: pt(0.329, 0.876), rotate: 0,
  id: 'FL1'
})
// reg_5v.power_path.in_cap.cap
const FC4 = board.add(C_1206_3216Metric, {
  translate: pt(0.348, 1.030), rotate: 0,
  id: 'FC4'
})
// reg_5v.power_path.out_cap.cap
const FC5 = board.add(C_1206_3216Metric, {
  translate: pt(0.569, 1.030), rotate: 0,
  id: 'FC5'
})
// reg_5v.en_res.res
const FR4 = board.add(R_0603_1608Metric, {
  translate: pt(0.472, 1.241), rotate: 0,
  id: 'FR4'
})
// tp_5v.tp
const FTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 1.945), rotate: 0,
  id: 'FTP3'
})
// prot_5v.diode
const FD1 = board.add(D_SOD_323, {
  translate: pt(0.314, 1.945), rotate: 0,
  id: 'FD1'
})
// reg_3v3.ic
const FU3 = board.add(SOT_23_6, {
  translate: pt(2.205, 0.067), rotate: 0,
  id: 'FU3'
})
// reg_3v3.fb.div.top_res
const FR5 = board.add(R_0603_1608Metric, {
  translate: pt(2.403, 0.246), rotate: 0,
  id: 'FR5'
})
// reg_3v3.fb.div.bottom_res
const FR6 = board.add(R_0603_1608Metric, {
  translate: pt(1.962, 0.376), rotate: 0,
  id: 'FR6'
})
// reg_3v3.hf_in_cap.cap
const FC6 = board.add(C_0603_1608Metric, {
  translate: pt(2.118, 0.376), rotate: 0,
  id: 'FC6'
})
// reg_3v3.boot_cap.cap
const FC7 = board.add(C_0603_1608Metric, {
  translate: pt(2.274, 0.376), rotate: 0,
  id: 'FC7'
})
// reg_3v3.power_path.inductor
const FL2 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(1.994, 0.089), rotate: 0,
  id: 'FL2'
})
// reg_3v3.power_path.in_cap.cap
const FC8 = board.add(C_1206_3216Metric, {
  translate: pt(1.994, 0.263), rotate: 0,
  id: 'FC8'
})
// reg_3v3.power_path.out_cap.cap
const FC9 = board.add(C_1206_3216Metric, {
  translate: pt(2.215, 0.263), rotate: 0,
  id: 'FC9'
})
// reg_3v3.en_res.res
const FR7 = board.add(R_0603_1608Metric, {
  translate: pt(1.962, 0.473), rotate: 0,
  id: 'FR7'
})
// tp_3v3.tp
const FTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.561, 1.945), rotate: 0,
  id: 'FTP4'
})
// prot_3v3.diode
const FD2 = board.add(D_SOD_323, {
  translate: pt(0.809, 1.945), rotate: 0,
  id: 'FD2'
})
// control.conn.ext
const FJ5 = board.add(PinSocket_1x14_P2_54mm_Vertical, {
  translate: pt(0.071, 1.370), rotate: 0,
  id: 'FJ5'
})
// enc.package
const FSW1 = board.add(RotaryEncoder_Alps_EC11J15_Switch, {
  translate: pt(0.652, 0.344), rotate: 0,
  id: 'FSW1'
})
// pd.ic
const FU8 = board.add(WQFN_14_1EP_2_5x2_5mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(2.247, 0.880), rotate: 0,
  id: 'FU8'
})
// pd.vdd_cap[0].cap
const FC24 = board.add(C_0603_1608Metric, {
  translate: pt(2.406, 1.021), rotate: 0,
  id: 'FC24'
})
// pd.vdd_cap[1].cap
const FC25 = board.add(C_0805_2012Metric, {
  translate: pt(2.241, 1.031), rotate: 0,
  id: 'FC25'
})
// spk_dac.rc.r
const FR17 = board.add(R_0603_1608Metric, {
  translate: pt(1.594, 1.588), rotate: 0,
  id: 'FR17'
})
// spk_dac.rc.c
const FC26 = board.add(C_0603_1608Metric, {
  translate: pt(1.594, 1.685), rotate: 0,
  id: 'FC26'
})
// spk_tp.tp
const FTP8 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.056, 1.945), rotate: 0,
  id: 'FTP8'
})
// spk_drv.ic
const FU9 = board.add(MSOP_8_3x3mm_P0_65mm, {
  translate: pt(1.892, 0.876), rotate: 0,
  id: 'FU9'
})
// spk_drv.pwr_cap0.cap
const FC27 = board.add(C_0603_1608Metric, {
  translate: pt(1.998, 1.013), rotate: 0,
  id: 'FC27'
})
// spk_drv.pwr_cap1.cap
const FC28 = board.add(C_0805_2012Metric, {
  translate: pt(1.833, 1.023), rotate: 0,
  id: 'FC28'
})
// spk_drv.inp_cap.cap
const FC29 = board.add(C_0603_1608Metric, {
  translate: pt(1.825, 1.130), rotate: 0,
  id: 'FC29'
})
// spk_drv.inn_cap.cap
const FC30 = board.add(C_0603_1608Metric, {
  translate: pt(1.981, 1.130), rotate: 0,
  id: 'FC30'
})
// spk.conn
const FJ7 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.767, 1.689), rotate: 0,
  id: 'FJ7'
})
// npx_shift.ic
const FU10 = board.add(SOT_23_5, {
  translate: pt(0.471, 1.626), rotate: 0,
  id: 'FU10'
})
// npx_shift.vdd_cap.cap
const FC31 = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 1.761), rotate: 0,
  id: 'FC31'
})
// npx_res.res
const FR18 = board.add(R_0603_1608Metric, {
  translate: pt(1.298, 1.937), rotate: 0,
  id: 'FR18'
})
// fan
const FJ8 = board.add(FanPinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.129, 1.709), rotate: 0,
  id: 'FJ8'
})
// fan_drv.pre
const FQ1 = board.add(SOT_23, {
  translate: pt(0.880, 1.130), rotate: 0,
  id: 'FQ1'
})
// fan_drv.pull
const FR19 = board.add(R_0603_1608Metric, {
  translate: pt(1.053, 1.092), rotate: 0,
  id: 'FR19'
})
// fan_drv.drv
const FQ2 = board.add(PQFN_8_EP_6x5mm_P1_27mm_Generic, {
  translate: pt(0.934, 0.915), rotate: 0,
  id: 'FQ2'
})
// fan_ctl.drv
const FQ3 = board.add(SOT_23, {
  translate: pt(1.846, 1.626), rotate: 0,
  id: 'FQ3'
})

board.setNetlist([
  {name: "Fgnd", pads: [["FJ1", "2"], ["FJ2", "A1"], ["FJ2", "A12"], ["FJ2", "B1"], ["FJ2", "B12"], ["FJ2", "S1"], ["FTP2", "1"], ["FU1", "3"], ["FU1", "7"], ["FU1", "8"], ["FC1", "2"], ["FU2", "1"], ["FR3", "2"], ["FC2", "2"], ["FC4", "2"], ["FC5", "2"], ["FD1", "2"], ["FU3", "1"], ["FR6", "2"], ["FC6", "2"], ["FC8", "2"], ["FC9", "2"], ["FD2", "2"], ["FJ5", "1"], ["FSW1", "C"], ["FSW1", "S2"], ["FU8", "15"], ["FU8", "8"], ["FU8", "9"], ["FC24", "2"], ["FC25", "2"], ["FC26", "2"], ["FU9", "7"], ["FC27", "2"], ["FC28", "2"], ["FC30", "2"], ["FU10", "3"], ["FC31", "2"], ["FJ8", "1"], ["FQ1", "2"], ["FQ3", "2"]]},
  {name: "Fvin", pads: [["FU1", "2"], ["FR1", "2"], ["FU2", "3"], ["FC2", "1"], ["FC4", "1"], ["FR4", "1"], ["FU3", "3"], ["FC6", "1"], ["FC8", "1"], ["FR7", "1"], ["FR19", "1"], ["FQ2", "1"], ["FQ2", "2"], ["FQ2", "3"]]},
  {name: "Fv5", pads: [["FR2", "1"], ["FL1", "2"], ["FC5", "1"], ["FTP3", "1"], ["FD1", "1"], ["FJ5", "3"], ["FU9", "1"], ["FU9", "6"], ["FC27", "1"], ["FC28", "1"], ["FU10", "5"], ["FC31", "1"]]},
  {name: "Fv3v3", pads: [["FU1", "4"], ["FC1", "1"], ["FR5", "1"], ["FL2", "2"], ["FC9", "1"], ["FTP4", "1"], ["FD2", "1"], ["FJ5", "2"], ["FU8", "3"], ["FU8", "4"], ["FC24", "1"], ["FC25", "1"]]},
  {name: "Fpwr.pwr", pads: [["FJ1", "1"], ["FJ2", "A4"], ["FJ2", "A9"], ["FJ2", "B4"], ["FJ2", "B9"], ["FTP1", "1"], ["FU1", "1"], ["FR1", "1"], ["FU8", "2"]]},
  {name: "Fusb.usb.dp", pads: [["FJ2", "A6"], ["FJ2", "B6"]]},
  {name: "Fusb.usb.dm", pads: [["FJ2", "A7"], ["FJ2", "B7"]]},
  {name: "Fusb.cc.cc1", pads: [["FJ2", "A5"], ["FU8", "10"], ["FU8", "11"]]},
  {name: "Fusb.cc.cc2", pads: [["FJ2", "B5"], ["FU8", "1"], ["FU8", "14"]]},
  {name: "Fvin_sense.i2c.scl", pads: [["FU1", "5"], ["FJ5", "4"], ["FU8", "6"]]},
  {name: "Fvin_sense.i2c.sda", pads: [["FU1", "6"], ["FJ5", "5"], ["FU8", "7"]]},
  {name: "Freg_5v.ic.sw", pads: [["FU2", "2"], ["FC3", "2"], ["FL1", "1"]]},
  {name: "Freg_5v.ic.fb", pads: [["FU2", "4"], ["FR2", "2"], ["FR3", "1"]]},
  {name: "Freg_5v.ic.boot", pads: [["FU2", "6"], ["FC3", "1"]]},
  {name: "Freg_5v.ic.en", pads: [["FU2", "5"], ["FR4", "2"]]},
  {name: "Freg_3v3.ic.sw", pads: [["FU3", "2"], ["FC7", "2"], ["FL2", "1"]]},
  {name: "Freg_3v3.ic.fb", pads: [["FU3", "4"], ["FR5", "2"], ["FR6", "1"]]},
  {name: "Freg_3v3.ic.boot", pads: [["FU3", "6"], ["FC7", "1"]]},
  {name: "Freg_3v3.ic.en", pads: [["FU3", "5"], ["FR7", "2"]]},
  {name: "Fcontrol.pd_int", pads: [["FJ5", "6"], ["FU8", "5"]]},
  {name: "Fcontrol.spk", pads: [["FJ5", "7"], ["FR17", "1"]]},
  {name: "Fcontrol.drv", pads: [["FJ5", "8"], ["FQ1", "1"]]},
  {name: "Fcontrol.tach", pads: [["FJ5", "11"], ["FJ8", "3"]]},
  {name: "Fcontrol.pwm", pads: [["FJ5", "9"], ["FU10", "2"], ["FQ3", "1"]]},
  {name: "Fcontrol.npx_en", pads: [["FJ5", "10"], ["FU10", "1"]]},
  {name: "Fcontrol.enc_a", pads: [["FJ5", "12"], ["FSW1", "A"]]},
  {name: "Fcontrol.enc_b", pads: [["FJ5", "13"], ["FSW1", "B"]]},
  {name: "Fcontrol.enc_sw", pads: [["FJ5", "14"], ["FSW1", "S1"]]},
  {name: "Fpd.ic.vconn", pads: [["FU8", "12"], ["FU8", "13"]]},
  {name: "Fspk_dac.output", pads: [["FR17", "2"], ["FC26", "1"], ["FTP8", "1"], ["FC29", "2"]]},
  {name: "Fspk_drv.spk.a", pads: [["FU9", "5"], ["FJ7", "1"]]},
  {name: "Fspk_drv.spk.b", pads: [["FU9", "8"], ["FJ7", "2"]]},
  {name: "Fspk_drv.ic.inp", pads: [["FU9", "3"], ["FC29", "1"]]},
  {name: "Fspk_drv.ic.inn", pads: [["FU9", "4"], ["FC30", "1"]]},
  {name: "Fnpx_shift.output", pads: [["FU10", "4"], ["FR18", "1"]]},
  {name: "Fnpx_res.output", pads: [["FR18", "2"], ["FJ8", "4"], ["FQ3", "3"]]},
  {name: "Ffan.pwr", pads: [["FJ8", "2"], ["FQ2", "5"]]},
  {name: "Ffan_drv.pre.drain", pads: [["FQ1", "3"], ["FR19", "2"], ["FQ2", "4"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.5822834645669293, 2.100787401574803);
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


