const board = new PCB();

// pwr_conn
const J1 = board.add(Molex_DuraClik_vert_3pin, {
  translate: pt(2.459, 1.764), rotate: 0,
  id: 'J1'
})
// pwr.ic
const U1 = board.add(SOT_23_6, {
  translate: pt(0.956, 1.831), rotate: 0,
  id: 'U1'
})
// pwr.fb.div.top_res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(1.111, 1.966), rotate: 0,
  id: 'R1'
})
// pwr.fb.div.bottom_res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(1.267, 1.966), rotate: 0,
  id: 'R2'
})
// pwr.hf_in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(0.934, 2.072), rotate: 0,
  id: 'C1'
})
// pwr.vbst_cap
const C2 = board.add(C_0603_1608Metric, {
  translate: pt(1.090, 2.072), rotate: 0,
  id: 'C2'
})
// pwr.power_path.inductor
const L1 = board.add(L_0805_2012Metric, {
  translate: pt(0.944, 1.970), rotate: 0,
  id: 'L1'
})
// pwr.power_path.in_cap.cap
const C3 = board.add(C_0603_1608Metric, {
  translate: pt(1.246, 2.072), rotate: 0,
  id: 'C3'
})
// pwr.power_path.out_cap.cap
const C4 = board.add(C_0805_2012Metric, {
  translate: pt(1.143, 1.802), rotate: 0,
  id: 'C4'
})
// mcu.swd.conn
const J2 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(2.106, 1.028), rotate: 0,
  id: 'J2'
})
// mcu.ic
const U2 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(1.694, 1.085), rotate: 0,
  id: 'U2'
})
// mcu.swd_pull.swdio.res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(1.723, 1.356), rotate: 0,
  id: 'R3'
})
// mcu.swd_pull.swclk.res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(1.879, 1.356), rotate: 0,
  id: 'R4'
})
// mcu.pwr_cap[0].cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(2.035, 1.356), rotate: 0,
  id: 'C5'
})
// mcu.pwr_cap[1].cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(2.191, 1.356), rotate: 0,
  id: 'C6'
})
// mcu.pwr_cap[2].cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(2.346, 1.356), rotate: 0,
  id: 'C7'
})
// mcu.pwr_cap[3].cap
const C8 = board.add(C_0603_1608Metric, {
  translate: pt(1.550, 1.472), rotate: 0,
  id: 'C8'
})
// mcu.pwr_cap[4].cap
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(1.706, 1.472), rotate: 0,
  id: 'C9'
})
// mcu.pwr_cap[5].cap
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(1.861, 1.472), rotate: 0,
  id: 'C10'
})
// mcu.vbat_cap.cap
const C11 = board.add(C_0603_1608Metric, {
  translate: pt(2.017, 1.472), rotate: 0,
  id: 'C11'
})
// mcu.pwra_cap[0].cap
const C12 = board.add(C_0603_1608Metric, {
  translate: pt(2.173, 1.472), rotate: 0,
  id: 'C12'
})
// mcu.pwra_cap[1].cap
const C13 = board.add(C_0805_2012Metric, {
  translate: pt(2.381, 1.094), rotate: 0,
  id: 'C13'
})
// mcu.vref_cap[0].cap
const C14 = board.add(C_0603_1608Metric, {
  translate: pt(2.329, 1.472), rotate: 0,
  id: 'C14'
})
// mcu.vref_cap[1].cap
const C15 = board.add(C_0603_1608Metric, {
  translate: pt(1.550, 1.569), rotate: 0,
  id: 'C15'
})
// mcu.vref_cap[2].cap
const C16 = board.add(C_0805_2012Metric, {
  translate: pt(1.558, 1.365), rotate: 0,
  id: 'C16'
})
// mcu.crystal.package
const X1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(2.397, 0.949), rotate: 0,
  id: 'X1'
})
// mcu.crystal.cap_a
const C17 = board.add(C_0603_1608Metric, {
  translate: pt(1.706, 1.569), rotate: 0,
  id: 'C17'
})
// mcu.crystal.cap_b
const C18 = board.add(C_0603_1608Metric, {
  translate: pt(1.861, 1.569), rotate: 0,
  id: 'C18'
})
// can.conn
const J3 = board.add(Molex_DuraClik_vert_5pin, {
  translate: pt(0.000, 2.299), rotate: 0,
  id: 'J3'
})
// can.can_fuse.fuse
const F1 = board.add(R_0603_1608Metric, {
  translate: pt(0.231, 2.211), rotate: 0,
  id: 'F1'
})
// can.reg.ic
const U3 = board.add(SOT_23_5, {
  translate: pt(0.589, 1.831), rotate: 0,
  id: 'U3'
})
// can.reg.in_cap.cap
const C19 = board.add(C_0603_1608Metric, {
  translate: pt(0.387, 2.211), rotate: 0,
  id: 'C19'
})
// can.reg.out_cap.cap
const C20 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 2.221), rotate: 0,
  id: 'C20'
})
// can.esd
const U4 = board.add(SOT_23, {
  translate: pt(0.583, 2.004), rotate: 0,
  id: 'U4'
})
// can.transceiver.ic
const U5 = board.add(SOP_8_6_62x9_15mm_P2_54mm, {
  translate: pt(0.234, 1.954), rotate: 0,
  id: 'U5'
})
// can.transceiver.logic_cap.cap
const C21 = board.add(C_0603_1608Metric, {
  translate: pt(0.543, 2.211), rotate: 0,
  id: 'C21'
})
// can.transceiver.can_cap.cap
const C22 = board.add(C_0603_1608Metric, {
  translate: pt(0.699, 2.211), rotate: 0,
  id: 'C22'
})
// vsense.div.top_res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(2.283, 1.793), rotate: 0,
  id: 'R5'
})
// vsense.div.bottom_res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(2.283, 1.889), rotate: 0,
  id: 'R6'
})
// rgb1.package
const D1 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(1.875, 1.819), rotate: 0,
  id: 'D1'
})
// rgb1.red_res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(2.014, 1.793), rotate: 0,
  id: 'R7'
})
// rgb1.green_res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(1.892, 1.942), rotate: 0,
  id: 'R8'
})
// rgb1.blue_res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(2.048, 1.942), rotate: 0,
  id: 'R9'
})
// rgb2.package
const D2 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(1.485, 1.819), rotate: 0,
  id: 'D2'
})
// rgb2.red_res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(1.624, 1.793), rotate: 0,
  id: 'R10'
})
// rgb2.green_res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(1.502, 1.942), rotate: 0,
  id: 'R11'
})
// rgb2.blue_res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(1.657, 1.942), rotate: 0,
  id: 'R12'
})
// light[0].conn
const J4 = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(1.248, 0.630), rotate: 0,
  id: 'J4'
})
// light[0].drv[0].pre
const Q1 = board.add(SOT_23, {
  translate: pt(1.298, 0.382), rotate: 0,
  id: 'Q1'
})
// light[0].drv[0].pull
const R13 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 0.659), rotate: 0,
  id: 'R13'
})
// light[0].drv[0].drv
const Q2 = board.add(TO_252_2, {
  translate: pt(0.997, 0.138), rotate: 0,
  id: 'Q2'
})
// light[0].drv[1].pre
const Q3 = board.add(SOT_23, {
  translate: pt(0.821, 0.697), rotate: 0,
  id: 'Q3'
})
// light[0].drv[1].pull
const R14 = board.add(R_0603_1608Metric, {
  translate: pt(1.150, 0.659), rotate: 0,
  id: 'R14'
})
// light[0].drv[1].drv
const Q4 = board.add(TO_252_2, {
  translate: pt(0.997, 0.453), rotate: 0,
  id: 'Q4'
})
// light[1].conn
const J5 = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(0.502, 1.512), rotate: 0,
  id: 'J5'
})
// light[1].drv[0].pre
const Q5 = board.add(SOT_23, {
  translate: pt(0.552, 1.264), rotate: 0,
  id: 'Q5'
})
// light[1].drv[0].pull
const R15 = board.add(R_0603_1608Metric, {
  translate: pt(0.249, 1.541), rotate: 0,
  id: 'R15'
})
// light[1].drv[0].drv
const Q6 = board.add(TO_252_2, {
  translate: pt(0.252, 1.020), rotate: 0,
  id: 'Q6'
})
// light[1].drv[1].pre
const Q7 = board.add(SOT_23, {
  translate: pt(0.076, 1.579), rotate: 0,
  id: 'Q7'
})
// light[1].drv[1].pull
const R16 = board.add(R_0603_1608Metric, {
  translate: pt(0.405, 1.541), rotate: 0,
  id: 'R16'
})
// light[1].drv[1].drv
const Q8 = board.add(TO_252_2, {
  translate: pt(0.252, 1.335), rotate: 0,
  id: 'Q8'
})
// light[2].conn
const J6 = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(1.248, 1.512), rotate: 0,
  id: 'J6'
})
// light[2].drv[0].pre
const Q9 = board.add(SOT_23, {
  translate: pt(1.298, 1.264), rotate: 0,
  id: 'Q9'
})
// light[2].drv[0].pull
const R17 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 1.541), rotate: 0,
  id: 'R17'
})
// light[2].drv[0].drv
const Q10 = board.add(TO_252_2, {
  translate: pt(0.997, 1.020), rotate: 0,
  id: 'Q10'
})
// light[2].drv[1].pre
const Q11 = board.add(SOT_23, {
  translate: pt(0.821, 1.579), rotate: 0,
  id: 'Q11'
})
// light[2].drv[1].pull
const R18 = board.add(R_0603_1608Metric, {
  translate: pt(1.150, 1.541), rotate: 0,
  id: 'R18'
})
// light[2].drv[1].drv
const Q12 = board.add(TO_252_2, {
  translate: pt(0.997, 1.335), rotate: 0,
  id: 'Q12'
})
// light[3].conn
const J7 = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(1.994, 0.630), rotate: 0,
  id: 'J7'
})
// light[3].drv[0].pre
const Q13 = board.add(SOT_23, {
  translate: pt(2.043, 0.382), rotate: 0,
  id: 'Q13'
})
// light[3].drv[0].pull
const R19 = board.add(R_0603_1608Metric, {
  translate: pt(1.740, 0.659), rotate: 0,
  id: 'R19'
})
// light[3].drv[0].drv
const Q14 = board.add(TO_252_2, {
  translate: pt(1.743, 0.138), rotate: 0,
  id: 'Q14'
})
// light[3].drv[1].pre
const Q15 = board.add(SOT_23, {
  translate: pt(1.567, 0.697), rotate: 0,
  id: 'Q15'
})
// light[3].drv[1].pull
const R20 = board.add(R_0603_1608Metric, {
  translate: pt(1.896, 0.659), rotate: 0,
  id: 'R20'
})
// light[3].drv[1].drv
const Q16 = board.add(TO_252_2, {
  translate: pt(1.743, 0.453), rotate: 0,
  id: 'Q16'
})
// light[4].conn
const J8 = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(2.739, 0.630), rotate: 0,
  id: 'J8'
})
// light[4].drv[0].pre
const Q17 = board.add(SOT_23, {
  translate: pt(2.789, 0.382), rotate: 0,
  id: 'Q17'
})
// light[4].drv[0].pull
const R21 = board.add(R_0603_1608Metric, {
  translate: pt(2.486, 0.659), rotate: 0,
  id: 'R21'
})
// light[4].drv[0].drv
const Q18 = board.add(TO_252_2, {
  translate: pt(2.489, 0.138), rotate: 0,
  id: 'Q18'
})
// light[4].drv[1].pre
const Q19 = board.add(SOT_23, {
  translate: pt(2.313, 0.697), rotate: 0,
  id: 'Q19'
})
// light[4].drv[1].pull
const R22 = board.add(R_0603_1608Metric, {
  translate: pt(2.642, 0.659), rotate: 0,
  id: 'R22'
})
// light[4].drv[1].drv
const Q20 = board.add(TO_252_2, {
  translate: pt(2.489, 0.453), rotate: 0,
  id: 'Q20'
})
// light[5].conn
const J9 = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(0.502, 0.630), rotate: 0,
  id: 'J9'
})
// light[5].drv[0].pre
const Q21 = board.add(SOT_23, {
  translate: pt(0.552, 0.382), rotate: 0,
  id: 'Q21'
})
// light[5].drv[0].pull
const R23 = board.add(R_0603_1608Metric, {
  translate: pt(0.249, 0.659), rotate: 0,
  id: 'R23'
})
// light[5].drv[0].drv
const Q22 = board.add(TO_252_2, {
  translate: pt(0.252, 0.138), rotate: 0,
  id: 'Q22'
})
// light[5].drv[1].pre
const Q23 = board.add(SOT_23, {
  translate: pt(0.076, 0.697), rotate: 0,
  id: 'Q23'
})
// light[5].drv[1].pull
const R24 = board.add(R_0603_1608Metric, {
  translate: pt(0.405, 0.659), rotate: 0,
  id: 'R24'
})
// light[5].drv[1].drv
const Q24 = board.add(TO_252_2, {
  translate: pt(0.252, 0.453), rotate: 0,
  id: 'Q24'
})

board.setNetlist([
  {name: "vin", pads: [["J1", "2"], ["U1", "3"], ["R5", "1"], ["U1", "5"], ["J4", "1"], ["J5", "1"], ["J6", "1"], ["J7", "1"], ["J8", "1"], ["J9", "1"], ["C1", "1"], ["C3", "1"], ["R13", "1"], ["Q2", "3"], ["R14", "1"], ["Q4", "3"], ["R15", "1"], ["Q6", "3"], ["R16", "1"], ["Q8", "3"], ["R17", "1"], ["Q10", "3"], ["R18", "1"], ["Q12", "3"], ["R19", "1"], ["Q14", "3"], ["R20", "1"], ["Q16", "3"], ["R21", "1"], ["Q18", "3"], ["R22", "1"], ["Q20", "3"], ["R23", "1"], ["Q22", "3"], ["R24", "1"], ["Q24", "3"]]},
  {name: "gnd", pads: [["J1", "1"], ["J1", "3"], ["U1", "1"], ["U2", "17"], ["U2", "11"], ["U2", "20"], ["U2", "40"], ["U2", "41"], ["J4", "4"], ["J5", "4"], ["J6", "4"], ["J7", "4"], ["J8", "4"], ["J9", "4"], ["U5", "4"], ["R6", "2"], ["C1", "2"], ["C5", "2"], ["C6", "2"], ["C7", "2"], ["C8", "2"], ["C9", "2"], ["C10", "2"], ["C11", "2"], ["C12", "2"], ["C13", "2"], ["C14", "2"], ["C15", "2"], ["C16", "2"], ["X1", "2"], ["X1", "4"], ["Q1", "2"], ["Q3", "2"], ["Q5", "2"], ["Q7", "2"], ["Q9", "2"], ["Q11", "2"], ["Q13", "2"], ["Q15", "2"], ["Q17", "2"], ["Q19", "2"], ["Q21", "2"], ["Q23", "2"], ["R2", "2"], ["R4", "1"], ["C21", "2"], ["J2", "3"], ["J2", "5"], ["J2", "9"], ["C17", "2"], ["C18", "2"], ["C3", "2"], ["C4", "2"]]},
  {name: "v3v3", pads: [["U2", "16"], ["U2", "10"], ["U2", "14"], ["U2", "30"], ["U2", "27"], ["U2", "39"], ["U2", "42"], ["D1", "2"], ["D2", "2"], ["U5", "1"], ["R1", "1"], ["J2", "1"], ["C5", "1"], ["C6", "1"], ["C7", "1"], ["C8", "1"], ["C9", "1"], ["C10", "1"], ["C11", "1"], ["C12", "1"], ["C13", "1"], ["C14", "1"], ["C15", "1"], ["C16", "1"], ["R3", "1"], ["C21", "1"], ["L1", "2"], ["C4", "1"]]},
  {name: "can_chain_0.txd", pads: [["U2", "43"], ["U5", "3"]]},
  {name: "can_chain_0.rxd", pads: [["U2", "44"], ["U5", "2"]]},
  {name: "vsense.output", pads: [["U2", "21"], ["R5", "2"], ["R6", "1"]]},
  {name: "mcu.gpio.rgb1_red", pads: [["U2", "28"], ["R7", "2"]]},
  {name: "mcu.gpio.rgb1_green", pads: [["U2", "23"], ["R8", "2"]]},
  {name: "mcu.gpio.rgb1_blue", pads: [["U2", "22"], ["R9", "2"]]},
  {name: "mcu.gpio.rgb2_red", pads: [["U2", "18"], ["R10", "2"]]},
  {name: "mcu.gpio.rgb2_green", pads: [["U2", "15"], ["R11", "2"]]},
  {name: "mcu.gpio.rgb2_blue", pads: [["U2", "13"], ["R12", "2"]]},
  {name: "light[0].control[0]", pads: [["U2", "12"], ["Q1", "1"]]},
  {name: "light[0].control[1]", pads: [["U2", "8"], ["Q3", "1"]]},
  {name: "light[1].control[0]", pads: [["U2", "7"], ["Q5", "1"]]},
  {name: "light[1].control[1]", pads: [["U2", "6"], ["Q7", "1"]]},
  {name: "light[2].control[0]", pads: [["U2", "4"], ["Q9", "1"]]},
  {name: "light[2].control[1]", pads: [["U2", "3"], ["Q11", "1"]]},
  {name: "light[3].control[0]", pads: [["U2", "2"], ["Q13", "1"]]},
  {name: "light[3].control[1]", pads: [["U2", "1"], ["Q15", "1"]]},
  {name: "light[4].control[0]", pads: [["U2", "48"], ["Q17", "1"]]},
  {name: "light[4].control[1]", pads: [["U2", "47"], ["Q19", "1"]]},
  {name: "light[5].control[0]", pads: [["U2", "46"], ["Q21", "1"]]},
  {name: "light[5].control[1]", pads: [["U2", "45"], ["Q23", "1"]]},
  {name: "pwr.fb.output", pads: [["U1", "4"], ["R1", "2"], ["R2", "1"]]},
  {name: "pwr.vbst_cap.neg", pads: [["C2", "2"], ["U1", "2"], ["L1", "1"]]},
  {name: "pwr.vbst_cap.pos", pads: [["C2", "1"], ["U1", "6"]]},
  {name: "mcu.xtal_node.xi", pads: [["U2", "26"], ["X1", "1"], ["C17", "1"]]},
  {name: "mcu.xtal_node.xo", pads: [["U2", "25"], ["X1", "3"], ["C18", "1"]]},
  {name: "mcu.swd_node.swdio", pads: [["U2", "33"], ["J2", "2"], ["R3", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["U2", "29"], ["J2", "4"], ["R4", "2"]]},
  {name: "mcu.reset_node", pads: [["U2", "34"], ["J2", "10"]]},
  {name: "mcu.swd.swo", pads: [["U2", "9"], ["J2", "6"]]},
  {name: "mcu.swd.tdi", pads: [["J2", "8"]]},
  {name: "mcu.ic.xtal_rtc.xtal_in", pads: [["U2", "31"]]},
  {name: "mcu.ic.xtal_rtc.xtal_out", pads: [["U2", "32"]]},
  {name: "can.can.canh", pads: [["J3", "4"], ["U4", "2"], ["U5", "7"]]},
  {name: "can.can.canl", pads: [["J3", "5"], ["U4", "1"], ["U5", "6"]]},
  {name: "can.conn.pwr", pads: [["J3", "2"], ["F1", "1"]]},
  {name: "can.can_fuse.pwr_out", pads: [["F1", "2"], ["U3", "1"], ["U3", "3"], ["C19", "1"]]},
  {name: "can.conn.gnd", pads: [["J3", "3"], ["U4", "3"], ["U3", "2"], ["U5", "5"], ["C19", "2"], ["C20", "2"], ["C22", "2"]]},
  {name: "can.transceiver.can_pwr", pads: [["U5", "8"], ["U3", "5"], ["C22", "1"], ["C20", "1"]]},
  {name: "rgb1.red_res.a", pads: [["R7", "1"], ["D1", "3"]]},
  {name: "rgb1.green_res.a", pads: [["R8", "1"], ["D1", "4"]]},
  {name: "rgb1.blue_res.a", pads: [["R9", "1"], ["D1", "1"]]},
  {name: "rgb2.red_res.a", pads: [["R10", "1"], ["D2", "3"]]},
  {name: "rgb2.green_res.a", pads: [["R11", "1"], ["D2", "4"]]},
  {name: "rgb2.blue_res.a", pads: [["R12", "1"], ["D2", "1"]]},
  {name: "light[0].drv[0].output", pads: [["J4", "2"], ["Q2", "2"]]},
  {name: "light[0].drv[1].output", pads: [["J4", "3"], ["Q4", "2"]]},
  {name: "light[0].drv[0].pre.drain", pads: [["Q1", "3"], ["R13", "2"], ["Q2", "1"]]},
  {name: "light[0].drv[1].pre.drain", pads: [["Q3", "3"], ["R14", "2"], ["Q4", "1"]]},
  {name: "light[1].drv[0].output", pads: [["J5", "2"], ["Q6", "2"]]},
  {name: "light[1].drv[1].output", pads: [["J5", "3"], ["Q8", "2"]]},
  {name: "light[1].drv[0].pre.drain", pads: [["Q5", "3"], ["R15", "2"], ["Q6", "1"]]},
  {name: "light[1].drv[1].pre.drain", pads: [["Q7", "3"], ["R16", "2"], ["Q8", "1"]]},
  {name: "light[2].drv[0].output", pads: [["J6", "2"], ["Q10", "2"]]},
  {name: "light[2].drv[1].output", pads: [["J6", "3"], ["Q12", "2"]]},
  {name: "light[2].drv[0].pre.drain", pads: [["Q9", "3"], ["R17", "2"], ["Q10", "1"]]},
  {name: "light[2].drv[1].pre.drain", pads: [["Q11", "3"], ["R18", "2"], ["Q12", "1"]]},
  {name: "light[3].drv[0].output", pads: [["J7", "2"], ["Q14", "2"]]},
  {name: "light[3].drv[1].output", pads: [["J7", "3"], ["Q16", "2"]]},
  {name: "light[3].drv[0].pre.drain", pads: [["Q13", "3"], ["R19", "2"], ["Q14", "1"]]},
  {name: "light[3].drv[1].pre.drain", pads: [["Q15", "3"], ["R20", "2"], ["Q16", "1"]]},
  {name: "light[4].drv[0].output", pads: [["J8", "2"], ["Q18", "2"]]},
  {name: "light[4].drv[1].output", pads: [["J8", "3"], ["Q20", "2"]]},
  {name: "light[4].drv[0].pre.drain", pads: [["Q17", "3"], ["R21", "2"], ["Q18", "1"]]},
  {name: "light[4].drv[1].pre.drain", pads: [["Q19", "3"], ["R22", "2"], ["Q20", "1"]]},
  {name: "light[5].drv[0].output", pads: [["J9", "2"], ["Q22", "2"]]},
  {name: "light[5].drv[1].output", pads: [["J9", "3"], ["Q24", "2"]]},
  {name: "light[5].drv[0].pre.drain", pads: [["Q21", "3"], ["R23", "2"], ["Q22", "1"]]},
  {name: "light[5].drv[1].pre.drain", pads: [["Q23", "3"], ["R24", "2"], ["Q24", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.9826771653543305, 2.4173228346456694);
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


