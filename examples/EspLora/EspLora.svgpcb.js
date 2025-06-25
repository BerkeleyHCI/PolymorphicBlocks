const board = new PCB();

// jlc_th.th1
const LH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.100, 2.597), rotate: 0,
  id: 'LH1'
})
// jlc_th.th2
const LH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.140, 2.597), rotate: 0,
  id: 'LH2'
})
// jlc_th.th3
const LH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.100, 2.636), rotate: 0,
  id: 'LH3'
})
// usb.conn
const LJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(2.899, 1.905), rotate: 0,
  id: 'LJ1'
})
// usb.cc_pull.cc1.res
const LR1 = board.add(R_0603_1608Metric, {
  translate: pt(2.748, 2.160), rotate: 0,
  id: 'LR1'
})
// usb.cc_pull.cc2.res
const LR2 = board.add(R_0603_1608Metric, {
  translate: pt(2.904, 2.160), rotate: 0,
  id: 'LR2'
})
// tp_gnd.tp
const LTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.525, 2.634), rotate: 0,
  id: 'LTP1'
})
// choke.fb
const LFB1 = board.add(L_0603_1608Metric, {
  translate: pt(3.264, 2.626), rotate: 0,
  id: 'LFB1'
})
// tp_pwr.tp
const LTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.026, 2.634), rotate: 0,
  id: 'LTP2'
})
// reg_3v3.ic
const LU1 = board.add(SOT_223_3_TabPin2, {
  translate: pt(3.400, 1.882), rotate: 0,
  id: 'LU1'
})
// reg_3v3.in_cap.cap
const LC1 = board.add(C_0603_1608Metric, {
  translate: pt(3.458, 2.092), rotate: 0,
  id: 'LC1'
})
// reg_3v3.out_cap.cap
const LC2 = board.add(C_0805_2012Metric, {
  translate: pt(3.294, 2.102), rotate: 0,
  id: 'LC2'
})
// tp_3v3.tp
const LTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.276, 2.634), rotate: 0,
  id: 'LTP3'
})
// prot_3v3.diode
const LD1 = board.add(D_SOD_323, {
  translate: pt(2.524, 2.634), rotate: 0,
  id: 'LD1'
})
// mcu.ic
const LU2 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'LU2'
})
// mcu.vcc_cap0.cap
const LC3 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.683), rotate: 0,
  id: 'LC3'
})
// mcu.vcc_cap1.cap
const LC4 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.667), rotate: 0,
  id: 'LC4'
})
// mcu.prog.conn
const LJ2 = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(2.096, 0.167), rotate: 0,
  id: 'LJ2'
})
// mcu.boot.package
const LSW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.096, 0.486), rotate: 0,
  id: 'LSW1'
})
// mcu.en_pull.rc.r
const LR3 = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.667), rotate: 0,
  id: 'LR3'
})
// mcu.en_pull.rc.c
const LC5 = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.796), rotate: 0,
  id: 'LC5'
})
// usb_esd
const LU3 = board.add(SOT_23, {
  translate: pt(3.985, 2.664), rotate: 0,
  id: 'LU3'
})
// ledr.package
const LD2 = board.add(LED_0603_1608Metric, {
  translate: pt(0.528, 2.626), rotate: 0,
  id: 'LD2'
})
// ledr.res
const LR4 = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 2.723), rotate: 0,
  id: 'LR4'
})
// ledg.package
const LD3 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 2.626), rotate: 0,
  id: 'LD3'
})
// ledg.res
const LR5 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.723), rotate: 0,
  id: 'LR5'
})
// ledb.package
const LD4 = board.add(LED_0603_1608Metric, {
  translate: pt(0.293, 2.626), rotate: 0,
  id: 'LD4'
})
// ledb.res
const LR6 = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 2.723), rotate: 0,
  id: 'LR6'
})
// lora.ic
const LU4 = board.add(QFN_24_1EP_4x4mm_P0_5mm_EP2_6x2_6mm, {
  translate: pt(0.480, 1.843), rotate: 0,
  id: 'LU4'
})
// lora.xtal
const LX1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(0.705, 1.807), rotate: 0,
  id: 'LX1'
})
// lora.vreg_cap.cap
const LC6 = board.add(C_0603_1608Metric, {
  translate: pt(0.436, 2.013), rotate: 0,
  id: 'LC6'
})
// lora.vbat_cap.cap
const LC7 = board.add(C_0603_1608Metric, {
  translate: pt(0.592, 2.013), rotate: 0,
  id: 'LC7'
})
// lora.vdd_cap.cap
const LC8 = board.add(C_0603_1608Metric, {
  translate: pt(0.748, 2.013), rotate: 0,
  id: 'LC8'
})
// lora.vrpa_cap0.cap
const LC9 = board.add(C_0603_1608Metric, {
  translate: pt(0.904, 2.013), rotate: 0,
  id: 'LC9'
})
// lora.vrpa_cap1.cap
const LC10 = board.add(C_0603_1608Metric, {
  translate: pt(0.436, 2.110), rotate: 0,
  id: 'LC10'
})
// lora.dcc_l
const LL1 = board.add(L_0603_1608Metric, {
  translate: pt(0.592, 2.110), rotate: 0,
  id: 'LL1'
})
// lora.rf_sw.ic
const LU5 = board.add(SOT_363_SC_70_6, {
  translate: pt(0.890, 1.795), rotate: 0,
  id: 'LU5'
})
// lora.rf_sw.vdd_res
const LR7 = board.add(R_0603_1608Metric, {
  translate: pt(0.748, 2.110), rotate: 0,
  id: 'LR7'
})
// lora.rf_sw.ctrl_res
const LR8 = board.add(R_0603_1608Metric, {
  translate: pt(0.904, 2.110), rotate: 0,
  id: 'LR8'
})
// lora.tx_dcblock
const LC11 = board.add(C_0603_1608Metric, {
  translate: pt(0.436, 2.207), rotate: 0,
  id: 'LC11'
})
// lora.rfc_dcblock
const LC12 = board.add(C_0603_1608Metric, {
  translate: pt(0.592, 2.207), rotate: 0,
  id: 'LC12'
})
// lora.vrpa_choke
const LL2 = board.add(L_0603_1608Metric, {
  translate: pt(0.748, 2.207), rotate: 0,
  id: 'LL2'
})
// lora.tx_l.l
const LL3 = board.add(L_0603_1608Metric, {
  translate: pt(0.904, 2.207), rotate: 0,
  id: 'LL3'
})
// lora.tx_l.c_lc
const LC13 = board.add(C_0603_1608Metric, {
  translate: pt(0.436, 2.304), rotate: 0,
  id: 'LC13'
})
// lora.tx_pi.c2
const LC14 = board.add(C_0603_1608Metric, {
  translate: pt(0.592, 2.304), rotate: 0,
  id: 'LC14'
})
// lora.tx_pi.l
const LL4 = board.add(L_0603_1608Metric, {
  translate: pt(0.748, 2.304), rotate: 0,
  id: 'LL4'
})
// lora.balun.l
const LL5 = board.add(L_0603_1608Metric, {
  translate: pt(0.904, 2.304), rotate: 0,
  id: 'LL5'
})
// lora.balun.c
const LC15 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.450), rotate: 0,
  id: 'LC15'
})
// lora.balun.c_p
const LC16 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 2.450), rotate: 0,
  id: 'LC16'
})
// lora.ant_pi.c1
const LC17 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 2.450), rotate: 0,
  id: 'LC17'
})
// lora.ant_pi.c2
const LC18 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 2.450), rotate: 0,
  id: 'LC18'
})
// lora.ant_pi.l
const LL6 = board.add(L_0603_1608Metric, {
  translate: pt(0.682, 2.450), rotate: 0,
  id: 'LL6'
})
// lora.ant.conn
const LJ3 = board.add(SMA_Amphenol_901_143_Horizontal, {
  translate: pt(0.169, 1.909), rotate: 0,
  id: 'LJ3'
})
// tp_lora_spi.tp_sck.tp
const LTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.757, 1.778), rotate: 0,
  id: 'LTP4'
})
// tp_lora_spi.tp_mosi.tp
const LTP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.757, 1.892), rotate: 0,
  id: 'LTP5'
})
// tp_lora_spi.tp_miso.tp
const LTP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.757, 2.006), rotate: 0,
  id: 'LTP6'
})
// tp_lora_cs.tp
const LTP7 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.021, 2.634), rotate: 0,
  id: 'LTP7'
})
// tp_lora_rst.tp
const LTP8 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.771, 2.634), rotate: 0,
  id: 'LTP8'
})
// tp_lora_dio.tp
const LTP9 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.775, 2.634), rotate: 0,
  id: 'LTP9'
})
// tp_lora_busy.tp
const LTP10 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.275, 2.634), rotate: 0,
  id: 'LTP10'
})
// i2c_pull.scl_res.res
const LR9 = board.add(R_0603_1608Metric, {
  translate: pt(0.763, 2.626), rotate: 0,
  id: 'LR9'
})
// i2c_pull.sda_res.res
const LR10 = board.add(R_0603_1608Metric, {
  translate: pt(0.763, 2.722), rotate: 0,
  id: 'LR10'
})
// i2c_tp.tp_scl.tp
const LTP11 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.008, 1.778), rotate: 0,
  id: 'LTP11'
})
// i2c_tp.tp_sda.tp
const LTP12 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.008, 1.892), rotate: 0,
  id: 'LTP12'
})
// oled.device.conn
const LJ4 = board.add(Hirose_FH12_30S_0_5SH_1x30_1MP_P0_50mm_Horizontal, {
  translate: pt(2.956, 1.054), rotate: 0,
  id: 'LJ4'
})
// oled.lcd
const LU6 = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(3.066, 0.516), rotate: 0,
  id: 'LU6'
})
// oled.c1_cap
const LC19 = board.add(C_0603_1608Metric, {
  translate: pt(3.815, 0.889), rotate: 0,
  id: 'LC19'
})
// oled.c2_cap
const LC20 = board.add(C_0603_1608Metric, {
  translate: pt(3.971, 0.889), rotate: 0,
  id: 'LC20'
})
// oled.iref_res
const LR11 = board.add(R_0603_1608Metric, {
  translate: pt(3.469, 1.006), rotate: 0,
  id: 'LR11'
})
// oled.vcomh_cap.cap
const LC21 = board.add(C_0805_2012Metric, {
  translate: pt(3.477, 0.899), rotate: 0,
  id: 'LC21'
})
// oled.vdd_cap1.cap
const LC22 = board.add(C_0603_1608Metric, {
  translate: pt(3.624, 1.006), rotate: 0,
  id: 'LC22'
})
// oled.vbat_cap.cap
const LC23 = board.add(C_0603_1608Metric, {
  translate: pt(3.780, 1.006), rotate: 0,
  id: 'LC23'
})
// oled.vcc_cap.cap
const LC24 = board.add(C_0805_2012Metric, {
  translate: pt(3.650, 0.899), rotate: 0,
  id: 'LC24'
})
// oled_rst.ic
const LU7 = board.add(SOT_23, {
  translate: pt(1.015, 2.664), rotate: 0,
  id: 'LU7'
})
// oled_pull.res
const LR12 = board.add(R_0603_1608Metric, {
  translate: pt(3.733, 2.626), rotate: 0,
  id: 'LR12'
})
// sd
const LJ5 = board.add(microSD_HC_Molex_104031_0811, {
  translate: pt(2.381, 1.998), rotate: 0,
  id: 'LJ5'
})
// nfc.ic
const LU8 = board.add(HVQFN_40_1EP_6x6mm_P0_5mm_EP4_1x4_1mm, {
  translate: pt(1.223, 1.883), rotate: 0,
  id: 'LU8'
})
// nfc.cvddup.cap
const LC25 = board.add(C_0805_2012Metric, {
  translate: pt(1.677, 1.779), rotate: 0,
  id: 'LC25'
})
// nfc.cvbat.cap
const LC26 = board.add(C_0805_2012Metric, {
  translate: pt(1.850, 1.779), rotate: 0,
  id: 'LC26'
})
// nfc.cvbat1.cap
const LC27 = board.add(C_0603_1608Metric, {
  translate: pt(1.312, 2.094), rotate: 0,
  id: 'LC27'
})
// nfc.cvdd1.cap
const LC28 = board.add(C_0805_2012Metric, {
  translate: pt(1.472, 1.952), rotate: 0,
  id: 'LC28'
})
// nfc.cvdd2.cap
const LC29 = board.add(C_0805_2012Metric, {
  translate: pt(1.646, 1.952), rotate: 0,
  id: 'LC29'
})
// nfc.ctvdd1.cap
const LC30 = board.add(C_0805_2012Metric, {
  translate: pt(1.819, 1.952), rotate: 0,
  id: 'LC30'
})
// nfc.ctvdd2.cap
const LC31 = board.add(C_0805_2012Metric, {
  translate: pt(1.147, 2.104), rotate: 0,
  id: 'LC31'
})
// nfc.cvddpad.cap
const LC32 = board.add(C_0603_1608Metric, {
  translate: pt(1.468, 2.094), rotate: 0,
  id: 'LC32'
})
// nfc.cvddmid.cap
const LC33 = board.add(C_0603_1608Metric, {
  translate: pt(1.624, 2.094), rotate: 0,
  id: 'LC33'
})
// nfc.xtal.package
const LX2 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(1.488, 1.807), rotate: 0,
  id: 'LX2'
})
// nfc.xtal.cap_a
const LC34 = board.add(C_0603_1608Metric, {
  translate: pt(1.780, 2.094), rotate: 0,
  id: 'LC34'
})
// nfc.xtal.cap_b
const LC35 = board.add(C_0603_1608Metric, {
  translate: pt(1.935, 2.094), rotate: 0,
  id: 'LC35'
})
// nfc.rx.rrx1
const LR13 = board.add(R_0603_1608Metric, {
  translate: pt(1.139, 2.211), rotate: 0,
  id: 'LR13'
})
// nfc.rx.rrx2
const LR14 = board.add(R_0603_1608Metric, {
  translate: pt(1.294, 2.211), rotate: 0,
  id: 'LR14'
})
// nfc.rx.crx1
const LC36 = board.add(C_0603_1608Metric, {
  translate: pt(1.450, 2.211), rotate: 0,
  id: 'LC36'
})
// nfc.rx.crx2
const LC37 = board.add(C_0603_1608Metric, {
  translate: pt(1.606, 2.211), rotate: 0,
  id: 'LC37'
})
// nfc.emc.l1
const LL7 = board.add(L_0603_1608Metric, {
  translate: pt(1.762, 2.211), rotate: 0,
  id: 'LL7'
})
// nfc.emc.l2
const LL8 = board.add(L_0603_1608Metric, {
  translate: pt(1.918, 2.211), rotate: 0,
  id: 'LL8'
})
// nfc.emc.c1
const LC38 = board.add(C_0603_1608Metric, {
  translate: pt(1.139, 2.307), rotate: 0,
  id: 'LC38'
})
// nfc.emc.c2
const LC39 = board.add(C_0603_1608Metric, {
  translate: pt(1.294, 2.307), rotate: 0,
  id: 'LC39'
})
// nfc.ant
const LANT1 = board.add(an13219, {
  translate: pt(1.392, 2.376), rotate: 0,
  id: 'LANT1'
})
// nfc.damp.r1
const LR15 = board.add(R_0603_1608Metric, {
  translate: pt(1.450, 2.307), rotate: 0,
  id: 'LR15'
})
// nfc.damp.r2
const LR16 = board.add(R_0603_1608Metric, {
  translate: pt(1.606, 2.307), rotate: 0,
  id: 'LR16'
})
// nfc.match.cs1
const LC40 = board.add(C_0603_1608Metric, {
  translate: pt(1.762, 2.307), rotate: 0,
  id: 'LC40'
})
// nfc.match.cs2
const LC41 = board.add(C_0603_1608Metric, {
  translate: pt(1.918, 2.307), rotate: 0,
  id: 'LC41'
})
// nfc.match.cp1
const LC42 = board.add(C_0603_1608Metric, {
  translate: pt(1.139, 2.404), rotate: 0,
  id: 'LC42'
})
// nfc.match.cp2
const LC43 = board.add(C_0603_1608Metric, {
  translate: pt(1.294, 2.404), rotate: 0,
  id: 'LC43'
})
// tx_cpack.cap
const LC44 = board.add(C_0603_1608Metric, {
  translate: pt(3.499, 2.626), rotate: 0,
  id: 'LC44'
})

board.setNetlist([
  {name: "Lgnd", pads: [["LU3", "3"], ["LJ5", "6"], ["LJ5", "11"], ["LU7", "1"], ["LJ1", "A1"], ["LJ1", "B12"], ["LJ1", "B1"], ["LJ1", "A12"], ["LTP1", "1"], ["LU1", "1"], ["LD1", "2"], ["LU2", "1"], ["LU2", "40"], ["LU2", "41"], ["LR4", "2"], ["LR5", "2"], ["LR6", "2"], ["LU4", "2"], ["LU4", "5"], ["LU4", "8"], ["LU4", "20"], ["LU4", "25"], ["LX1", "2"], ["LX1", "4"], ["LU8", "1"], ["LU8", "3"], ["LU8", "4"], ["LU8", "9"], ["LU8", "20"], ["LU8", "41"], ["LU5", "2"], ["LJ3", "2"], ["LJ1", "S1"], ["LR11", "2"], ["LC1", "2"], ["LC2", "2"], ["LC3", "2"], ["LC4", "2"], ["LJ2", "5"], ["LSW1", "2"], ["LC6", "2"], ["LC7", "2"], ["LC8", "2"], ["LC9", "2"], ["LC10", "2"], ["LC16", "2"], ["LC21", "2"], ["LC22", "2"], ["LC23", "2"], ["LC24", "2"], ["LC25", "2"], ["LC26", "2"], ["LC27", "2"], ["LC28", "2"], ["LC29", "2"], ["LC30", "2"], ["LC31", "2"], ["LC32", "2"], ["LC33", "2"], ["LX2", "2"], ["LX2", "4"], ["LC5", "2"], ["LR1", "1"], ["LR2", "1"], ["LC14", "2"], ["LC17", "2"], ["LC18", "2"], ["LJ4", "8"], ["LJ4", "1"], ["LJ4", "30"], ["LJ4", "29"], ["LJ4", "17"], ["LJ4", "16"], ["LJ4", "21"], ["LJ4", "22"], ["LJ4", "23"], ["LJ4", "24"], ["LJ4", "25"], ["LJ4", "12"], ["LJ4", "10"], ["LJ4", "15"], ["LJ4", "13"], ["LC34", "2"], ["LC35", "2"], ["LC38", "2"], ["LC39", "2"], ["LC42", "2"], ["LC43", "2"], ["LC44", "2"]]},
  {name: "Lpwr", pads: [["LFB1", "2"], ["LTP2", "1"], ["LU1", "3"], ["LU8", "12"], ["LU8", "28"], ["LU8", "13"], ["LC1", "1"], ["LC25", "1"], ["LC26", "1"], ["LC27", "1"]]},
  {name: "Lv3v3", pads: [["LJ5", "4"], ["LU7", "3"], ["LU1", "2"], ["LTP3", "1"], ["LD1", "1"], ["LU2", "2"], ["LU4", "1"], ["LU4", "10"], ["LU4", "11"], ["LR12", "1"], ["LU8", "6"], ["LC2", "1"], ["LC3", "1"], ["LC4", "1"], ["LJ2", "1"], ["LC7", "1"], ["LC8", "1"], ["LR7", "1"], ["LR9", "1"], ["LR10", "1"], ["LJ4", "9"], ["LJ4", "6"], ["LC22", "1"], ["LC23", "1"], ["LC32", "1"], ["LR3", "1"], ["LJ4", "11"]]},
  {name: "Lusb.pwr", pads: [["LJ1", "A4"], ["LJ1", "B9"], ["LJ1", "B4"], ["LJ1", "A9"], ["LFB1", "1"]]},
  {name: "Lusb_chain_0.d_P", pads: [["LJ1", "A6"], ["LJ1", "B6"], ["LU3", "2"], ["LU2", "14"]]},
  {name: "Lusb_chain_0.d_N", pads: [["LJ1", "A7"], ["LJ1", "B7"], ["LU3", "1"], ["LU2", "13"]]},
  {name: "Lledr.signal", pads: [["LU2", "34"], ["LD2", "2"]]},
  {name: "Lledg.signal", pads: [["LU2", "35"], ["LD3", "2"]]},
  {name: "Lledb.signal", pads: [["LU2", "39"], ["LD4", "2"]]},
  {name: "Ltp_lora_spi.io.sck", pads: [["LU2", "5"], ["LU4", "18"], ["LTP4", "1"]]},
  {name: "Ltp_lora_spi.io.mosi", pads: [["LU2", "6"], ["LU4", "17"], ["LTP5", "1"]]},
  {name: "Ltp_lora_spi.io.miso", pads: [["LU2", "15"], ["LU4", "16"], ["LTP6", "1"]]},
  {name: "Ltp_lora_cs.io", pads: [["LU2", "7"], ["LU4", "19"], ["LTP7", "1"]]},
  {name: "Ltp_lora_rst.io", pads: [["LU2", "12"], ["LU4", "15"], ["LTP8", "1"]]},
  {name: "Ltp_lora_dio.io", pads: [["LU2", "31"], ["LU4", "13"], ["LTP9", "1"]]},
  {name: "Llora.busy", pads: [["LU2", "33"], ["LU4", "14"], ["LTP10", "1"]]},
  {name: "Li2c_pull.i2c.scl", pads: [["LU2", "10"], ["LU8", "7"], ["LR9", "2"], ["LTP11", "1"], ["LJ4", "18"]]},
  {name: "Li2c_pull.i2c.sda", pads: [["LU2", "11"], ["LU8", "5"], ["LR10", "2"], ["LTP12", "1"], ["LJ4", "19"], ["LJ4", "20"]]},
  {name: "Loled_rst.nreset", pads: [["LU7", "2"], ["LR12", "2"], ["LJ4", "14"]]},
  {name: "Lsd.spi.sck", pads: [["LU2", "22"], ["LJ5", "5"]]},
  {name: "Lsd.spi.mosi", pads: [["LU2", "19"], ["LJ5", "3"]]},
  {name: "Lsd.spi.miso", pads: [["LU2", "38"], ["LJ5", "7"]]},
  {name: "Lsd.cs", pads: [["LU2", "21"], ["LJ5", "2"]]},
  {name: "Lnfc.reset", pads: [["LU8", "10"], ["LU2", "32"]]},
  {name: "Lnfc.irq", pads: [["LU8", "8"], ["LU2", "24"]]},
  {name: "Ltx_cpack.pos.0", pads: [["LL3", "2"], ["LC13", "1"], ["LC44", "1"], ["LL4", "1"]]},
  {name: "Lusb.conn.cc.cc1", pads: [["LJ1", "A5"], ["LR1", "2"]]},
  {name: "Lusb.conn.cc.cc2", pads: [["LJ1", "B5"], ["LR2", "2"]]},
  {name: "Lmcu.program_uart_node.a_tx", pads: [["LU2", "37"], ["LJ2", "3"]]},
  {name: "Lmcu.program_uart_node.b_tx", pads: [["LU2", "36"], ["LJ2", "4"]]},
  {name: "Lmcu.program_en_node", pads: [["LU2", "3"], ["LJ2", "6"], ["LR3", "2"], ["LC5", "1"]]},
  {name: "Lmcu.program_boot_node", pads: [["LU2", "27"], ["LSW1", "1"], ["LJ2", "2"]]},
  {name: "Lledr.res.a", pads: [["LR4", "1"], ["LD2", "1"]]},
  {name: "Lledg.res.a", pads: [["LR5", "1"], ["LD3", "1"]]},
  {name: "Lledb.res.a", pads: [["LR6", "1"], ["LD4", "1"]]},
  {name: "Llora.xtal.crystal.xtal_in", pads: [["LX1", "1"], ["LU4", "3"]]},
  {name: "Llora.xtal.crystal.xtal_out", pads: [["LX1", "3"], ["LU4", "4"]]},
  {name: "Llora.ic.vreg", pads: [["LU4", "7"], ["LL1", "2"], ["LC6", "1"]]},
  {name: "Llora.ic.vr_pa", pads: [["LU4", "24"], ["LL2", "1"], ["LC9", "1"], ["LC10", "1"]]},
  {name: "Llora.dcc_l.a", pads: [["LL1", "1"], ["LU4", "9"]]},
  {name: "Llora.rf_sw.ctrl", pads: [["LU4", "12"], ["LR8", "1"]]},
  {name: "Llora.tx_dcblock.pos", pads: [["LC11", "1"], ["LU5", "1"]]},
  {name: "Llora.rfc_dcblock.neg", pads: [["LC12", "2"], ["LU5", "5"]]},
  {name: "Llora.ic.rfo", pads: [["LU4", "23"], ["LL2", "2"], ["LL3", "1"], ["LC13", "2"]]},
  {name: "Llora.tx_pi.output", pads: [["LC11", "2"], ["LL4", "2"], ["LC14", "1"]]},
  {name: "Llora.balun.input", pads: [["LC15", "1"], ["LU5", "3"]]},
  {name: "Llora.balun.rfi_n", pads: [["LU4", "22"], ["LC15", "2"], ["LL5", "1"]]},
  {name: "Llora.balun.rfi_p", pads: [["LU4", "21"], ["LC16", "1"], ["LL5", "2"]]},
  {name: "Llora.rfc_dcblock.pos", pads: [["LC12", "1"], ["LC17", "1"], ["LL6", "1"]]},
  {name: "Llora.ant_pi.output", pads: [["LJ3", "1"], ["LL6", "2"], ["LC18", "1"]]},
  {name: "Llora.ic.dio3", pads: [["LU4", "6"]]},
  {name: "Llora.rf_sw.vdd_res.b", pads: [["LR7", "2"], ["LU5", "6"]]},
  {name: "Llora.rf_sw.ctrl_res.b", pads: [["LR8", "2"], ["LU5", "4"]]},
  {name: "Loled.c1_cap.pos", pads: [["LC19", "1"], ["LJ4", "4"]]},
  {name: "Loled.c1_cap.neg", pads: [["LC19", "2"], ["LJ4", "5"]]},
  {name: "Loled.c2_cap.pos", pads: [["LC20", "1"], ["LJ4", "2"]]},
  {name: "Loled.c2_cap.neg", pads: [["LC20", "2"], ["LJ4", "3"]]},
  {name: "Loled.iref_res.a", pads: [["LR11", "1"], ["LJ4", "26"]]},
  {name: "Loled.device.vcomh", pads: [["LJ4", "27"], ["LC21", "1"]]},
  {name: "Loled.device.vcc", pads: [["LJ4", "28"], ["LC24", "1"]]},
  {name: "Lnfc.ic.vdd", pads: [["LU8", "26"], ["LU8", "27"], ["LU8", "31"], ["LC28", "1"], ["LC29", "1"]]},
  {name: "Lnfc.ic.vddtx", pads: [["LU8", "14"], ["LU8", "18"], ["LU8", "22"], ["LC30", "1"], ["LC31", "1"]]},
  {name: "Lnfc.ic.vddmid", pads: [["LU8", "17"], ["LC33", "1"]]},
  {name: "Lnfc.ic.xtal.xtal_in", pads: [["LU8", "30"], ["LX2", "1"], ["LC34", "1"]]},
  {name: "Lnfc.ic.xtal.xtal_out", pads: [["LU8", "29"], ["LX2", "3"], ["LC35", "1"]]},
  {name: "Lnfc.ic.rxp", pads: [["LU8", "16"], ["LC36", "2"]]},
  {name: "Lnfc.ic.rxn", pads: [["LU8", "15"], ["LC37", "2"]]},
  {name: "Lnfc.ic.tx1", pads: [["LU8", "21"], ["LL7", "1"]]},
  {name: "Lnfc.ic.tx2", pads: [["LU8", "19"], ["LL8", "1"]]},
  {name: "Lnfc.damp.ant1", pads: [["LR15", "2"], ["LANT1", "1"]]},
  {name: "Lnfc.damp.ant2", pads: [["LR16", "2"], ["LANT1", "2"]]},
  {name: "Lnfc.emc.out1", pads: [["LC40", "1"], ["LR13", "1"], ["LL7", "2"], ["LC38", "1"]]},
  {name: "Lnfc.emc.out2", pads: [["LC41", "1"], ["LR14", "1"], ["LL8", "2"], ["LC39", "1"]]},
  {name: "Lnfc.match.out1", pads: [["LR15", "1"], ["LC40", "2"], ["LC42", "1"]]},
  {name: "Lnfc.match.out2", pads: [["LR16", "1"], ["LC41", "2"], ["LC43", "1"]]},
  {name: "Lnfc.rx.rrx1.b", pads: [["LR13", "2"], ["LC36", "1"]]},
  {name: "Lnfc.rx.rrx2.b", pads: [["LR14", "2"], ["LC37", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.25767716535433, 2.8696850393700797);
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


