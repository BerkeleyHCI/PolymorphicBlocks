const board = new PCB();

// jlc_th.th1
const CH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.246, 2.093), rotate: 0,
  id: 'CH1'
})
// jlc_th.th2
const CH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.285, 2.093), rotate: 0,
  id: 'CH2'
})
// jlc_th.th3
const CH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.246, 2.132), rotate: 0,
  id: 'CH3'
})
// pwr_conn.conn
const CJ1 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.767, 1.870), rotate: 0,
  id: 'CJ1'
})
// tp_pwr.tp
const CTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.816, 2.130), rotate: 0,
  id: 'CTP1'
})
// tp_gnd.tp
const CTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.066, 2.130), rotate: 0,
  id: 'CTP2'
})
// reg_3v3.ic
const CU1 = board.add(SOT_223_3_TabPin2, {
  translate: pt(2.713, 1.244), rotate: 0,
  id: 'CU1'
})
// reg_3v3.in_cap.cap
const CC1 = board.add(C_0603_1608Metric, {
  translate: pt(2.772, 1.454), rotate: 0,
  id: 'CC1'
})
// reg_3v3.out_cap.cap
const CC2 = board.add(C_0805_2012Metric, {
  translate: pt(2.607, 1.464), rotate: 0,
  id: 'CC2'
})
// tp_3v3.tp
const CTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.316, 2.130), rotate: 0,
  id: 'CTP3'
})
// prot_3v3.diode
const CD1 = board.add(D_SOD_323, {
  translate: pt(2.564, 2.130), rotate: 0,
  id: 'CD1'
})
// mcu.ic
const CU2 = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'CU2'
})
// mcu.vcc_cap0.cap
const CC3 = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.419), rotate: 0,
  id: 'CC3'
})
// mcu.vcc_cap1.cap
const CC4 = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.403), rotate: 0,
  id: 'CC4'
})
// mcu.prog.conn
const CJ2 = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(2.096, 0.167), rotate: 0,
  id: 'CJ2'
})
// mcu.en_pull.rc.r
const CR1 = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.403), rotate: 0,
  id: 'CR1'
})
// mcu.en_pull.rc.c
const CC5 = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.533), rotate: 0,
  id: 'CC5'
})
// ledr.package
const CD2 = board.add(LED_0603_1608Metric, {
  translate: pt(0.399, 2.122), rotate: 0,
  id: 'CD2'
})
// ledr.res
const CR2 = board.add(R_0603_1608Metric, {
  translate: pt(0.399, 2.219), rotate: 0,
  id: 'CR2'
})
// ledg.package
const CD3 = board.add(LED_0603_1608Metric, {
  translate: pt(0.634, 2.122), rotate: 0,
  id: 'CD3'
})
// ledg.res
const CR3 = board.add(R_0603_1608Metric, {
  translate: pt(0.634, 2.219), rotate: 0,
  id: 'CR3'
})
// ledb.package
const CD4 = board.add(LED_0603_1608Metric, {
  translate: pt(0.869, 2.122), rotate: 0,
  id: 'CD4'
})
// ledb.res
const CR4 = board.add(R_0603_1608Metric, {
  translate: pt(0.869, 2.219), rotate: 0,
  id: 'CR4'
})
// sw[0].package
const CSW1 = board.add(SW_Push_1P1T_MP_NO_Horizontal_Alps_SKRTLAE010, {
  translate: pt(2.617, 1.831), rotate: 0,
  id: 'CSW1'
})
// sw[1].package
const CSW2 = board.add(SW_Push_1P1T_MP_NO_Horizontal_Alps_SKRTLAE010, {
  translate: pt(2.958, 1.831), rotate: 0,
  id: 'CSW2'
})
// sw[2].package
const CSW3 = board.add(SW_Push_1P1T_MP_NO_Horizontal_Alps_SKRTLAE010, {
  translate: pt(3.299, 1.831), rotate: 0,
  id: 'CSW3'
})
// sw[3].package
const CSW4 = board.add(SW_Push_1P1T_MP_NO_Horizontal_Alps_SKRTLAE010, {
  translate: pt(0.111, 2.183), rotate: 0,
  id: 'CSW4'
})
// i2c_pull.scl_res.res
const CR5 = board.add(R_0603_1608Metric, {
  translate: pt(1.104, 2.122), rotate: 0,
  id: 'CR5'
})
// i2c_pull.sda_res.res
const CR6 = board.add(R_0603_1608Metric, {
  translate: pt(1.104, 2.219), rotate: 0,
  id: 'CR6'
})
// i2c_tp.tp_scl.tp
const CTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.909, 1.778), rotate: 0,
  id: 'CTP4'
})
// i2c_tp.tp_sda.tp
const CTP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.909, 1.892), rotate: 0,
  id: 'CTP5'
})
// env.ic
const CU3 = board.add(Bosch_LGA_8_3x3mm_P0_8mm_ClockwisePinNumbering, {
  translate: pt(0.069, 1.809), rotate: 0,
  id: 'CU3'
})
// env.vdd_cap.cap
const CC6 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.946), rotate: 0,
  id: 'CC6'
})
// env.vddio_cap.cap
const CC7 = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.946), rotate: 0,
  id: 'CC7'
})
// als.ic
const CU4 = board.add(HVSOF6, {
  translate: pt(2.163, 1.781), rotate: 0,
  id: 'CU4'
})
// als.vcc_cap.cap
const CC8 = board.add(C_0603_1608Metric, {
  translate: pt(2.329, 1.769), rotate: 0,
  id: 'CC8'
})
// als.dvi_res
const CR7 = board.add(R_0603_1608Metric, {
  translate: pt(2.152, 1.891), rotate: 0,
  id: 'CR7'
})
// als.dvi_cap
const CC9 = board.add(C_0603_1608Metric, {
  translate: pt(2.308, 1.891), rotate: 0,
  id: 'CC9'
})
// rgb_shift.ic
const CU5 = board.add(SOT_23_5, {
  translate: pt(0.471, 1.807), rotate: 0,
  id: 'CU5'
})
// rgb_shift.vdd_cap.cap
const CC10 = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 1.942), rotate: 0,
  id: 'CC10'
})
// rgb_tp.tp
const CTP6 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.811, 2.130), rotate: 0,
  id: 'CTP6'
})
// digit[0].led[0]
const CD5 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.039), rotate: 0,
  id: 'CD5'
})
// digit[0].led[1]
const CD6 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.039), rotate: 0,
  id: 'CD6'
})
// digit[0].led[2]
const CD7 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.039), rotate: 0,
  id: 'CD7'
})
// digit[0].led[3]
const CD8 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.039), rotate: 0,
  id: 'CD8'
})
// digit[0].led[4]
const CD9 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.157), rotate: 0,
  id: 'CD9'
})
// digit[0].led[5]
const CD10 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.157), rotate: 0,
  id: 'CD10'
})
// digit[0].led[6]
const CD11 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.157), rotate: 0,
  id: 'CD11'
})
// digit[0].led[7]
const CD12 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.157), rotate: 0,
  id: 'CD12'
})
// digit[0].led[8]
const CD13 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.276), rotate: 0,
  id: 'CD13'
})
// digit[0].led[9]
const CD14 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.276), rotate: 0,
  id: 'CD14'
})
// digit[0].led[10]
const CD15 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.276), rotate: 0,
  id: 'CD15'
})
// digit[0].led[11]
const CD16 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.276), rotate: 0,
  id: 'CD16'
})
// digit[0].led[12]
const CD17 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.394), rotate: 0,
  id: 'CD17'
})
// digit[0].led[13]
const CD18 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.394), rotate: 0,
  id: 'CD18'
})
// digit[1].led[0]
const CD19 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.039), rotate: 0,
  id: 'CD19'
})
// digit[1].led[1]
const CD20 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.039), rotate: 0,
  id: 'CD20'
})
// digit[1].led[2]
const CD21 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.039), rotate: 0,
  id: 'CD21'
})
// digit[1].led[3]
const CD22 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.039), rotate: 0,
  id: 'CD22'
})
// digit[1].led[4]
const CD23 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.157), rotate: 0,
  id: 'CD23'
})
// digit[1].led[5]
const CD24 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.157), rotate: 0,
  id: 'CD24'
})
// digit[1].led[6]
const CD25 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.157), rotate: 0,
  id: 'CD25'
})
// digit[1].led[7]
const CD26 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.157), rotate: 0,
  id: 'CD26'
})
// digit[1].led[8]
const CD27 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.276), rotate: 0,
  id: 'CD27'
})
// digit[1].led[9]
const CD28 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.276), rotate: 0,
  id: 'CD28'
})
// digit[1].led[10]
const CD29 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.276), rotate: 0,
  id: 'CD29'
})
// digit[1].led[11]
const CD30 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.276), rotate: 0,
  id: 'CD30'
})
// digit[1].led[12]
const CD31 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.394), rotate: 0,
  id: 'CD31'
})
// digit[1].led[13]
const CD32 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.394), rotate: 0,
  id: 'CD32'
})
// digit[2].led[0]
const CD33 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.591), rotate: 0,
  id: 'CD33'
})
// digit[2].led[1]
const CD34 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.591), rotate: 0,
  id: 'CD34'
})
// digit[2].led[2]
const CD35 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.591), rotate: 0,
  id: 'CD35'
})
// digit[2].led[3]
const CD36 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.591), rotate: 0,
  id: 'CD36'
})
// digit[2].led[4]
const CD37 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.709), rotate: 0,
  id: 'CD37'
})
// digit[2].led[5]
const CD38 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.709), rotate: 0,
  id: 'CD38'
})
// digit[2].led[6]
const CD39 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.709), rotate: 0,
  id: 'CD39'
})
// digit[2].led[7]
const CD40 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.709), rotate: 0,
  id: 'CD40'
})
// digit[2].led[8]
const CD41 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.827), rotate: 0,
  id: 'CD41'
})
// digit[2].led[9]
const CD42 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.827), rotate: 0,
  id: 'CD42'
})
// digit[2].led[10]
const CD43 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.827), rotate: 0,
  id: 'CD43'
})
// digit[2].led[11]
const CD44 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.827), rotate: 0,
  id: 'CD44'
})
// digit[2].led[12]
const CD45 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.945), rotate: 0,
  id: 'CD45'
})
// digit[2].led[13]
const CD46 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.945), rotate: 0,
  id: 'CD46'
})
// digit[3].led[0]
const CD47 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.591), rotate: 0,
  id: 'CD47'
})
// digit[3].led[1]
const CD48 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.591), rotate: 0,
  id: 'CD48'
})
// digit[3].led[2]
const CD49 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.591), rotate: 0,
  id: 'CD49'
})
// digit[3].led[3]
const CD50 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.591), rotate: 0,
  id: 'CD50'
})
// digit[3].led[4]
const CD51 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.709), rotate: 0,
  id: 'CD51'
})
// digit[3].led[5]
const CD52 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.709), rotate: 0,
  id: 'CD52'
})
// digit[3].led[6]
const CD53 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.709), rotate: 0,
  id: 'CD53'
})
// digit[3].led[7]
const CD54 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.709), rotate: 0,
  id: 'CD54'
})
// digit[3].led[8]
const CD55 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.827), rotate: 0,
  id: 'CD55'
})
// digit[3].led[9]
const CD56 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.827), rotate: 0,
  id: 'CD56'
})
// digit[3].led[10]
const CD57 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.827), rotate: 0,
  id: 'CD57'
})
// digit[3].led[11]
const CD58 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.827), rotate: 0,
  id: 'CD58'
})
// digit[3].led[12]
const CD59 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.945), rotate: 0,
  id: 'CD59'
})
// digit[3].led[13]
const CD60 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.945), rotate: 0,
  id: 'CD60'
})
// center.led[0]
const CD61 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.489, 1.780), rotate: 0,
  id: 'CD61'
})
// center.led[1]
const CD62 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.489, 1.898), rotate: 0,
  id: 'CD62'
})
// meta.led[0]
const CD63 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.686, 1.780), rotate: 0,
  id: 'CD63'
})
// meta.led[1]
const CD64 = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.686, 1.898), rotate: 0,
  id: 'CD64'
})
// spk_dac.rc.r
const CR8 = board.add(R_0603_1608Metric, {
  translate: pt(1.338, 2.122), rotate: 0,
  id: 'CR8'
})
// spk_dac.rc.c
const CC11 = board.add(C_0603_1608Metric, {
  translate: pt(1.338, 2.219), rotate: 0,
  id: 'CC11'
})
// spk_tp.tp
const CTP7 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.062, 2.130), rotate: 0,
  id: 'CTP7'
})
// spk_drv.ic
const CU6 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(3.128, 1.171), rotate: 0,
  id: 'CU6'
})
// spk_drv.pwr_cap.cap
const CC12 = board.add(C_0603_1608Metric, {
  translate: pt(3.063, 1.308), rotate: 0,
  id: 'CC12'
})
// spk_drv.bulk_cap.cap
const CC13 = board.add(C_0805_2012Metric, {
  translate: pt(3.357, 1.141), rotate: 0,
  id: 'CC13'
})
// spk_drv.inp_res
const CR9 = board.add(R_0603_1608Metric, {
  translate: pt(3.219, 1.308), rotate: 0,
  id: 'CR9'
})
// spk_drv.inp_cap
const CC14 = board.add(C_0603_1608Metric, {
  translate: pt(3.375, 1.308), rotate: 0,
  id: 'CC14'
})
// spk_drv.inn_res
const CR10 = board.add(R_0603_1608Metric, {
  translate: pt(3.063, 1.405), rotate: 0,
  id: 'CR10'
})
// spk_drv.inn_cap
const CC15 = board.add(C_0603_1608Metric, {
  translate: pt(3.219, 1.405), rotate: 0,
  id: 'CC15'
})
// spk.conn
const CJ3 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.156, 1.870), rotate: 0,
  id: 'CJ3'
})
// v5v_sense.div.top_res
const CR11 = board.add(R_0603_1608Metric, {
  translate: pt(1.573, 2.122), rotate: 0,
  id: 'CR11'
})
// v5v_sense.div.bottom_res
const CR12 = board.add(R_0603_1608Metric, {
  translate: pt(1.573, 2.219), rotate: 0,
  id: 'CR12'
})

board.setNetlist([
  {name: "Cpwr", pads: [["CJ1", "2"], ["CTP1", "1"], ["CU1", "3"], ["CU5", "5"], ["CD5", "2"], ["CD6", "2"], ["CD7", "2"], ["CD8", "2"], ["CD9", "2"], ["CD10", "2"], ["CD11", "2"], ["CD12", "2"], ["CD13", "2"], ["CD14", "2"], ["CD15", "2"], ["CD16", "2"], ["CD17", "2"], ["CD18", "2"], ["CD19", "2"], ["CD20", "2"], ["CD21", "2"], ["CD22", "2"], ["CD23", "2"], ["CD24", "2"], ["CD25", "2"], ["CD26", "2"], ["CD27", "2"], ["CD28", "2"], ["CD29", "2"], ["CD30", "2"], ["CD31", "2"], ["CD32", "2"], ["CD33", "2"], ["CD34", "2"], ["CD35", "2"], ["CD36", "2"], ["CD37", "2"], ["CD38", "2"], ["CD39", "2"], ["CD40", "2"], ["CD41", "2"], ["CD42", "2"], ["CD43", "2"], ["CD44", "2"], ["CD45", "2"], ["CD46", "2"], ["CD47", "2"], ["CD48", "2"], ["CD49", "2"], ["CD50", "2"], ["CD51", "2"], ["CD52", "2"], ["CD53", "2"], ["CD54", "2"], ["CD55", "2"], ["CD56", "2"], ["CD57", "2"], ["CD58", "2"], ["CD59", "2"], ["CD60", "2"], ["CD61", "2"], ["CD62", "2"], ["CD63", "2"], ["CD64", "2"], ["CU6", "1"], ["CU6", "6"], ["CR11", "1"], ["CC1", "1"], ["CC10", "1"], ["CC12", "1"], ["CC13", "1"]]},
  {name: "Cgnd", pads: [["CJ1", "1"], ["CTP2", "1"], ["CU1", "1"], ["CD1", "2"], ["CU2", "1"], ["CU2", "40"], ["CU2", "41"], ["CR2", "2"], ["CR3", "2"], ["CR4", "2"], ["CSW1", "1"], ["CSW2", "1"], ["CSW3", "1"], ["CSW4", "1"], ["CU3", "1"], ["CU3", "5"], ["CU3", "7"], ["CU4", "2"], ["CU4", "3"], ["CU5", "1"], ["CU5", "3"], ["CD5", "4"], ["CD6", "4"], ["CD7", "4"], ["CD8", "4"], ["CD9", "4"], ["CD10", "4"], ["CD11", "4"], ["CD12", "4"], ["CD13", "4"], ["CD14", "4"], ["CD15", "4"], ["CD16", "4"], ["CD17", "4"], ["CD18", "4"], ["CD19", "4"], ["CD20", "4"], ["CD21", "4"], ["CD22", "4"], ["CD23", "4"], ["CD24", "4"], ["CD25", "4"], ["CD26", "4"], ["CD27", "4"], ["CD28", "4"], ["CD29", "4"], ["CD30", "4"], ["CD31", "4"], ["CD32", "4"], ["CD33", "4"], ["CD34", "4"], ["CD35", "4"], ["CD36", "4"], ["CD37", "4"], ["CD38", "4"], ["CD39", "4"], ["CD40", "4"], ["CD41", "4"], ["CD42", "4"], ["CD43", "4"], ["CD44", "4"], ["CD45", "4"], ["CD46", "4"], ["CD47", "4"], ["CD48", "4"], ["CD49", "4"], ["CD50", "4"], ["CD51", "4"], ["CD52", "4"], ["CD53", "4"], ["CD54", "4"], ["CD55", "4"], ["CD56", "4"], ["CD57", "4"], ["CD58", "4"], ["CD59", "4"], ["CD60", "4"], ["CD61", "4"], ["CD62", "4"], ["CD63", "4"], ["CD64", "4"], ["CU6", "7"], ["CU6", "9"], ["CC11", "2"], ["CR12", "2"], ["CC9", "2"], ["CC15", "2"], ["CC1", "2"], ["CC2", "2"], ["CC3", "2"], ["CC4", "2"], ["CJ2", "5"], ["CC6", "2"], ["CC7", "2"], ["CC8", "2"], ["CC10", "2"], ["CC12", "2"], ["CC13", "2"], ["CC5", "2"]]},
  {name: "Cv3v3", pads: [["CU1", "2"], ["CTP3", "1"], ["CD1", "1"], ["CU2", "2"], ["CU3", "2"], ["CU3", "6"], ["CU3", "8"], ["CU4", "1"], ["CC2", "1"], ["CR7", "1"], ["CC3", "1"], ["CC4", "1"], ["CJ2", "1"], ["CR5", "1"], ["CR6", "1"], ["CC7", "1"], ["CC6", "1"], ["CC8", "1"], ["CR1", "1"]]},
  {name: "Cledr.signal", pads: [["CU2", "4"], ["CD2", "2"]]},
  {name: "Cledg.signal", pads: [["CU2", "5"], ["CD3", "2"]]},
  {name: "Cledb.signal", pads: [["CU2", "6"], ["CD4", "2"]]},
  {name: "Csw[0].out", pads: [["CU2", "32"], ["CSW1", "2"]]},
  {name: "Csw[1].out", pads: [["CU2", "33"], ["CSW2", "2"]]},
  {name: "Csw[2].out", pads: [["CU2", "34"], ["CSW3", "2"]]},
  {name: "Csw[3].out", pads: [["CU2", "35"], ["CSW4", "2"]]},
  {name: "Ci2c_chain_0.scl", pads: [["CU2", "9"], ["CU3", "4"], ["CU4", "6"], ["CR5", "2"], ["CTP4", "1"]]},
  {name: "Ci2c_chain_0.sda", pads: [["CU2", "8"], ["CU3", "3"], ["CU4", "4"], ["CR6", "2"], ["CTP5", "1"]]},
  {name: "Crgb_shift.input", pads: [["CU2", "12"], ["CU5", "2"]]},
  {name: "Crgb_shift.output", pads: [["CU5", "4"], ["CD5", "1"], ["CTP6", "1"]]},
  {name: "Cdigit[0].dout", pads: [["CD18", "3"], ["CD19", "1"]]},
  {name: "Cdigit[1].dout", pads: [["CD32", "3"], ["CD63", "1"]]},
  {name: "Cmeta.dout", pads: [["CD64", "3"], ["CD61", "1"]]},
  {name: "Ccenter.dout", pads: [["CD62", "3"], ["CD33", "1"]]},
  {name: "Cdigit[2].dout", pads: [["CD46", "3"], ["CD47", "1"]]},
  {name: "Cspk_chain_0", pads: [["CU2", "31"], ["CR8", "1"]]},
  {name: "Cspk_chain_1", pads: [["CTP7", "1"], ["CC14", "2"], ["CR8", "2"], ["CC11", "1"]]},
  {name: "Cspk_chain_2.a", pads: [["CU6", "8"], ["CJ3", "1"]]},
  {name: "Cspk_chain_2.b", pads: [["CU6", "5"], ["CJ3", "2"]]},
  {name: "Cv5v_sense.output", pads: [["CU2", "7"], ["CR11", "2"], ["CR12", "1"]]},
  {name: "Cmcu.program_uart_node.a_tx", pads: [["CU2", "37"], ["CJ2", "3"]]},
  {name: "Cmcu.program_uart_node.b_tx", pads: [["CU2", "36"], ["CJ2", "4"]]},
  {name: "Cmcu.program_en_node", pads: [["CU2", "3"], ["CJ2", "6"], ["CR1", "2"], ["CC5", "1"]]},
  {name: "Cmcu.program_boot_node", pads: [["CU2", "27"], ["CJ2", "2"]]},
  {name: "Cledr.res.a", pads: [["CR2", "1"], ["CD2", "1"]]},
  {name: "Cledg.res.a", pads: [["CR3", "1"], ["CD3", "1"]]},
  {name: "Cledb.res.a", pads: [["CR4", "1"], ["CD4", "1"]]},
  {name: "Cals.dvi_res.b", pads: [["CR7", "2"], ["CU4", "5"], ["CC9", "1"]]},
  {name: "Cdigit[0].led[0].dout", pads: [["CD5", "3"], ["CD6", "1"]]},
  {name: "Cdigit[0].led[1].dout", pads: [["CD6", "3"], ["CD7", "1"]]},
  {name: "Cdigit[0].led[2].dout", pads: [["CD7", "3"], ["CD8", "1"]]},
  {name: "Cdigit[0].led[3].dout", pads: [["CD8", "3"], ["CD9", "1"]]},
  {name: "Cdigit[0].led[4].dout", pads: [["CD9", "3"], ["CD10", "1"]]},
  {name: "Cdigit[0].led[5].dout", pads: [["CD10", "3"], ["CD11", "1"]]},
  {name: "Cdigit[0].led[6].dout", pads: [["CD11", "3"], ["CD12", "1"]]},
  {name: "Cdigit[0].led[7].dout", pads: [["CD12", "3"], ["CD13", "1"]]},
  {name: "Cdigit[0].led[8].dout", pads: [["CD13", "3"], ["CD14", "1"]]},
  {name: "Cdigit[0].led[9].dout", pads: [["CD14", "3"], ["CD15", "1"]]},
  {name: "Cdigit[0].led[10].dout", pads: [["CD15", "3"], ["CD16", "1"]]},
  {name: "Cdigit[0].led[11].dout", pads: [["CD16", "3"], ["CD17", "1"]]},
  {name: "Cdigit[0].led[12].dout", pads: [["CD17", "3"], ["CD18", "1"]]},
  {name: "Cdigit[1].led[0].dout", pads: [["CD19", "3"], ["CD20", "1"]]},
  {name: "Cdigit[1].led[1].dout", pads: [["CD20", "3"], ["CD21", "1"]]},
  {name: "Cdigit[1].led[2].dout", pads: [["CD21", "3"], ["CD22", "1"]]},
  {name: "Cdigit[1].led[3].dout", pads: [["CD22", "3"], ["CD23", "1"]]},
  {name: "Cdigit[1].led[4].dout", pads: [["CD23", "3"], ["CD24", "1"]]},
  {name: "Cdigit[1].led[5].dout", pads: [["CD24", "3"], ["CD25", "1"]]},
  {name: "Cdigit[1].led[6].dout", pads: [["CD25", "3"], ["CD26", "1"]]},
  {name: "Cdigit[1].led[7].dout", pads: [["CD26", "3"], ["CD27", "1"]]},
  {name: "Cdigit[1].led[8].dout", pads: [["CD27", "3"], ["CD28", "1"]]},
  {name: "Cdigit[1].led[9].dout", pads: [["CD28", "3"], ["CD29", "1"]]},
  {name: "Cdigit[1].led[10].dout", pads: [["CD29", "3"], ["CD30", "1"]]},
  {name: "Cdigit[1].led[11].dout", pads: [["CD30", "3"], ["CD31", "1"]]},
  {name: "Cdigit[1].led[12].dout", pads: [["CD31", "3"], ["CD32", "1"]]},
  {name: "Cdigit[2].led[0].dout", pads: [["CD33", "3"], ["CD34", "1"]]},
  {name: "Cdigit[2].led[1].dout", pads: [["CD34", "3"], ["CD35", "1"]]},
  {name: "Cdigit[2].led[2].dout", pads: [["CD35", "3"], ["CD36", "1"]]},
  {name: "Cdigit[2].led[3].dout", pads: [["CD36", "3"], ["CD37", "1"]]},
  {name: "Cdigit[2].led[4].dout", pads: [["CD37", "3"], ["CD38", "1"]]},
  {name: "Cdigit[2].led[5].dout", pads: [["CD38", "3"], ["CD39", "1"]]},
  {name: "Cdigit[2].led[6].dout", pads: [["CD39", "3"], ["CD40", "1"]]},
  {name: "Cdigit[2].led[7].dout", pads: [["CD40", "3"], ["CD41", "1"]]},
  {name: "Cdigit[2].led[8].dout", pads: [["CD41", "3"], ["CD42", "1"]]},
  {name: "Cdigit[2].led[9].dout", pads: [["CD42", "3"], ["CD43", "1"]]},
  {name: "Cdigit[2].led[10].dout", pads: [["CD43", "3"], ["CD44", "1"]]},
  {name: "Cdigit[2].led[11].dout", pads: [["CD44", "3"], ["CD45", "1"]]},
  {name: "Cdigit[2].led[12].dout", pads: [["CD45", "3"], ["CD46", "1"]]},
  {name: "Cdigit[3].led[0].dout", pads: [["CD47", "3"], ["CD48", "1"]]},
  {name: "Cdigit[3].led[1].dout", pads: [["CD48", "3"], ["CD49", "1"]]},
  {name: "Cdigit[3].led[2].dout", pads: [["CD49", "3"], ["CD50", "1"]]},
  {name: "Cdigit[3].led[3].dout", pads: [["CD50", "3"], ["CD51", "1"]]},
  {name: "Cdigit[3].led[4].dout", pads: [["CD51", "3"], ["CD52", "1"]]},
  {name: "Cdigit[3].led[5].dout", pads: [["CD52", "3"], ["CD53", "1"]]},
  {name: "Cdigit[3].led[6].dout", pads: [["CD53", "3"], ["CD54", "1"]]},
  {name: "Cdigit[3].led[7].dout", pads: [["CD54", "3"], ["CD55", "1"]]},
  {name: "Cdigit[3].led[8].dout", pads: [["CD55", "3"], ["CD56", "1"]]},
  {name: "Cdigit[3].led[9].dout", pads: [["CD56", "3"], ["CD57", "1"]]},
  {name: "Cdigit[3].led[10].dout", pads: [["CD57", "3"], ["CD58", "1"]]},
  {name: "Cdigit[3].led[11].dout", pads: [["CD58", "3"], ["CD59", "1"]]},
  {name: "Cdigit[3].led[12].dout", pads: [["CD59", "3"], ["CD60", "1"]]},
  {name: "Cdigit[3].dout", pads: [["CD60", "3"]]},
  {name: "Ccenter.led[0].dout", pads: [["CD61", "3"], ["CD62", "1"]]},
  {name: "Cmeta.led[0].dout", pads: [["CD63", "3"], ["CD64", "1"]]},
  {name: "Cspk_drv.inp_cap.pos", pads: [["CC14", "1"], ["CR9", "1"]]},
  {name: "Cspk_drv.inp_res.b", pads: [["CR9", "2"], ["CU6", "4"]]},
  {name: "Cspk_drv.inn_cap.pos", pads: [["CC15", "1"], ["CR10", "1"]]},
  {name: "Cspk_drv.inn_res.b", pads: [["CR10", "2"], ["CU6", "3"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.6425196850393706, 2.3822834645669295);
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


