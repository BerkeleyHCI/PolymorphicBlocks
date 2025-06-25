const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.002, 2.210), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.041, 2.210), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.002, 2.249), rotate: 0,
  id: 'H3'
})
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 1.905), rotate: 0,
  id: 'J1'
})
// batt.conn
const J2 = board.add(JST_PH_S2B_PH_K_1x02_P2_00mm_Horizontal, {
  translate: pt(0.633, 2.006), rotate: 0,
  id: 'J2'
})
// tp_pwr.tp
const TP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.874, 2.247), rotate: 0,
  id: 'TP1'
})
// tp_gnd.tp
const TP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.124, 2.247), rotate: 0,
  id: 'TP2'
})
// vbat_prot.fet
const Q1 = board.add(SOT_23, {
  translate: pt(0.076, 2.277), rotate: 0,
  id: 'Q1'
})
// reg_3v3.ic
const U1 = board.add(SOT_23_6, {
  translate: pt(3.419, 0.952), rotate: 0,
  id: 'U1'
})
// reg_3v3.fb.div.top_res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(3.570, 1.131), rotate: 0,
  id: 'R1'
})
// reg_3v3.fb.div.bottom_res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(3.176, 1.261), rotate: 0,
  id: 'R2'
})
// reg_3v3.hf_in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(3.332, 1.261), rotate: 0,
  id: 'C1'
})
// reg_3v3.boot_cap
const C2 = board.add(C_0603_1608Metric, {
  translate: pt(3.488, 1.261), rotate: 0,
  id: 'C2'
})
// reg_3v3.power_path.inductor
const L1 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(3.209, 0.974), rotate: 0,
  id: 'L1'
})
// reg_3v3.power_path.in_cap.cap
const C3 = board.add(C_1206_3216Metric, {
  translate: pt(3.209, 1.147), rotate: 0,
  id: 'C3'
})
// reg_3v3.power_path.out_cap.cap
const C4 = board.add(C_0805_2012Metric, {
  translate: pt(3.406, 1.141), rotate: 0,
  id: 'C4'
})
// reg_3v3.en_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(3.176, 1.357), rotate: 0,
  id: 'R3'
})
// tp_3v3.tp
const TP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.375, 2.247), rotate: 0,
  id: 'TP3'
})
// vbat_sense_gate.pre
const Q2 = board.add(SOT_23, {
  translate: pt(1.487, 1.807), rotate: 0,
  id: 'Q2'
})
// vbat_sense_gate.pull
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(1.660, 1.942), rotate: 0,
  id: 'R4'
})
// vbat_sense_gate.drv
const Q3 = board.add(SOT_23, {
  translate: pt(1.487, 1.980), rotate: 0,
  id: 'Q3'
})
// mcu.ic
const U2 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'U2'
})
// mcu.vcc_cap0.cap
const C5 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.683), rotate: 0,
  id: 'C5'
})
// mcu.vcc_cap1.cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.667), rotate: 0,
  id: 'C6'
})
// mcu.prog.conn
const J3 = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(2.096, 0.167), rotate: 0,
  id: 'J3'
})
// mcu.boot.package
const SW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.096, 0.486), rotate: 0,
  id: 'SW1'
})
// mcu.en_pull.rc.r
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.667), rotate: 0,
  id: 'R5'
})
// mcu.en_pull.rc.c
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.796), rotate: 0,
  id: 'C7'
})
// usb_esd
const U3 = board.add(SOT_23, {
  translate: pt(2.887, 2.277), rotate: 0,
  id: 'U3'
})
// ledr.package
const D1 = board.add(LED_0603_1608Metric, {
  translate: pt(2.848, 1.769), rotate: 0,
  id: 'D1'
})
// ledr.res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(2.848, 1.866), rotate: 0,
  id: 'R6'
})
// ledg.package
const D2 = board.add(LED_0603_1608Metric, {
  translate: pt(3.083, 1.769), rotate: 0,
  id: 'D2'
})
// ledg.res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(3.083, 1.866), rotate: 0,
  id: 'R7'
})
// ledb.package
const D3 = board.add(LED_0603_1608Metric, {
  translate: pt(3.318, 1.769), rotate: 0,
  id: 'D3'
})
// ledb.res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(3.318, 1.866), rotate: 0,
  id: 'R8'
})
// sw.package
const SW2 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.504, 1.852), rotate: 0,
  id: 'SW2'
})
// vbat_sense.div.top_res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(3.553, 1.769), rotate: 0,
  id: 'R9'
})
// vbat_sense.div.bottom_res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(3.553, 1.866), rotate: 0,
  id: 'R10'
})
// touch_duck
const U4 = board.add(Symbol_DucklingSolid, {
  translate: pt(3.159, 2.210), rotate: 0,
  id: 'U4'
})
// touch_lemur
const U5 = board.add(Symbol_LemurSolid, {
  translate: pt(3.198, 2.210), rotate: 0,
  id: 'U5'
})
// epd_gate.drv
const Q4 = board.add(SOT_23, {
  translate: pt(0.345, 2.277), rotate: 0,
  id: 'Q4'
})
// mem_gate.drv
const Q5 = board.add(SOT_23, {
  translate: pt(0.614, 2.277), rotate: 0,
  id: 'Q5'
})
// epd.device.conn.conn
const J4 = board.add(TE_2_1734839_4_1x24_1MP_P0_5mm_Horizontal, {
  translate: pt(2.903, 0.167), rotate: 0,
  id: 'J4'
})
// epd.vdd_cap.cap
const C8 = board.add(C_0603_1608Metric, {
  translate: pt(2.930, 0.624), rotate: 0,
  id: 'C8'
})
// epd.vdd1v8_cap.cap
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(3.086, 0.624), rotate: 0,
  id: 'C9'
})
// epd.vgl_cap.cap
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(3.242, 0.624), rotate: 0,
  id: 'C10'
})
// epd.vgh_cap.cap
const C11 = board.add(C_1206_3216Metric, {
  translate: pt(2.850, 0.346), rotate: 0,
  id: 'C11'
})
// epd.vsh_cap.cap
const C12 = board.add(C_1206_3216Metric, {
  translate: pt(3.070, 0.346), rotate: 0,
  id: 'C12'
})
// epd.vsl_cap.cap
const C13 = board.add(C_1206_3216Metric, {
  translate: pt(3.291, 0.346), rotate: 0,
  id: 'C13'
})
// epd.vcom_cap.cap
const C14 = board.add(C_0603_1608Metric, {
  translate: pt(3.398, 0.624), rotate: 0,
  id: 'C14'
})
// epd.boost.fet
const Q6 = board.add(SOT_23, {
  translate: pt(3.381, 0.067), rotate: 0,
  id: 'Q6'
})
// epd.boost.inductor
const L2 = board.add(L_1210_3225Metric, {
  translate: pt(2.630, 0.363), rotate: 0,
  id: 'L2'
})
// epd.boost.sense
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(2.598, 0.738), rotate: 0,
  id: 'R11'
})
// epd.boost.in_cap.cap
const C15 = board.add(C_0805_2012Metric, {
  translate: pt(3.269, 0.504), rotate: 0,
  id: 'C15'
})
// epd.boost.diode
const D4 = board.add(D_SOD_323, {
  translate: pt(3.438, 0.502), rotate: 0,
  id: 'D4'
})
// epd.boost.boot_neg_diode
const D5 = board.add(D_SOD_323, {
  translate: pt(2.604, 0.632), rotate: 0,
  id: 'D5'
})
// epd.boost.boot_gnd_diode
const D6 = board.add(D_SOD_323, {
  translate: pt(2.769, 0.632), rotate: 0,
  id: 'D6'
})
// epd.boost.boot_cap
const C16 = board.add(C_1206_3216Metric, {
  translate: pt(2.631, 0.510), rotate: 0,
  id: 'C16'
})
// epd.boost.out_cap.cap
const C17 = board.add(C_1206_3216Metric, {
  translate: pt(2.851, 0.510), rotate: 0,
  id: 'C17'
})
// epd.boost.neg_out_cap.cap
const C18 = board.add(C_1206_3216Metric, {
  translate: pt(3.072, 0.510), rotate: 0,
  id: 'C18'
})
// epd.gate_pdr
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(2.754, 0.738), rotate: 0,
  id: 'R12'
})
// tp_epd.tp_sck.tp
const TP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.902, 1.778), rotate: 0,
  id: 'TP4'
})
// tp_epd.tp_mosi.tp
const TP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.902, 1.892), rotate: 0,
  id: 'TP5'
})
// tp_epd.tp_miso.tp
const TP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.902, 2.006), rotate: 0,
  id: 'TP6'
})
// tp_erst.tp
const TP7 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.625, 2.247), rotate: 0,
  id: 'TP7'
})
// tp_dc.tp
const TP8 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.876, 2.247), rotate: 0,
  id: 'TP8'
})
// tp_epd_cs.tp
const TP9 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.126, 2.247), rotate: 0,
  id: 'TP9'
})
// tp_busy.tp
const TP10 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.376, 2.247), rotate: 0,
  id: 'TP10'
})
// sd
const J5 = board.add(microSD_HC_Molex_104031_0811, {
  translate: pt(2.809, 1.143), rotate: 0,
  id: 'J5'
})
// flash.ic
const U6 = board.add(SOIC_8_5_23x5_23mm_P1_27mm, {
  translate: pt(1.110, 1.853), rotate: 0,
  id: 'U6'
})
// flash.vcc_cap.cap
const C19 = board.add(C_0603_1608Metric, {
  translate: pt(0.985, 2.033), rotate: 0,
  id: 'C19'
})
// tp_sd.tp_sck.tp
const TP11 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.153, 1.778), rotate: 0,
  id: 'TP11'
})
// tp_sd.tp_mosi.tp
const TP12 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.153, 1.892), rotate: 0,
  id: 'TP12'
})
// tp_sd.tp_miso.tp
const TP13 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.153, 2.006), rotate: 0,
  id: 'TP13'
})
// tp_sd_cs.tp
const TP14 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.627, 2.247), rotate: 0,
  id: 'TP14'
})

board.setNetlist([
  {name: "gnd", pads: [["U3", "3"], ["J5", "6"], ["J5", "11"], ["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["J2", "1"], ["TP2", "1"], ["Q1", "1"], ["U1", "1"], ["Q2", "2"], ["U2", "1"], ["U2", "40"], ["U2", "41"], ["R6", "2"], ["R7", "2"], ["R8", "2"], ["SW2", "2"], ["U6", "4"], ["R10", "2"], ["J1", "S1"], ["R12", "2"], ["C1", "2"], ["C5", "2"], ["C6", "2"], ["J3", "5"], ["SW1", "2"], ["C8", "2"], ["C9", "2"], ["C10", "2"], ["C11", "2"], ["C12", "2"], ["C13", "2"], ["C14", "2"], ["C19", "2"], ["R2", "2"], ["C7", "2"], ["J4", "8"], ["R11", "2"], ["D6", "1"], ["C3", "2"], ["C4", "2"], ["C15", "2"], ["C17", "2"], ["C18", "2"], ["J4", "17"]]},
  {name: "vbat", pads: [["Q1", "2"], ["U1", "3"], ["R4", "1"], ["Q3", "2"], ["R3", "1"], ["C1", "1"], ["C3", "1"]]},
  {name: "v3v3", pads: [["TP3", "1"], ["U2", "2"], ["Q4", "2"], ["Q5", "2"], ["R1", "1"], ["C5", "1"], ["C6", "1"], ["J3", "1"], ["R5", "1"], ["L1", "2"], ["C4", "1"]]},
  {name: "batt.pwr", pads: [["J2", "2"], ["TP1", "1"], ["Q1", "3"]]},
  {name: "usb_chain_0.d_P", pads: [["J1", "A6"], ["J1", "B6"], ["U3", "2"], ["U2", "14"]]},
  {name: "usb_chain_0.d_N", pads: [["J1", "A7"], ["J1", "B7"], ["U3", "1"], ["U2", "13"]]},
  {name: "ledr.signal", pads: [["U2", "39"], ["D1", "2"]]},
  {name: "ledg.signal", pads: [["U2", "38"], ["D2", "2"]]},
  {name: "ledb.signal", pads: [["U2", "4"], ["D3", "2"]]},
  {name: "sw.out", pads: [["U2", "5"], ["SW2", "1"]]},
  {name: "vbat_sense_gate.control", pads: [["U2", "6"], ["Q2", "1"]]},
  {name: "vbat_sense_gate.output", pads: [["Q3", "3"], ["R9", "1"]]},
  {name: "vbat_sense.output", pads: [["U2", "7"], ["R9", "2"], ["R10", "1"]]},
  {name: "touch_duck.pad", pads: [["U2", "21"], ["U4", "1"]]},
  {name: "touch_lemur.pad", pads: [["U2", "22"], ["U5", "1"]]},
  {name: "epd_gate.control", pads: [["U2", "10"], ["Q4", "1"]]},
  {name: "mem_gate.control", pads: [["U2", "23"], ["Q5", "1"]]},
  {name: "epd_gate.output", pads: [["Q4", "3"], ["C8", "1"], ["J4", "9"], ["J4", "10"], ["L2", "1"], ["C15", "1"]]},
  {name: "tp_epd.io.sck", pads: [["U2", "33"], ["TP4", "1"], ["J4", "12"]]},
  {name: "tp_epd.io.mosi", pads: [["U2", "35"], ["TP5", "1"], ["J4", "11"]]},
  {name: "tp_epd.io.miso", pads: [["TP6", "1"]]},
  {name: "tp_erst.io", pads: [["U2", "8"], ["TP7", "1"], ["J4", "15"]]},
  {name: "tp_dc.io", pads: [["U2", "31"], ["TP8", "1"], ["J4", "14"]]},
  {name: "tp_epd_cs.io", pads: [["U2", "32"], ["TP9", "1"], ["J4", "13"]]},
  {name: "tp_busy.io", pads: [["U2", "9"], ["TP10", "1"], ["J4", "16"]]},
  {name: "mem_gate.output", pads: [["J5", "4"], ["Q5", "3"], ["U6", "8"], ["U6", "3"], ["U6", "7"], ["C19", "1"]]},
  {name: "tp_sd.io.sck", pads: [["U2", "17"], ["J5", "5"], ["U6", "6"], ["TP11", "1"]]},
  {name: "tp_sd.io.mosi", pads: [["U2", "18"], ["J5", "3"], ["U6", "5"], ["TP12", "1"]]},
  {name: "tp_sd.io.miso", pads: [["U2", "15"], ["J5", "7"], ["U6", "2"], ["TP13", "1"]]},
  {name: "tp_sd_cs.io", pads: [["U2", "19"], ["J5", "2"], ["TP14", "1"]]},
  {name: "flash.cs", pads: [["U2", "20"], ["U6", "1"]]},
  {name: "usb.pwr", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"]]},
  {name: "reg_3v3.fb.output", pads: [["U1", "4"], ["R1", "2"], ["R2", "1"]]},
  {name: "reg_3v3.boot_cap.neg", pads: [["C2", "2"], ["U1", "2"], ["L1", "1"]]},
  {name: "reg_3v3.boot_cap.pos", pads: [["C2", "1"], ["U1", "6"]]},
  {name: "reg_3v3.en_res.b", pads: [["R3", "2"], ["U1", "5"]]},
  {name: "vbat_sense_gate.pre.drain", pads: [["Q2", "3"], ["R4", "2"], ["Q3", "1"]]},
  {name: "mcu.program_uart_node.a_tx", pads: [["U2", "37"], ["J3", "3"]]},
  {name: "mcu.program_uart_node.b_tx", pads: [["U2", "36"], ["J3", "4"]]},
  {name: "mcu.program_en_node", pads: [["U2", "3"], ["J3", "6"], ["R5", "2"], ["C7", "1"]]},
  {name: "mcu.program_boot_node", pads: [["U2", "27"], ["SW1", "1"], ["J3", "2"]]},
  {name: "ledr.res.a", pads: [["R6", "1"], ["D1", "1"]]},
  {name: "ledg.res.a", pads: [["R7", "1"], ["D2", "1"]]},
  {name: "ledb.res.a", pads: [["R8", "1"], ["D3", "1"]]},
  {name: "epd.device.vdd1v8", pads: [["J4", "7"], ["C9", "1"]]},
  {name: "epd.device.vgl", pads: [["J4", "21"], ["C10", "1"]]},
  {name: "epd.device.vgh", pads: [["J4", "20"], ["C11", "1"]]},
  {name: "epd.device.vsh", pads: [["J4", "5"], ["C12", "1"]]},
  {name: "epd.device.vsl", pads: [["J4", "3"], ["C13", "1"]]},
  {name: "epd.device.vcom", pads: [["J4", "1"], ["C14", "1"]]},
  {name: "epd.device.gdr", pads: [["J4", "23"], ["R12", "1"], ["Q6", "1"]]},
  {name: "epd.device.rese", pads: [["J4", "22"], ["Q6", "2"], ["R11", "1"]]},
  {name: "epd.boost.pos_out", pads: [["J4", "4"], ["D4", "1"], ["C17", "1"]]},
  {name: "epd.boost.neg_out", pads: [["J4", "2"], ["D5", "2"], ["C18", "1"]]},
  {name: "epd.boost.inductor.b", pads: [["L2", "2"], ["Q6", "3"], ["D4", "2"], ["C16", "1"]]},
  {name: "epd.boost.boot_cap.neg", pads: [["C16", "2"], ["D5", "1"], ["D6", "2"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.746456692913387, 2.4618110236220474);
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


