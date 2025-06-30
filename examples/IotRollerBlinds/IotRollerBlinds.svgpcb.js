const board = new PCB();

// jlc_th.th1
const BH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.235, 2.076), rotate: 0,
  id: 'BH1'
})
// jlc_th.th2
const BH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.274, 2.076), rotate: 0,
  id: 'BH2'
})
// jlc_th.th3
const BH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.235, 2.116), rotate: 0,
  id: 'BH3'
})
// pwr.conn
const BJ1 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.096, 1.872), rotate: 0,
  id: 'BJ1'
})
// pwr_out.conn
const BJ2 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.486, 1.872), rotate: 0,
  id: 'BJ2'
})
// conn.conn
const BJ3 = board.add(JST_XH_B6B_XH_A_1x06_P2_50mm_Vertical, {
  translate: pt(0.744, 1.276), rotate: 0,
  id: 'BJ3'
})
// tp_gnd.tp
const BTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.550, 1.779), rotate: 0,
  id: 'BTP1'
})
// fuse.fuse
const BF1 = board.add(Fuseholder_Littelfuse_Nano2_154x, {
  translate: pt(2.115, 1.231), rotate: 0,
  id: 'BF1'
})
// ferrite.fb
const BFB1 = board.add(L_0603_1608Metric, {
  translate: pt(0.058, 2.105), rotate: 0,
  id: 'BFB1'
})
// tp_vin.tp
const BTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.800, 1.779), rotate: 0,
  id: 'BTP2'
})
// reg_3v3.ic
const BU1 = board.add(SOT_23_6, {
  translate: pt(0.301, 1.189), rotate: 0,
  id: 'BU1'
})
// reg_3v3.fb.div.top_res
const BR1 = board.add(R_0603_1608Metric, {
  translate: pt(0.452, 1.368), rotate: 0,
  id: 'BR1'
})
// reg_3v3.fb.div.bottom_res
const BR2 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.498), rotate: 0,
  id: 'BR2'
})
// reg_3v3.hf_in_cap.cap
const BC1 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.498), rotate: 0,
  id: 'BC1'
})
// reg_3v3.boot_cap
const BC2 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 1.498), rotate: 0,
  id: 'BC2'
})
// reg_3v3.power_path.inductor
const BL1 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(0.091, 1.211), rotate: 0,
  id: 'BL1'
})
// reg_3v3.power_path.in_cap.cap
const BC3 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 1.385), rotate: 0,
  id: 'BC3'
})
// reg_3v3.power_path.out_cap.cap
const BC4 = board.add(C_0805_2012Metric, {
  translate: pt(0.287, 1.378), rotate: 0,
  id: 'BC4'
})
// reg_3v3.en_res
const BR3 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.595), rotate: 0,
  id: 'BR3'
})
// tp_3v3.tp
const BTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.051, 1.779), rotate: 0,
  id: 'BTP3'
})
// prot_3v3.diode
const BD1 = board.add(D_SOD_323, {
  translate: pt(2.298, 1.779), rotate: 0,
  id: 'BD1'
})
// mcu.ic
const BU2 = board.add(ESP_WROOM_02, {
  translate: pt(0.561, 0.281), rotate: 0,
  id: 'BU2'
})
// mcu.vcc_cap0.cap
const BC5 = board.add(C_0805_2012Metric, {
  translate: pt(1.228, 0.413), rotate: 0,
  id: 'BC5'
})
// mcu.vcc_cap1.cap
const BC6 = board.add(C_0603_1608Metric, {
  translate: pt(1.393, 0.403), rotate: 0,
  id: 'BC6'
})
// mcu.prog.conn
const BJ4 = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(1.329, 0.167), rotate: 0,
  id: 'BJ4'
})
// mcu.en_pull.rc.r
const BR4 = board.add(R_0603_1608Metric, {
  translate: pt(1.220, 0.519), rotate: 0,
  id: 'BR4'
})
// mcu.en_pull.rc.c
const BC7 = board.add(C_0603_1608Metric, {
  translate: pt(1.376, 0.519), rotate: 0,
  id: 'BC7'
})
// ledr.package
const BD2 = board.add(LED_0603_1608Metric, {
  translate: pt(0.838, 1.771), rotate: 0,
  id: 'BD2'
})
// ledr.res
const BR5 = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 1.868), rotate: 0,
  id: 'BR5'
})
// vin_sense.div.top_res
const BR6 = board.add(R_0603_1608Metric, {
  translate: pt(1.073, 1.770), rotate: 0,
  id: 'BR6'
})
// vin_sense.div.bottom_res
const BR7 = board.add(R_0603_1608Metric, {
  translate: pt(1.073, 1.867), rotate: 0,
  id: 'BR7'
})
// qwiic_pull.scl_res.res
const BR8 = board.add(R_0603_1608Metric, {
  translate: pt(1.307, 1.770), rotate: 0,
  id: 'BR8'
})
// qwiic_pull.sda_res.res
const BR9 = board.add(R_0603_1608Metric, {
  translate: pt(1.307, 1.867), rotate: 0,
  id: 'BR9'
})
// qwiic.conn
const BJ5 = board.add(JST_SH_SM04B_SRSS_TB_1x04_1MP_P1_00mm_Horizontal, {
  translate: pt(1.624, 1.251), rotate: 0,
  id: 'BJ5'
})
// drv.ic
const BU3 = board.add(HSOP_8_1EP_3_9x4_9mm_P1_27mm_EP2_41x3_1mm, {
  translate: pt(1.740, 0.492), rotate: 0,
  id: 'BU3'
})
// drv.vm_cap0.cap
const BC8 = board.add(C_0603_1608Metric, {
  translate: pt(2.202, 0.415), rotate: 0,
  id: 'BC8'
})
// drv.vm_cap1.cap
const BC9 = board.add(CP_Elec_8x10, {
  translate: pt(1.811, 0.173), rotate: 0,
  id: 'BC9'
})
// drv.isen_res.res
const BR10 = board.add(R_1206_3216Metric, {
  translate: pt(2.015, 0.430), rotate: 0,
  id: 'BR10'
})

board.setNetlist([
  {name: "Bvin_raw", pads: [["BJ1", "2"], ["BJ2", "2"], ["BF1", "1"]]},
  {name: "Bgnd", pads: [["BJ1", "1"], ["BJ2", "1"], ["BJ3", "4"], ["BTP1", "1"], ["BU1", "1"], ["BD1", "2"], ["BU2", "9"], ["BU2", "19"], ["BJ5", "1"], ["BU3", "1"], ["BU3", "9"], ["BR7", "2"], ["BC1", "2"], ["BC5", "2"], ["BC6", "2"], ["BJ4", "5"], ["BC8", "2"], ["BC9", "2"], ["BR2", "2"], ["BC7", "2"], ["BR10", "1"], ["BC3", "2"], ["BC4", "2"]]},
  {name: "Bvin", pads: [["BFB1", "2"], ["BTP2", "1"], ["BJ3", "1"], ["BU1", "3"], ["BU3", "5"], ["BR6", "1"], ["BR3", "1"], ["BC1", "1"], ["BC8", "1"], ["BC9", "1"], ["BC3", "1"]]},
  {name: "Bv3v3", pads: [["BU3", "4"], ["BTP3", "1"], ["BD1", "1"], ["BU2", "1"], ["BD2", "2"], ["BJ5", "2"], ["BR1", "1"], ["BU2", "7"], ["BU2", "16"], ["BC5", "1"], ["BC6", "1"], ["BJ4", "1"], ["BR8", "1"], ["BR9", "1"], ["BR4", "1"], ["BL1", "2"], ["BC4", "1"]]},
  {name: "Bfuse.pwr_out", pads: [["BF1", "2"], ["BFB1", "1"]]},
  {name: "Bmcu.program_boot_node", pads: [["BR5", "2"], ["BU2", "8"], ["BJ4", "2"]]},
  {name: "Bvin_sense.output", pads: [["BU2", "4"], ["BR6", "2"], ["BR7", "1"]]},
  {name: "Bconn.enca", pads: [["BU2", "13"], ["BJ3", "2"]]},
  {name: "Bconn.encb", pads: [["BU2", "10"], ["BJ3", "3"]]},
  {name: "Bqwiic_pull.i2c.scl", pads: [["BU2", "5"], ["BR8", "2"], ["BJ5", "4"]]},
  {name: "Bqwiic_pull.i2c.sda", pads: [["BU2", "6"], ["BJ5", "3"], ["BR9", "2"]]},
  {name: "Bdrv.in1", pads: [["BU2", "15"], ["BU3", "3"]]},
  {name: "Bdrv.in2", pads: [["BU2", "14"], ["BU3", "2"]]},
  {name: "Bdrv.out1", pads: [["BU3", "6"], ["BJ3", "5"]]},
  {name: "Bdrv.out2", pads: [["BU3", "8"], ["BJ3", "6"]]},
  {name: "Breg_3v3.fb.output", pads: [["BU1", "4"], ["BR1", "2"], ["BR2", "1"]]},
  {name: "Breg_3v3.boot_cap.neg", pads: [["BC2", "2"], ["BU1", "2"], ["BL1", "1"]]},
  {name: "Breg_3v3.boot_cap.pos", pads: [["BC2", "1"], ["BU1", "6"]]},
  {name: "Breg_3v3.en_res.b", pads: [["BR3", "2"], ["BU1", "5"]]},
  {name: "Bmcu.program_uart_node.a_tx", pads: [["BU2", "12"], ["BJ4", "3"]]},
  {name: "Bmcu.program_uart_node.b_tx", pads: [["BU2", "11"], ["BJ4", "4"]]},
  {name: "Bmcu.program_en_node", pads: [["BU2", "2"], ["BJ4", "6"], ["BR4", "2"], ["BC7", "1"]]},
  {name: "Bledr.res.a", pads: [["BR5", "1"], ["BD2", "1"]]},
  {name: "Bdrv.ic.isen", pads: [["BU3", "7"], ["BR10", "2"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.4793307086614176, 2.2519685039370083);
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


