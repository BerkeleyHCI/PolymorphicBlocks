const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.735, 1.763), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.775, 1.763), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.735, 1.803), rotate: 0,
  id: 'H3'
})
// mcu
const U1 = board.add(FEATHERWING_NODIM, {
  translate: pt(0.893, 1.763), rotate: 0,
  id: 'U1'
})
// motor_pwr.conn
const J1 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.112, 1.286), rotate: 0,
  id: 'J1'
})
// sw1.package
const SW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.753, 0.919), rotate: 0,
  id: 'SW1'
})
// ledr.package
const D1 = board.add(LED_0603_1608Metric, {
  translate: pt(0.293, 1.519), rotate: 0,
  id: 'D1'
})
// ledr.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 1.617), rotate: 0,
  id: 'R1'
})
// ledg.package
const D2 = board.add(LED_0603_1608Metric, {
  translate: pt(2.340, 1.185), rotate: 0,
  id: 'D2'
})
// ledg.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(2.340, 1.282), rotate: 0,
  id: 'R2'
})
// ledb.package
const D3 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 1.519), rotate: 0,
  id: 'D3'
})
// ledb.res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.617), rotate: 0,
  id: 'R3'
})
// i2c_pull.scl_res.res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(0.763, 1.519), rotate: 0,
  id: 'R4'
})
// i2c_pull.sda_res.res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(0.763, 1.616), rotate: 0,
  id: 'R5'
})
// i2c_tp.tp_scl.tp
const TP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.098, 1.193), rotate: 0,
  id: 'TP1'
})
// i2c_tp.tp_sda.tp
const TP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.098, 1.307), rotate: 0,
  id: 'TP2'
})
// i2c.conn
const J2 = board.add(JST_PH_B4B_PH_K_1x04_P2_00mm_Vertical, {
  translate: pt(0.096, 1.286), rotate: 0,
  id: 'J2'
})
// ref_div.div.top_res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 1.519), rotate: 0,
  id: 'R6'
})
// ref_div.div.bottom_res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 1.616), rotate: 0,
  id: 'R7'
})
// ref_buf.amp.ic
const U2 = board.add(SOT_23_5, {
  translate: pt(0.952, 0.874), rotate: 0,
  id: 'U2'
})
// ref_buf.amp.vdd_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(0.929, 1.009), rotate: 0,
  id: 'C1'
})
// ref_tp.tp
const TP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 1.801), rotate: 0,
  id: 'TP3'
})
// hall.conn
const J3 = board.add(JST_PH_B5B_PH_K_1x05_P2_00mm_Vertical, {
  translate: pt(1.502, 1.286), rotate: 0,
  id: 'J3'
})
// hall_pull.res[u].res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(2.376, 0.029), rotate: 0,
  id: 'R8'
})
// hall_pull.res[v].res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(2.376, 0.126), rotate: 0,
  id: 'R9'
})
// hall_pull.res[w].res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(2.376, 0.222), rotate: 0,
  id: 'R10'
})
// hall_tp.tp[u].tp
const TP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.883, 0.037), rotate: 0,
  id: 'TP4'
})
// hall_tp.tp[v].tp
const TP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.883, 0.152), rotate: 0,
  id: 'TP5'
})
// hall_tp.tp[w].tp
const TP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.883, 0.266), rotate: 0,
  id: 'TP6'
})
// vsense.div.top_res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(0.997, 1.519), rotate: 0,
  id: 'R11'
})
// vsense.div.bottom_res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(0.997, 1.616), rotate: 0,
  id: 'R12'
})
// vsense_tp.tp
const TP7 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.991, 1.528), rotate: 0,
  id: 'TP7'
})
// isense.sense.res.res
const R13 = board.add(R_1206_3216Metric, {
  translate: pt(1.359, 0.044), rotate: 0,
  id: 'R13'
})
// isense.amp.amp.ic
const U3 = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.084, 0.106), rotate: 0,
  id: 'U3'
})
// isense.amp.amp.vdd_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(1.336, 0.166), rotate: 0,
  id: 'C2'
})
// isense.amp.r1
const R14 = board.add(R_0603_1608Metric, {
  translate: pt(0.997, 0.281), rotate: 0,
  id: 'R14'
})
// isense.amp.r2
const R15 = board.add(R_0603_1608Metric, {
  translate: pt(1.153, 0.281), rotate: 0,
  id: 'R15'
})
// isense.amp.rf
const R16 = board.add(R_0603_1608Metric, {
  translate: pt(1.309, 0.281), rotate: 0,
  id: 'R16'
})
// isense.amp.rg
const R17 = board.add(R_0603_1608Metric, {
  translate: pt(0.997, 0.378), rotate: 0,
  id: 'R17'
})
// isense_tp.tp
const TP8 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.741, 1.528), rotate: 0,
  id: 'TP8'
})
// isense_clamp.res
const R18 = board.add(R_0603_1608Metric, {
  translate: pt(0.559, 1.792), rotate: 0,
  id: 'R18'
})
// bldc_drv.ic
const U4 = board.add(HTSSOP_28_1EP_4_4x9_7mm_P0_65mm_EP2_85x5_4mm_ThermalVias, {
  translate: pt(0.152, 0.201), rotate: 0,
  id: 'U4'
})
// bldc_drv.vm_cap_bulk.cap
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(0.407, 0.480), rotate: 0,
  id: 'C3'
})
// bldc_drv.vm_cap1.cap
const C4 = board.add(C_0805_2012Metric, {
  translate: pt(0.580, 0.480), rotate: 0,
  id: 'C4'
})
// bldc_drv.vm_cap2.cap
const C5 = board.add(C_0805_2012Metric, {
  translate: pt(0.754, 0.480), rotate: 0,
  id: 'C5'
})
// bldc_drv.v3p3_cap.cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.660), rotate: 0,
  id: 'C6'
})
// bldc_drv.cp_cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 0.660), rotate: 0,
  id: 'C7'
})
// bldc_drv.vcp_cap
const C8 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.660), rotate: 0,
  id: 'C8'
})
// bldc_drv.pgnd_res[1].res.res
const R19 = board.add(R_2512_6332Metric, {
  translate: pt(0.493, 0.076), rotate: 0,
  id: 'R19'
})
// bldc_drv.pgnd_res[2].res.res
const R20 = board.add(R_2512_6332Metric, {
  translate: pt(0.493, 0.266), rotate: 0,
  id: 'R20'
})
// bldc_drv.pgnd_res[3].res.res
const R21 = board.add(R_2512_6332Metric, {
  translate: pt(0.150, 0.517), rotate: 0,
  id: 'R21'
})
// bldc_fault_tp.tp
const TP9 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.241, 1.528), rotate: 0,
  id: 'TP9'
})
// bldc_en_tp.tp[1].tp
const TP10 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.134, 0.037), rotate: 0,
  id: 'TP10'
})
// bldc_en_tp.tp[2].tp
const TP11 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.134, 0.152), rotate: 0,
  id: 'TP11'
})
// bldc_en_tp.tp[3].tp
const TP12 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.134, 0.266), rotate: 0,
  id: 'TP12'
})
// bldc_in_tp.tp[1].tp
const TP13 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.633, 0.037), rotate: 0,
  id: 'TP13'
})
// bldc_in_tp.tp[2].tp
const TP14 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.633, 0.152), rotate: 0,
  id: 'TP14'
})
// bldc_in_tp.tp[3].tp
const TP15 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.633, 0.266), rotate: 0,
  id: 'TP15'
})
// bldc.conn
const J4 = board.add(JST_PH_B3B_PH_K_1x03_P2_00mm_Vertical, {
  translate: pt(0.644, 1.286), rotate: 0,
  id: 'J4'
})
// curr_amp[1].amp.ic
const U5 = board.add(SOT_23_5, {
  translate: pt(1.231, 0.874), rotate: 0,
  id: 'U5'
})
// curr_amp[1].amp.vdd_cap.cap
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(1.409, 0.836), rotate: 0,
  id: 'C9'
})
// curr_amp[1].r1
const R22 = board.add(R_0603_1608Metric, {
  translate: pt(1.209, 1.009), rotate: 0,
  id: 'R22'
})
// curr_amp[1].r2
const R23 = board.add(R_0603_1608Metric, {
  translate: pt(1.365, 1.009), rotate: 0,
  id: 'R23'
})
// curr_tp[1].tp
const TP16 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.490, 1.528), rotate: 0,
  id: 'TP16'
})
// curr_amp[2].amp.ic
const U6 = board.add(SOT_23_5, {
  translate: pt(0.516, 0.874), rotate: 0,
  id: 'U6'
})
// curr_amp[2].amp.vdd_cap.cap
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(0.694, 0.836), rotate: 0,
  id: 'C10'
})
// curr_amp[2].r1
const R24 = board.add(R_0603_1608Metric, {
  translate: pt(0.494, 1.009), rotate: 0,
  id: 'R24'
})
// curr_amp[2].r2
const R25 = board.add(R_0603_1608Metric, {
  translate: pt(0.650, 1.009), rotate: 0,
  id: 'R25'
})
// curr_tp[2].tp
const TP17 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 1.801), rotate: 0,
  id: 'TP17'
})
// curr_amp[3].amp.ic
const U7 = board.add(SOT_23_5, {
  translate: pt(0.081, 0.874), rotate: 0,
  id: 'U7'
})
// curr_amp[3].amp.vdd_cap.cap
const C11 = board.add(C_0603_1608Metric, {
  translate: pt(0.259, 0.836), rotate: 0,
  id: 'C11'
})
// curr_amp[3].r1
const R26 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.009), rotate: 0,
  id: 'R26'
})
// curr_amp[3].r2
const R27 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 1.009), rotate: 0,
  id: 'R27'
})
// curr_tp[3].tp
const TP18 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.240, 1.528), rotate: 0,
  id: 'TP18'
})

board.setNetlist([
  {name: "vusb", pads: [["U1", "26"], ["J3", "1"]]},
  {name: "v3v3", pads: [["U1", "2"], ["J2", "2"], ["U2", "5"], ["R6", "1"], ["U5", "5"], ["U6", "5"], ["U7", "5"], ["R4", "1"], ["R5", "1"], ["R8", "1"], ["R9", "1"], ["R10", "1"], ["C1", "1"], ["C9", "1"], ["C10", "1"], ["C11", "1"]]},
  {name: "gnd", pads: [["U1", "4"], ["J1", "1"], ["SW1", "2"], ["R1", "2"], ["R2", "2"], ["R3", "2"], ["J2", "1"], ["J3", "5"], ["U4", "12"], ["U4", "13"], ["U4", "14"], ["U4", "19"], ["U4", "20"], ["U4", "21"], ["U4", "28"], ["U4", "29"], ["R7", "2"], ["U2", "2"], ["R12", "2"], ["U3", "4"], ["R23", "2"], ["R25", "2"], ["R27", "2"], ["C3", "2"], ["C4", "2"], ["C5", "2"], ["C6", "2"], ["U5", "2"], ["U6", "2"], ["U7", "2"], ["C1", "2"], ["C2", "2"], ["R19", "1"], ["R20", "1"], ["R21", "1"], ["C9", "2"], ["C10", "2"], ["C11", "2"]]},
  {name: "sw1.out", pads: [["U1", "20"], ["SW1", "1"]]},
  {name: "ledr.signal", pads: [["U1", "16"], ["D1", "2"]]},
  {name: "ledg.signal", pads: [["U1", "7"], ["D2", "2"]]},
  {name: "ledb.signal", pads: [["U1", "3"], ["D3", "2"]]},
  {name: "i2c_pull.i2c.scl", pads: [["U1", "22"], ["R4", "2"], ["TP1", "1"], ["J2", "4"]]},
  {name: "i2c_pull.i2c.sda", pads: [["U1", "21"], ["J2", "3"], ["R5", "2"], ["TP2", "1"]]},
  {name: "ref_div.output", pads: [["U2", "1"], ["R6", "2"], ["R7", "1"]]},
  {name: "ref_buf.output", pads: [["U2", "3"], ["TP3", "1"], ["R17", "1"], ["U2", "4"]]},
  {name: "hall.phases.u", pads: [["U1", "23"], ["J3", "2"], ["R8", "2"], ["TP4", "1"]]},
  {name: "hall.phases.v", pads: [["U1", "24"], ["J3", "3"], ["R9", "2"], ["TP5", "1"]]},
  {name: "hall.phases.w", pads: [["U1", "25"], ["J3", "4"], ["R10", "2"], ["TP6", "1"]]},
  {name: "motor_pwr.pwr", pads: [["J1", "2"], ["R11", "1"], ["U3", "7"], ["R13", "1"], ["C2", "1"], ["R15", "1"]]},
  {name: "vsense.output", pads: [["U1", "6"], ["TP7", "1"], ["R11", "2"], ["R12", "1"]]},
  {name: "isense.out", pads: [["TP8", "1"], ["R18", "1"], ["R16", "1"], ["U3", "6"]]},
  {name: "isense_clamp.signal_out", pads: [["U1", "5"], ["R18", "2"]]},
  {name: "isense.pwr_out", pads: [["U4", "4"], ["U4", "11"], ["R13", "2"], ["C8", "2"], ["C3", "1"], ["C4", "1"], ["C5", "1"], ["R14", "1"]]},
  {name: "bldc_drv.nreset", pads: [["U1", "18"], ["U4", "16"]]},
  {name: "bldc_drv.nfault", pads: [["U1", "19"], ["U4", "18"], ["TP9", "1"]]},
  {name: "mcu.gpio.bldc_en_1", pads: [["U1", "12"], ["U4", "26"], ["TP10", "1"]]},
  {name: "mcu.gpio.bldc_en_2", pads: [["U1", "14"], ["U4", "24"], ["TP11", "1"]]},
  {name: "mcu.gpio.bldc_en_3", pads: [["U1", "17"], ["U4", "22"], ["TP12", "1"]]},
  {name: "mcu.gpio.bldc_in_1", pads: [["U1", "11"], ["U4", "27"], ["TP13", "1"]]},
  {name: "mcu.gpio.bldc_in_2", pads: [["U1", "13"], ["U4", "25"], ["TP14", "1"]]},
  {name: "mcu.gpio.bldc_in_3", pads: [["U1", "15"], ["U4", "23"], ["TP15", "1"]]},
  {name: "bldc_drv.outs.1", pads: [["U4", "5"], ["J4", "1"]]},
  {name: "bldc_drv.outs.2", pads: [["U4", "8"], ["J4", "2"]]},
  {name: "bldc_drv.outs.3", pads: [["U4", "9"], ["J4", "3"]]},
  {name: "curr_amp[1].input", pads: [["U5", "1"], ["R19", "2"], ["U4", "6"]]},
  {name: "curr_amp[1].output", pads: [["U1", "10"], ["TP16", "1"], ["R22", "1"], ["U5", "4"]]},
  {name: "curr_amp[2].input", pads: [["U6", "1"], ["R20", "2"], ["U4", "7"]]},
  {name: "curr_amp[2].output", pads: [["U1", "9"], ["TP17", "1"], ["R24", "1"], ["U6", "4"]]},
  {name: "curr_amp[3].input", pads: [["U7", "1"], ["R21", "2"], ["U4", "10"]]},
  {name: "curr_amp[3].output", pads: [["U1", "8"], ["TP18", "1"], ["R26", "1"], ["U7", "4"]]},
  {name: "ledr.res.a", pads: [["R1", "1"], ["D1", "1"]]},
  {name: "ledg.res.a", pads: [["R2", "1"], ["D2", "1"]]},
  {name: "ledb.res.a", pads: [["R3", "1"], ["D3", "1"]]},
  {name: "isense.amp.r2.b", pads: [["R15", "2"], ["U3", "3"], ["R17", "2"]]},
  {name: "isense.amp.r1.b", pads: [["R14", "2"], ["U3", "2"], ["R16", "2"]]},
  {name: "bldc_drv.ic.v3p3", pads: [["U4", "15"], ["C6", "1"], ["U4", "17"]]},
  {name: "bldc_drv.cp_cap.pos", pads: [["C7", "1"], ["U4", "2"]]},
  {name: "bldc_drv.cp_cap.neg", pads: [["C7", "2"], ["U4", "1"]]},
  {name: "bldc_drv.vcp_cap.pos", pads: [["C8", "1"], ["U4", "3"]]},
  {name: "curr_amp[1].r2.a", pads: [["R23", "1"], ["U5", "3"], ["R22", "2"]]},
  {name: "curr_amp[2].r2.a", pads: [["R25", "1"], ["U6", "3"], ["R24", "2"]]},
  {name: "curr_amp[3].r2.a", pads: [["R27", "1"], ["U7", "3"], ["R26", "2"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.552755905511811, 1.9562992125984253);
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


