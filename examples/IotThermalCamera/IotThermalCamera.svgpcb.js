const board = new PCB();

// jlc_th.th1
const TH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.379, 3.103), rotate: 0,
  id: 'TH1'
})
// jlc_th.th2
const TH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.418, 3.103), rotate: 0,
  id: 'TH2'
})
// jlc_th.th3
const TH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.379, 3.143), rotate: 0,
  id: 'TH3'
})
// usb.conn
const TJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.825, 2.719), rotate: 0,
  id: 'TJ1'
})
// eth.conn
const TJ2 = board.add(RJ45_Wuerth_7499111446_Horizontal, {
  translate: pt(2.527, 0.798), rotate: 0,
  id: 'TJ2'
})
// eth.led_yel_res
const TR1 = board.add(R_0603_1608Metric, {
  translate: pt(3.438, 0.029), rotate: 0,
  id: 'TR1'
})
// eth.led_grn_res
const TR2 = board.add(R_0603_1608Metric, {
  translate: pt(3.218, 0.159), rotate: 0,
  id: 'TR2'
})
// eth.cap
const TC1 = board.add(C_1206_3216Metric, {
  translate: pt(3.250, 0.045), rotate: 0,
  id: 'TC1'
})
// poe.ic
const TU1 = board.add(HSOP_8_1EP_3_9x4_9mm_P1_27mm_EP2_41x3_1mm_ThermalVias, {
  translate: pt(2.779, 1.846), rotate: 0,
  id: 'TU1'
})
// poe.cls.res
const TR3 = board.add(R_0603_1608Metric, {
  translate: pt(2.691, 2.198), rotate: 0,
  id: 'TR3'
})
// poe.den
const TR4 = board.add(R_0603_1608Metric, {
  translate: pt(2.847, 2.198), rotate: 0,
  id: 'TR4'
})
// poe.vdd_cap.cap
const TC2 = board.add(C_0805_2012Metric, {
  translate: pt(3.015, 2.031), rotate: 0,
  id: 'TC2'
})
// poe.prot.diode
const TD1 = board.add(D_SMA, {
  translate: pt(2.771, 2.061), rotate: 0,
  id: 'TD1'
})
// poe_jmp.pos
const TJP1 = board.add(SolderJumper_2_P1_3mm_Open_TrianglePad1_0x1_5mm, {
  translate: pt(3.038, 2.604), rotate: 0,
  id: 'TJP1'
})
// poe_jmp.neg
const TJP2 = board.add(SolderJumper_2_P1_3mm_Open_TrianglePad1_0x1_5mm, {
  translate: pt(3.038, 2.741), rotate: 0,
  id: 'TJP2'
})
// tp_gnd.tp
const TTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.018, 3.141), rotate: 0,
  id: 'TTP1'
})
// tp_poe.tp
const TTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.269, 3.141), rotate: 0,
  id: 'TTP2'
})
// reg_poe.ic
const TU2 = board.add(HSOP_8_1EP_3_9x4_9mm_P1_27mm_EP2_41x3_1mm_ThermalVias, {
  translate: pt(0.406, 2.661), rotate: 0,
  id: 'TU2'
})
// reg_poe.fb.div.top_res
const TR5 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.956), rotate: 0,
  id: 'TR5'
})
// reg_poe.fb.div.bottom_res
const TR6 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.956), rotate: 0,
  id: 'TR6'
})
// reg_poe.hf_cap.cap
const TC3 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 2.850), rotate: 0,
  id: 'TC3'
})
// reg_poe.boot_cap.cap
const TC4 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 2.956), rotate: 0,
  id: 'TC4'
})
// reg_poe.rt.res
const TR7 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 2.956), rotate: 0,
  id: 'TR7'
})
// reg_poe.power_path.inductor
const TL1 = board.add(L_Sunlord_SWPA5040S, {
  translate: pt(0.110, 2.663), rotate: 0,
  id: 'TL1'
})
// reg_poe.power_path.in_cap.cap.c[0]
const TC5 = board.add(C_0805_2012Metric, {
  translate: pt(0.240, 2.850), rotate: 0,
  id: 'TC5'
})
// reg_poe.power_path.in_cap.cap.c[1]
const TC6 = board.add(C_0805_2012Metric, {
  translate: pt(0.413, 2.850), rotate: 0,
  id: 'TC6'
})
// reg_poe.power_path.out_cap.cap
const TC7 = board.add(C_0805_2012Metric, {
  translate: pt(0.587, 2.850), rotate: 0,
  id: 'TC7'
})
// prot_v5.diode
const TD2 = board.add(D_SOD_123, {
  translate: pt(1.438, 3.148), rotate: 0,
  id: 'TD2'
})
// choke.fb
const TFB1 = board.add(L_0603_1608Metric, {
  translate: pt(3.012, 3.132), rotate: 0,
  id: 'TFB1'
})
// tp_pwr.tp
const TTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.519, 3.141), rotate: 0,
  id: 'TTP3'
})
// reg_3v3.ic
const TU3 = board.add(SOT_23_6, {
  translate: pt(2.259, 1.807), rotate: 0,
  id: 'TU3'
})
// reg_3v3.fb.div.top_res
const TR8 = board.add(R_0603_1608Metric, {
  translate: pt(2.457, 1.986), rotate: 0,
  id: 'TR8'
})
// reg_3v3.fb.div.bottom_res
const TR9 = board.add(R_0603_1608Metric, {
  translate: pt(2.016, 2.116), rotate: 0,
  id: 'TR9'
})
// reg_3v3.hf_in_cap.cap
const TC8 = board.add(C_0603_1608Metric, {
  translate: pt(2.172, 2.116), rotate: 0,
  id: 'TC8'
})
// reg_3v3.boot_cap.cap
const TC9 = board.add(C_0603_1608Metric, {
  translate: pt(2.328, 2.116), rotate: 0,
  id: 'TC9'
})
// reg_3v3.power_path.inductor
const TL2 = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(2.048, 1.829), rotate: 0,
  id: 'TL2'
})
// reg_3v3.power_path.in_cap.cap
const TC10 = board.add(C_1206_3216Metric, {
  translate: pt(2.048, 2.003), rotate: 0,
  id: 'TC10'
})
// reg_3v3.power_path.out_cap.cap
const TC11 = board.add(C_1206_3216Metric, {
  translate: pt(2.269, 2.003), rotate: 0,
  id: 'TC11'
})
// reg_3v3.en_res.res
const TR10 = board.add(R_0603_1608Metric, {
  translate: pt(2.016, 2.213), rotate: 0,
  id: 'TR10'
})
// tp_3v3.tp
const TTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.769, 3.141), rotate: 0,
  id: 'TTP4'
})
// prot_3v3.diode
const TD3 = board.add(D_SOD_123, {
  translate: pt(1.742, 3.148), rotate: 0,
  id: 'TD3'
})
// reg_3v0.ic
const TU4 = board.add(SOT_23_5, {
  translate: pt(3.302, 2.621), rotate: 0,
  id: 'TU4'
})
// reg_3v0.in_cap.cap
const TC12 = board.add(C_0603_1608Metric, {
  translate: pt(3.280, 2.756), rotate: 0,
  id: 'TC12'
})
// reg_3v0.out_cap.cap
const TC13 = board.add(C_0603_1608Metric, {
  translate: pt(3.435, 2.756), rotate: 0,
  id: 'TC13'
})
// reg_2v8.ic
const TU5 = board.add(SOT_23_5, {
  translate: pt(3.693, 2.621), rotate: 0,
  id: 'TU5'
})
// reg_2v8.in_cap.cap
const TC14 = board.add(C_0603_1608Metric, {
  translate: pt(3.670, 2.756), rotate: 0,
  id: 'TC14'
})
// reg_2v8.out_cap.cap
const TC15 = board.add(C_0603_1608Metric, {
  translate: pt(3.826, 2.756), rotate: 0,
  id: 'TC15'
})
// reg_1v2.ic
const TU6 = board.add(SOT_23_5, {
  translate: pt(0.081, 3.170), rotate: 0,
  id: 'TU6'
})
// reg_1v2.in_cap.cap
const TC16 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 3.305), rotate: 0,
  id: 'TC16'
})
// reg_1v2.out_cap.cap
const TC17 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 3.305), rotate: 0,
  id: 'TC17'
})
// mcu.prog.conn
const TJ3 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(2.067, 0.079), rotate: 0,
  id: 'TJ3'
})
// mcu.ic
const TU7 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'TU7'
})
// mcu.vcc_cap0.cap
const TC18 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.242), rotate: 0,
  id: 'TC18'
})
// mcu.vcc_cap1.cap
const TC19 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.226), rotate: 0,
  id: 'TC19'
})
// mcu.en_pull.rc.r
const TR11 = board.add(R_0603_1608Metric, {
  translate: pt(1.987, 0.356), rotate: 0,
  id: 'TR11'
})
// mcu.en_pull.rc.c
const TC20 = board.add(C_0603_1608Metric, {
  translate: pt(2.143, 0.356), rotate: 0,
  id: 'TC20'
})
// ledr.package
const TD4 = board.add(LED_0603_1608Metric, {
  translate: pt(0.699, 3.132), rotate: 0,
  id: 'TD4'
})
// ledr.res
const TR12 = board.add(R_0603_1608Metric, {
  translate: pt(0.699, 3.229), rotate: 0,
  id: 'TR12'
})
// phy.ic
const TU8 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 1.943), rotate: 0,
  id: 'TU8'
})
// phy.l.fb
const TFB2 = board.add(L_0603_1608Metric, {
  translate: pt(0.676, 1.942), rotate: 0,
  id: 'TFB2'
})
// phy.crystal.package
const TX1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(0.528, 1.807), rotate: 0,
  id: 'TX1'
})
// phy.crystal.cap_a
const TC21 = board.add(C_0603_1608Metric, {
  translate: pt(0.832, 1.942), rotate: 0,
  id: 'TC21'
})
// phy.crystal.cap_b
const TC22 = board.add(C_0603_1608Metric, {
  translate: pt(0.988, 1.942), rotate: 0,
  id: 'TC22'
})
// phy.exres1.res
const TR13 = board.add(R_0603_1608Metric, {
  translate: pt(0.503, 2.059), rotate: 0,
  id: 'TR13'
})
// phy.c1v20.cap
const TC23 = board.add(C_0603_1608Metric, {
  translate: pt(0.659, 2.059), rotate: 0,
  id: 'TC23'
})
// phy.tocap.cap
const TC24 = board.add(C_0805_2012Metric, {
  translate: pt(0.717, 1.779), rotate: 0,
  id: 'TC24'
})
// phy.vdd_cap0.cap
const TC25 = board.add(C_0603_1608Metric, {
  translate: pt(0.815, 2.059), rotate: 0,
  id: 'TC25'
})
// phy.vdd_cap1.cap
const TC26 = board.add(C_0805_2012Metric, {
  translate: pt(0.890, 1.779), rotate: 0,
  id: 'TC26'
})
// phy.avdd_caps[0].cap
const TC27 = board.add(C_0603_1608Metric, {
  translate: pt(0.971, 2.059), rotate: 0,
  id: 'TC27'
})
// phy.avdd_caps[1].cap
const TC28 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.214), rotate: 0,
  id: 'TC28'
})
// phy.avdd_caps[2].cap
const TC29 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 2.214), rotate: 0,
  id: 'TC29'
})
// phy.avdd_caps[3].cap
const TC30 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 2.214), rotate: 0,
  id: 'TC30'
})
// phy.avdd_caps[4].cap
const TC31 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 2.214), rotate: 0,
  id: 'TC31'
})
// phy.avdd_caps[5].cap
const TC32 = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 2.214), rotate: 0,
  id: 'TC32'
})
// phy.avdd_caps[6].cap
const TC33 = board.add(C_0805_2012Metric, {
  translate: pt(0.512, 1.952), rotate: 0,
  id: 'TC33'
})
// phy.txp_damp
const TR14 = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 2.214), rotate: 0,
  id: 'TR14'
})
// phy.txn_damp
const TR15 = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 2.214), rotate: 0,
  id: 'TR15'
})
// phy.rxp_damp
const TR16 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.311), rotate: 0,
  id: 'TR16'
})
// phy.rxn_damp
const TR17 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.311), rotate: 0,
  id: 'TR17'
})
// phy.txp_bias
const TR18 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 2.311), rotate: 0,
  id: 'TR18'
})
// phy.txn_bias
const TR19 = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 2.311), rotate: 0,
  id: 'TR19'
})
// phy.txc_bias
const TR20 = board.add(R_0603_1608Metric, {
  translate: pt(0.682, 2.311), rotate: 0,
  id: 'TR20'
})
// phy.txc_cap
const TC34 = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 2.311), rotate: 0,
  id: 'TC34'
})
// phy.rxp_ac
const TC35 = board.add(C_0603_1608Metric, {
  translate: pt(0.994, 2.311), rotate: 0,
  id: 'TC35'
})
// phy.rxn_ac
const TC36 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.407), rotate: 0,
  id: 'TC36'
})
// phy.rxp_bias
const TR21 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.407), rotate: 0,
  id: 'TR21'
})
// phy.rxn_bias
const TR22 = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 2.407), rotate: 0,
  id: 'TR22'
})
// phy.rxc_cap
const TC37 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 2.407), rotate: 0,
  id: 'TC37'
})
// usb_esd
const TU9 = board.add(SOT_23, {
  translate: pt(3.264, 3.170), rotate: 0,
  id: 'TU9'
})
// i2c_pull.scl_res.res
const TR23 = board.add(R_0603_1608Metric, {
  translate: pt(0.934, 3.132), rotate: 0,
  id: 'TR23'
})
// i2c_pull.sda_res.res
const TR24 = board.add(R_0603_1608Metric, {
  translate: pt(0.934, 3.229), rotate: 0,
  id: 'TR24'
})
// i2c_tp.tp_scl.tp
const TTP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.457, 3.141), rotate: 0,
  id: 'TTP5'
})
// i2c_tp.tp_sda.tp
const TTP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.457, 3.255), rotate: 0,
  id: 'TTP6'
})
// dist.ic
const TU10 = board.add(ST_VL53L5x, {
  translate: pt(2.465, 2.768), rotate: 0,
  id: 'TU10'
})
// dist.avdd_cap.cap
const TC38 = board.add(C_0805_2012Metric, {
  translate: pt(2.220, 2.593), rotate: 0,
  id: 'TC38'
})
// dist.iovdd_cap.cap
const TC39 = board.add(C_0603_1608Metric, {
  translate: pt(2.384, 2.583), rotate: 0,
  id: 'TC39'
})
// dist.lpn_pull.res
const TR25 = board.add(R_0603_1608Metric, {
  translate: pt(2.211, 2.700), rotate: 0,
  id: 'TR25'
})
// dist.rsvd6_pull.res
const TR26 = board.add(R_0603_1608Metric, {
  translate: pt(2.367, 2.700), rotate: 0,
  id: 'TR26'
})
// dist.i2c_rst_pull.res
const TR27 = board.add(R_0603_1608Metric, {
  translate: pt(2.211, 2.796), rotate: 0,
  id: 'TR27'
})
// dist.int_pull.res
const TR28 = board.add(R_0603_1608Metric, {
  translate: pt(2.367, 2.796), rotate: 0,
  id: 'TR28'
})
// pd.ic
const TU11 = board.add(WQFN_14_1EP_2_5x2_5mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(2.656, 2.627), rotate: 0,
  id: 'TU11'
})
// pd.vdd_cap[0].cap
const TC40 = board.add(C_0603_1608Metric, {
  translate: pt(2.641, 2.768), rotate: 0,
  id: 'TC40'
})
// pd.vdd_cap[1].cap
const TC41 = board.add(C_0603_1608Metric, {
  translate: pt(2.797, 2.768), rotate: 0,
  id: 'TC41'
})
// ioe.ic
const TU12 = board.add(TSSOP_20_4_4x6_5mm_P0_65mm, {
  translate: pt(3.352, 1.878), rotate: 0,
  id: 'TU12'
})
// ioe.sdi.conn
const TJ4 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(3.338, 2.134), rotate: 0,
  id: 'TJ4'
})
// ioe.vdd_cap.cap
const TC42 = board.add(C_0603_1608Metric, {
  translate: pt(3.574, 2.084), rotate: 0,
  id: 'TC42'
})
// ioe.reset_cap.cap
const TC43 = board.add(C_0603_1608Metric, {
  translate: pt(3.574, 2.181), rotate: 0,
  id: 'TC43'
})
// poe_sense.div.top_res
const TR29 = board.add(R_0603_1608Metric, {
  translate: pt(1.169, 3.132), rotate: 0,
  id: 'TR29'
})
// poe_sense.div.bottom_res
const TR30 = board.add(R_0603_1608Metric, {
  translate: pt(1.169, 3.229), rotate: 0,
  id: 'TR30'
})
// cam.device.conn.conn
const TJ5 = board.add(TE_2_1734839_4_1x24_1MP_P0_5mm_Horizontal, {
  translate: pt(1.135, 2.722), rotate: 0,
  id: 'TJ5'
})
// cam.dovdd_cap.cap
const TC44 = board.add(C_0603_1608Metric, {
  translate: pt(0.830, 2.884), rotate: 0,
  id: 'TC44'
})
// cam.reset_cap.cap
const TC45 = board.add(C_0603_1608Metric, {
  translate: pt(0.986, 2.884), rotate: 0,
  id: 'TC45'
})
// cam.pclk_cap.cap
const TC46 = board.add(C_0603_1608Metric, {
  translate: pt(1.142, 2.884), rotate: 0,
  id: 'TC46'
})
// flir.ic
const TU13 = board.add(Molex_1050281001, {
  translate: pt(1.402, 1.972), rotate: 0,
  id: 'TU13'
})
// flir.vddc_cap.cap
const TC47 = board.add(C_0603_1608Metric, {
  translate: pt(1.732, 1.942), rotate: 0,
  id: 'TC47'
})
// flir.vddio_cap.cap
const TC48 = board.add(C_0603_1608Metric, {
  translate: pt(1.732, 2.039), rotate: 0,
  id: 'TC48'
})
// flir.vdd_cap.cap
const TC49 = board.add(C_0603_1608Metric, {
  translate: pt(1.732, 2.136), rotate: 0,
  id: 'TC49'
})
// flir.mclk.device
const TX2 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(1.757, 1.807), rotate: 0,
  id: 'TX2'
})
// flir.mclk.cap.cap
const TC50 = board.add(C_0603_1608Metric, {
  translate: pt(1.228, 2.273), rotate: 0,
  id: 'TC50'
})

board.setNetlist([
  {name: "Tgnd", pads: [["TJ1", "A1"], ["TJ1", "A12"], ["TJ1", "B1"], ["TJ1", "B12"], ["TJ1", "S1"], ["TC1", "2"], ["TU1", "5"], ["TU1", "8"], ["TTP1", "1"], ["TU2", "1"], ["TU2", "9"], ["TR6", "2"], ["TC3", "2"], ["TR7", "1"], ["TC5", "2"], ["TC6", "2"], ["TC7", "2"], ["TD2", "2"], ["TU3", "1"], ["TR9", "2"], ["TC8", "2"], ["TC10", "2"], ["TC11", "2"], ["TD3", "2"], ["TU4", "2"], ["TC12", "2"], ["TC13", "2"], ["TU5", "2"], ["TC14", "2"], ["TC15", "2"], ["TU6", "2"], ["TC16", "2"], ["TC17", "2"], ["TJ3", "5"], ["TU7", "1"], ["TU7", "40"], ["TU7", "41"], ["TC18", "2"], ["TC19", "2"], ["TC20", "2"], ["TR12", "2"], ["TU8", "14"], ["TU8", "16"], ["TU8", "19"], ["TU8", "23"], ["TU8", "29"], ["TU8", "3"], ["TU8", "48"], ["TU8", "9"], ["TX1", "2"], ["TX1", "4"], ["TC21", "2"], ["TC22", "2"], ["TR13", "1"], ["TC23", "2"], ["TC24", "2"], ["TC25", "2"], ["TC26", "2"], ["TC27", "2"], ["TC28", "2"], ["TC29", "2"], ["TC30", "2"], ["TC31", "2"], ["TC32", "2"], ["TC33", "2"], ["TC34", "2"], ["TC37", "2"], ["TU9", "3"], ["TU10", "A2"], ["TU10", "A6"], ["TU10", "A7"], ["TU10", "B4"], ["TU10", "C1"], ["TU10", "C6"], ["TU10", "C7"], ["TC38", "2"], ["TC39", "2"], ["TR27", "1"], ["TU11", "15"], ["TU11", "8"], ["TU11", "9"], ["TC40", "2"], ["TC41", "2"], ["TU12", "7"], ["TJ4", "5"], ["TC42", "2"], ["TC43", "2"], ["TR30", "2"], ["TJ5", "15"], ["TJ5", "2"], ["TJ5", "8"], ["TC44", "2"], ["TC45", "2"], ["TC46", "2"], ["TU13", "1"], ["TU13", "10"], ["TU13", "15"], ["TU13", "18"], ["TU13", "20"], ["TU13", "25"], ["TU13", "27"], ["TU13", "30"], ["TU13", "33"], ["TU13", "6"], ["TU13", "8"], ["TU13", "9"], ["TC47", "2"], ["TC48", "2"], ["TC49", "2"], ["TX2", "2"], ["TC50", "2"]]},
  {name: "Tpwr", pads: [["TFB1", "2"], ["TTP3", "1"], ["TU3", "3"], ["TC8", "1"], ["TC10", "1"], ["TR10", "1"], ["TR29", "1"]]},
  {name: "Tv3v3", pads: [["TJ2", "11"], ["TJ2", "13"], ["TR8", "1"], ["TL2", "2"], ["TC11", "1"], ["TTP4", "1"], ["TD3", "1"], ["TU4", "1"], ["TU4", "3"], ["TC12", "1"], ["TU5", "1"], ["TU5", "3"], ["TC14", "1"], ["TU6", "1"], ["TU6", "3"], ["TC16", "1"], ["TJ3", "1"], ["TU7", "2"], ["TC18", "1"], ["TC19", "1"], ["TR11", "1"], ["TU8", "28"], ["TU8", "43"], ["TU8", "44"], ["TU8", "45"], ["TFB2", "1"], ["TC25", "1"], ["TC26", "1"], ["TR23", "1"], ["TR24", "1"], ["TU10", "A4"], ["TU10", "B1"], ["TU10", "B7"], ["TC38", "1"], ["TC39", "1"], ["TR25", "1"], ["TR26", "1"], ["TR28", "1"], ["TU11", "3"], ["TU11", "4"], ["TC40", "1"], ["TC41", "1"], ["TU12", "9"], ["TJ4", "1"], ["TC42", "1"]]},
  {name: "Tv3v0", pads: [["TU4", "5"], ["TC13", "1"], ["TJ5", "11"], ["TC44", "1"], ["TU13", "16"], ["TC48", "1"], ["TX2", "1"], ["TX2", "4"], ["TC50", "1"]]},
  {name: "Tv2v8", pads: [["TU5", "5"], ["TC15", "1"], ["TJ5", "4"], ["TU13", "19"], ["TC49", "1"]]},
  {name: "Tv1v2", pads: [["TU6", "5"], ["TC17", "1"], ["TJ5", "10"], ["TU13", "7"], ["TC47", "1"]]},
  {name: "Tusb_chain_0.d_P", pads: [["TJ1", "A6"], ["TJ1", "B6"], ["TU7", "14"], ["TU9", "2"]]},
  {name: "Tusb_chain_0.d_N", pads: [["TJ1", "A7"], ["TJ1", "B7"], ["TU7", "13"], ["TU9", "1"]]},
  {name: "Ti2c_chain_0.scl", pads: [["TU7", "33"], ["TR23", "2"], ["TTP5", "1"], ["TU10", "C4"], ["TU11", "6"], ["TU12", "12"], ["TJ5", "5"], ["TU13", "21"]]},
  {name: "Ti2c_chain_0.sda", pads: [["TU7", "32"], ["TR24", "2"], ["TTP6", "1"], ["TU10", "C3"], ["TU11", "7"], ["TU12", "11"], ["TJ5", "3"], ["TU13", "22"]]},
  {name: "Tusb.pwr", pads: [["TJ1", "A4"], ["TJ1", "A9"], ["TJ1", "B4"], ["TJ1", "B9"], ["TR5", "1"], ["TL1", "2"], ["TC7", "1"], ["TD2", "1"], ["TFB1", "1"], ["TU11", "2"]]},
  {name: "Tusb.cc.cc1", pads: [["TJ1", "A5"], ["TU11", "10"], ["TU11", "11"]]},
  {name: "Tusb.cc.cc2", pads: [["TJ1", "B5"], ["TU11", "1"], ["TU11", "14"]]},
  {name: "Teth.eth.tx.pos", pads: [["TJ2", "5"], ["TR14", "2"], ["TR18", "2"]]},
  {name: "Teth.eth.tx.neg", pads: [["TJ2", "6"], ["TR15", "2"], ["TR19", "2"]]},
  {name: "Teth.eth.tx.center", pads: [["TJ2", "4"], ["TR20", "2"], ["TC34", "1"]]},
  {name: "Teth.eth.rx.pos", pads: [["TJ2", "1"], ["TC35", "1"]]},
  {name: "Teth.eth.rx.neg", pads: [["TJ2", "2"], ["TC36", "1"]]},
  {name: "Teth.eth.rx.center", pads: [["TJ2", "3"], ["TR21", "2"], ["TR22", "2"], ["TC37", "1"]]},
  {name: "Teth.poe.pos", pads: [["TJ2", "9"], ["TJP1", "1"]]},
  {name: "Teth.poe.neg", pads: [["TJ2", "10"], ["TJP2", "1"]]},
  {name: "Teth.led_yel_sink", pads: [["TR1", "2"], ["TU12", "10"]]},
  {name: "Teth.led_grn_sink", pads: [["TR2", "2"], ["TU12", "8"]]},
  {name: "Teth.conn.led_grn_cathode", pads: [["TJ2", "14"], ["TR2", "1"]]},
  {name: "Teth.conn.led_yel_cathode", pads: [["TJ2", "12"], ["TR1", "1"]]},
  {name: "Teth.conn.shield", pads: [["TJ2", "SH"], ["TC1", "1"]]},
  {name: "Tpoe.pwr_out", pads: [["TU1", "1"], ["TR4", "1"], ["TC2", "1"], ["TD1", "1"], ["TJP1", "2"], ["TTP2", "1"], ["TU2", "2"], ["TU2", "3"], ["TC3", "1"], ["TC5", "1"], ["TC6", "1"]]},
  {name: "Tpoe.poe.neg", pads: [["TU1", "4"], ["TU1", "9"], ["TR3", "1"], ["TC2", "2"], ["TD1", "2"], ["TJP2", "2"]]},
  {name: "Tpoe.cdb", pads: [["TU1", "6"]]},
  {name: "Tpoe.t2p", pads: [["TU1", "7"]]},
  {name: "Tpoe.ic.den", pads: [["TU1", "2"], ["TR4", "2"]]},
  {name: "Tpoe.ic.cls", pads: [["TU1", "3"], ["TR3", "2"]]},
  {name: "Treg_poe.pg", pads: [["TU2", "6"]]},
  {name: "Treg_poe.ic.sw", pads: [["TU2", "8"], ["TC4", "2"], ["TL1", "1"]]},
  {name: "Treg_poe.ic.fb", pads: [["TU2", "5"], ["TR5", "2"], ["TR6", "1"]]},
  {name: "Treg_poe.ic.boot", pads: [["TU2", "7"], ["TC4", "1"]]},
  {name: "Treg_poe.ic.rt", pads: [["TU2", "4"], ["TR7", "2"]]},
  {name: "Treg_3v3.ic.sw", pads: [["TU3", "2"], ["TC9", "2"], ["TL2", "1"]]},
  {name: "Treg_3v3.ic.fb", pads: [["TU3", "4"], ["TR8", "2"], ["TR9", "1"]]},
  {name: "Treg_3v3.ic.boot", pads: [["TU3", "6"], ["TC9", "1"]]},
  {name: "Treg_3v3.ic.en", pads: [["TU3", "5"], ["TR10", "2"]]},
  {name: "Tmcu.program_uart_node.a_tx", pads: [["TJ3", "4"], ["TU7", "36"]]},
  {name: "Tmcu.program_uart_node.b_tx", pads: [["TJ3", "3"], ["TU7", "37"]]},
  {name: "Tmcu.program_en_node", pads: [["TJ3", "6"], ["TU7", "3"], ["TR11", "2"], ["TC20", "1"]]},
  {name: "Tmcu.program_boot_node", pads: [["TJ3", "2"], ["TU7", "27"], ["TD4", "2"]]},
  {name: "Tledr.package.k", pads: [["TD4", "1"], ["TR12", "1"]]},
  {name: "Tphy.reset", pads: [["TU8", "37"]]},
  {name: "Tphy.spi.sck", pads: [["TU7", "9"], ["TU8", "33"]]},
  {name: "Tphy.spi.mosi", pads: [["TU7", "8"], ["TU8", "35"]]},
  {name: "Tphy.spi.miso", pads: [["TU7", "7"], ["TU8", "34"]]},
  {name: "Tphy.cs", pads: [["TU7", "35"], ["TU8", "32"]]},
  {name: "Tphy.int", pads: [["TU7", "31"], ["TU8", "36"], ["TU11", "5"]]},
  {name: "Tphy.ic.avdd", pads: [["TU8", "11"], ["TU8", "15"], ["TU8", "17"], ["TU8", "21"], ["TU8", "4"], ["TU8", "8"], ["TFB2", "2"], ["TC27", "1"], ["TC28", "1"], ["TC29", "1"], ["TC30", "1"], ["TC31", "1"], ["TC32", "1"], ["TC33", "1"], ["TR18", "1"], ["TR19", "1"], ["TR20", "1"]]},
  {name: "Tphy.ic.v1v20", pads: [["TU8", "22"], ["TC23", "1"]]},
  {name: "Tphy.ic.tocap", pads: [["TU8", "20"], ["TC24", "1"]]},
  {name: "Tphy.ic.exres1", pads: [["TU8", "10"], ["TR13", "2"]]},
  {name: "Tphy.ic.crystal.xtal_in", pads: [["TU8", "30"], ["TX1", "1"], ["TC21", "1"]]},
  {name: "Tphy.ic.crystal.xtal_out", pads: [["TU8", "31"], ["TX1", "3"], ["TC22", "1"]]},
  {name: "Tphy.ic.txp", pads: [["TU8", "2"], ["TR14", "1"]]},
  {name: "Tphy.ic.txn", pads: [["TU8", "1"], ["TR15", "1"]]},
  {name: "Tphy.ic.rxp", pads: [["TU8", "6"], ["TR16", "1"]]},
  {name: "Tphy.ic.rxn", pads: [["TU8", "5"], ["TR17", "1"]]},
  {name: "Tphy.rxp_damp.b", pads: [["TR16", "2"], ["TC35", "2"], ["TR21", "1"]]},
  {name: "Tphy.rxn_damp.b", pads: [["TR17", "2"], ["TC36", "2"], ["TR22", "1"]]},
  {name: "Tdist.ic.i2c_rst", pads: [["TU10", "A1"], ["TR27", "2"]]},
  {name: "Tdist.ic.int", pads: [["TU10", "A3"], ["TR28", "2"]]},
  {name: "Tdist.ic.lpn", pads: [["TU10", "A5"], ["TR25", "2"]]},
  {name: "Tdist.ic.rsvd6", pads: [["TU10", "C2"], ["TR26", "2"]]},
  {name: "Tpd.ic.vconn", pads: [["TU11", "12"], ["TU11", "13"]]},
  {name: "Tioe.ic.nrst", pads: [["TU12", "4"], ["TJ4", "3"], ["TC43", "1"]]},
  {name: "Tioe.ic.osc.xtal_in", pads: [["TU12", "5"]]},
  {name: "Tioe.ic.osc.xtal_out", pads: [["TU12", "6"]]},
  {name: "Tioe.ic.swio", pads: [["TU12", "18"], ["TJ4", "2"]]},
  {name: "Tpoe_sense.output", pads: [["TU12", "14"], ["TR29", "2"], ["TR30", "1"]]},
  {name: "Tcam.dvp8.xclk", pads: [["TU7", "21"], ["TJ5", "13"]]},
  {name: "Tcam.dvp8.pclk", pads: [["TU7", "19"], ["TJ5", "17"], ["TC46", "1"]]},
  {name: "Tcam.dvp8.href", pads: [["TU7", "23"], ["TJ5", "9"]]},
  {name: "Tcam.dvp8.vsync", pads: [["TU7", "24"], ["TJ5", "7"]]},
  {name: "Tcam.dvp8.y0", pads: [["TU7", "18"], ["TJ5", "19"]]},
  {name: "Tcam.dvp8.y1", pads: [["TU7", "17"], ["TJ5", "21"]]},
  {name: "Tcam.dvp8.y2", pads: [["TU7", "12"], ["TJ5", "22"]]},
  {name: "Tcam.dvp8.y3", pads: [["TU7", "11"], ["TJ5", "20"]]},
  {name: "Tcam.dvp8.y4", pads: [["TU7", "10"], ["TJ5", "18"]]},
  {name: "Tcam.dvp8.y5", pads: [["TU7", "15"], ["TJ5", "16"]]},
  {name: "Tcam.dvp8.y6", pads: [["TU7", "20"], ["TJ5", "14"]]},
  {name: "Tcam.dvp8.y7", pads: [["TU7", "22"], ["TJ5", "12"]]},
  {name: "Tcam.reset", pads: [["TU7", "25"], ["TJ5", "6"], ["TC45", "1"], ["TU13", "24"]]},
  {name: "Tcam.device.y.0", pads: [["TJ5", "24"]]},
  {name: "Tcam.device.y.1", pads: [["TJ5", "23"]]},
  {name: "Tflir.shutdown", pads: [["TU7", "34"], ["TU13", "23"]]},
  {name: "Tflir.spi.sck", pads: [["TU7", "39"], ["TU13", "13"]]},
  {name: "Tflir.spi.mosi", pads: [["TU7", "5"], ["TU13", "11"]]},
  {name: "Tflir.spi.miso", pads: [["TU7", "4"], ["TU13", "12"]]},
  {name: "Tflir.cs", pads: [["TU7", "38"], ["TU13", "14"]]},
  {name: "Tflir.vsync", pads: [["TU7", "6"], ["TU13", "2"]]},
  {name: "Tflir.ic.master_clk", pads: [["TU13", "26"], ["TX2", "3"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.0023622047244105, 3.4519685039370085);
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


