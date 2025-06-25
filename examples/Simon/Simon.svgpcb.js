const board = new PCB();

// mcu
const U1 = board.add(Nucleo32, {
  translate: pt(0.365, 0.990), rotate: 0,
  id: 'U1'
})
// spk_drv.ic
const U2 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.915, 1.240), rotate: 0,
  id: 'U2'
})
// spk_drv.in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(1.158, 1.163), rotate: 0,
  id: 'C1'
})
// spk_drv.byp_cap
const C2 = board.add(C_0603_1608Metric, {
  translate: pt(1.158, 1.259), rotate: 0,
  id: 'C2'
})
// spk_drv.sig_cap
const C3 = board.add(C_0603_1608Metric, {
  translate: pt(0.828, 1.415), rotate: 0,
  id: 'C3'
})
// spk_drv.sig_res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.983, 1.415), rotate: 0,
  id: 'R1'
})
// spk_drv.fb_res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(1.139, 1.415), rotate: 0,
  id: 'R2'
})
// spk.conn
const J1 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.431, 1.264), rotate: 0,
  id: 'J1'
})
// rgb.package
const D1 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(1.766, 1.189), rotate: 0,
  id: 'D1'
})
// rgb.red_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(1.905, 1.163), rotate: 0,
  id: 'R3'
})
// rgb.green_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(1.783, 1.312), rotate: 0,
  id: 'R4'
})
// rgb.blue_res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(1.939, 1.312), rotate: 0,
  id: 'R5'
})
// sw.package
const SW1 = board.add(SW_Push_SPST_NO_Alps_SKRK, {
  translate: pt(2.223, 1.201), rotate: 0,
  id: 'SW1'
})
// sw_pull.res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(1.297, 1.590), rotate: 0,
  id: 'R6'
})
// btn[0]
const J2 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.395, 0.937), rotate: 0,
  id: 'J2'
})
// btn_pull[0].res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(1.531, 1.590), rotate: 0,
  id: 'R7'
})
// btn[1]
const J3 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.576, 0.937), rotate: 0,
  id: 'J3'
})
// btn_pull[1].res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(1.062, 1.590), rotate: 0,
  id: 'R8'
})
// btn[2]
const J4 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.757, 0.937), rotate: 0,
  id: 'J4'
})
// btn_pull[2].res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(0.828, 1.590), rotate: 0,
  id: 'R9'
})
// btn[3]
const J5 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.939, 0.937), rotate: 0,
  id: 'J5'
})
// btn_pull[3].res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(2.508, 1.163), rotate: 0,
  id: 'R10'
})
// pwr.ic
const U3 = board.add(SOT_23_5, {
  translate: pt(2.130, 0.634), rotate: 0,
  id: 'U3'
})
// pwr.fb.div.top_res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(2.284, 0.769), rotate: 0,
  id: 'R11'
})
// pwr.fb.div.bottom_res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(2.107, 0.875), rotate: 0,
  id: 'R12'
})
// pwr.power_path.inductor
const L1 = board.add(L_0805_2012Metric, {
  translate: pt(2.118, 0.774), rotate: 0,
  id: 'L1'
})
// pwr.power_path.in_cap.cap
const C4 = board.add(C_0603_1608Metric, {
  translate: pt(2.263, 0.875), rotate: 0,
  id: 'C4'
})
// pwr.power_path.out_cap.cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(2.419, 0.875), rotate: 0,
  id: 'C5'
})
// pwr.rect
const D2 = board.add(D_SOD_323, {
  translate: pt(2.313, 0.604), rotate: 0,
  id: 'D2'
})
// btn_drv[0].pre
const Q1 = board.add(SOT_23, {
  translate: pt(0.845, 0.382), rotate: 0,
  id: 'Q1'
})
// btn_drv[0].pull
const R13 = board.add(R_0603_1608Metric, {
  translate: pt(1.018, 0.344), rotate: 0,
  id: 'R13'
})
// btn_drv[0].drv
const Q2 = board.add(TO_252_2, {
  translate: pt(1.021, 0.138), rotate: 0,
  id: 'Q2'
})
// btn_drv[1].pre
const Q3 = board.add(SOT_23, {
  translate: pt(1.955, 0.382), rotate: 0,
  id: 'Q3'
})
// btn_drv[1].pull
const R14 = board.add(R_0603_1608Metric, {
  translate: pt(2.128, 0.344), rotate: 0,
  id: 'R14'
})
// btn_drv[1].drv
const Q4 = board.add(TO_252_2, {
  translate: pt(2.131, 0.138), rotate: 0,
  id: 'Q4'
})
// btn_drv[2].pre
const Q5 = board.add(SOT_23, {
  translate: pt(1.400, 0.382), rotate: 0,
  id: 'Q5'
})
// btn_drv[2].pull
const R15 = board.add(R_0603_1608Metric, {
  translate: pt(1.573, 0.344), rotate: 0,
  id: 'R15'
})
// btn_drv[2].drv
const Q6 = board.add(TO_252_2, {
  translate: pt(1.576, 0.138), rotate: 0,
  id: 'Q6'
})
// btn_drv[3].pre
const Q7 = board.add(SOT_23, {
  translate: pt(0.845, 0.949), rotate: 0,
  id: 'Q7'
})
// btn_drv[3].pull
const R16 = board.add(R_0603_1608Metric, {
  translate: pt(1.018, 0.911), rotate: 0,
  id: 'R16'
})
// btn_drv[3].drv
const Q8 = board.add(TO_252_2, {
  translate: pt(1.021, 0.705), rotate: 0,
  id: 'Q8'
})

board.setNetlist([
  {name: "v5v", pads: [["U1", "19"], ["U2", "6"], ["U3", "5"], ["U3", "4"], ["C1", "1"], ["L1", "1"], ["C4", "1"]]},
  {name: "v3v3", pads: [["U1", "29"], ["D1", "2"], ["R6", "1"], ["R7", "1"], ["R8", "1"], ["R9", "1"], ["R10", "1"]]},
  {name: "gnd", pads: [["U1", "4"], ["U1", "17"], ["J2", "2"], ["J2", "4"], ["J3", "2"], ["J3", "4"], ["J4", "2"], ["J4", "4"], ["J5", "2"], ["J5", "4"], ["U2", "1"], ["U2", "7"], ["SW1", "2"], ["U3", "2"], ["Q1", "2"], ["Q3", "2"], ["Q5", "2"], ["Q7", "2"], ["C2", "2"], ["C1", "2"], ["R12", "2"], ["C4", "2"], ["C5", "2"]]},
  {name: "v12", pads: [["R13", "1"], ["Q2", "3"], ["R14", "1"], ["Q4", "3"], ["R15", "1"], ["Q6", "3"], ["R16", "1"], ["Q8", "3"], ["D2", "1"], ["R11", "1"], ["C5", "1"]]},
  {name: "spk_drv.sig", pads: [["U1", "24"], ["C3", "2"]]},
  {name: "spk_drv.spk.a", pads: [["U2", "5"], ["J1", "1"], ["R2", "2"]]},
  {name: "spk_drv.spk.b", pads: [["U2", "8"], ["J1", "2"]]},
  {name: "mcu.gpio.rgb_red", pads: [["U1", "15"], ["R3", "2"]]},
  {name: "mcu.gpio.rgb_green", pads: [["U1", "14"], ["R4", "2"]]},
  {name: "mcu.gpio.rgb_blue", pads: [["U1", "13"], ["R5", "2"]]},
  {name: "sw.out", pads: [["U1", "27"], ["SW1", "1"], ["R6", "2"]]},
  {name: "btn_pull[0].io", pads: [["J2", "3"], ["U1", "6"], ["R7", "2"]]},
  {name: "btn_pull[1].io", pads: [["J3", "3"], ["U1", "8"], ["R8", "2"]]},
  {name: "btn_pull[2].io", pads: [["J4", "3"], ["U1", "10"], ["R9", "2"]]},
  {name: "btn_pull[3].io", pads: [["J5", "3"], ["U1", "12"], ["R10", "2"]]},
  {name: "btn_drv[0].control", pads: [["U1", "5"], ["Q1", "1"]]},
  {name: "btn_drv[0].output", pads: [["Q2", "2"], ["J2", "1"]]},
  {name: "btn_drv[1].control", pads: [["U1", "7"], ["Q3", "1"]]},
  {name: "btn_zeroed_current[1]", pads: [["Q4", "2"], ["J3", "1"]]},
  {name: "btn_drv[2].control", pads: [["U1", "9"], ["Q5", "1"]]},
  {name: "btn_zeroed_current[2]", pads: [["Q6", "2"], ["J4", "1"]]},
  {name: "btn_drv[3].control", pads: [["U1", "11"], ["Q7", "1"]]},
  {name: "btn_zeroed_current[3]", pads: [["Q8", "2"], ["J5", "1"]]},
  {name: "spk_drv.sig_cap.pos", pads: [["C3", "1"], ["R1", "1"]]},
  {name: "spk_drv.sig_res.b", pads: [["R1", "2"], ["R2", "1"], ["U2", "4"]]},
  {name: "spk_drv.byp_cap.pos", pads: [["C2", "1"], ["U2", "3"], ["U2", "2"]]},
  {name: "rgb.red_res.a", pads: [["R3", "1"], ["D1", "3"]]},
  {name: "rgb.green_res.a", pads: [["R4", "1"], ["D1", "4"]]},
  {name: "rgb.blue_res.a", pads: [["R5", "1"], ["D1", "1"]]},
  {name: "pwr.fb.output", pads: [["U3", "3"], ["R11", "2"], ["R12", "1"]]},
  {name: "pwr.power_path.switch", pads: [["U3", "1"], ["L1", "2"], ["D2", "2"]]},
  {name: "btn_drv[0].pre.drain", pads: [["Q1", "3"], ["R13", "2"], ["Q2", "1"]]},
  {name: "btn_drv[1].pre.drain", pads: [["Q3", "3"], ["R14", "2"], ["Q4", "1"]]},
  {name: "btn_drv[2].pre.drain", pads: [["Q5", "3"], ["R15", "2"], ["Q6", "1"]]},
  {name: "btn_drv[3].pre.drain", pads: [["Q7", "3"], ["R16", "2"], ["Q8", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.6842519685039368, 2.0192913385826774);
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


