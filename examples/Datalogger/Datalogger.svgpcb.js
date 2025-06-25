const board = new PCB();

// pwr_conn
const J1 = board.add(Molex_DuraClik_vert_3pin, {
  translate: pt(3.367, 2.356), rotate: 0,
  id: 'J1'
})
// usb_conn.conn
const J2 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.843, 1.867), rotate: 0,
  id: 'J2'
})
// usb_conn.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(1.692, 2.122), rotate: 0,
  id: 'R1'
})
// usb_conn.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(1.848, 2.122), rotate: 0,
  id: 'R2'
})
// bat
const U1 = board.add(BatteryHolder_Keystone_106_1x20mm, {
  translate: pt(2.492, 0.369), rotate: 0,
  id: 'U1'
})
// pwr_5v.ic
const U2 = board.add(SOT_23_6, {
  translate: pt(2.511, 1.770), rotate: 0,
  id: 'U2'
})
// pwr_5v.fb.div.top_res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(2.576, 1.987), rotate: 0,
  id: 'R3'
})
// pwr_5v.fb.div.bottom_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(2.229, 2.104), rotate: 0,
  id: 'R4'
})
// pwr_5v.hf_in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(2.385, 2.104), rotate: 0,
  id: 'C1'
})
// pwr_5v.vbst_cap
const C2 = board.add(C_0603_1608Metric, {
  translate: pt(2.541, 2.104), rotate: 0,
  id: 'C2'
})
// pwr_5v.power_path.inductor
const L1 = board.add(L_Taiyo_Yuden_NR_50xx, {
  translate: pt(2.281, 1.811), rotate: 0,
  id: 'L1'
})
// pwr_5v.power_path.in_cap.cap
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(2.238, 1.997), rotate: 0,
  id: 'C3'
})
// pwr_5v.power_path.out_cap.cap
const C4 = board.add(C_0805_2012Metric, {
  translate: pt(2.411, 1.997), rotate: 0,
  id: 'C4'
})
// buffer.sense
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(1.881, 1.364), rotate: 0,
  id: 'R5'
})
// buffer.fet
const Q1 = board.add(SOT_223_3_TabPin2, {
  translate: pt(1.996, 0.981), rotate: 0,
  id: 'Q1'
})
// buffer.diode
const D1 = board.add(D_SOD_323, {
  translate: pt(2.087, 1.200), rotate: 0,
  id: 'D1'
})
// buffer.set.div.top_res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(2.037, 1.364), rotate: 0,
  id: 'R6'
})
// buffer.set.div.bottom_res
const R7 = board.add(R_0603_1608Metric, {
  translate: pt(1.263, 1.465), rotate: 0,
  id: 'R7'
})
// buffer.amp.ic
const U3 = board.add(SOT_23_6, {
  translate: pt(1.904, 1.229), rotate: 0,
  id: 'U3'
})
// buffer.amp.vdd_cap.cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(1.419, 1.465), rotate: 0,
  id: 'C5'
})
// buffer.cap
const C6 = board.add(CP_Radial_D14_0mm_P5_00mm, {
  translate: pt(1.406, 1.118), rotate: 0,
  id: 'C6'
})
// pwr_3v3.ic
const U4 = board.add(SOT_223_3_TabPin2, {
  translate: pt(2.925, 1.844), rotate: 0,
  id: 'U4'
})
// pwr_3v3.in_cap.cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(2.983, 2.054), rotate: 0,
  id: 'C7'
})
// pwr_3v3.out_cap.cap
const C8 = board.add(C_0805_2012Metric, {
  translate: pt(2.819, 2.064), rotate: 0,
  id: 'C8'
})
// mcu.swd.conn
const J3 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(1.941, 0.146), rotate: 0,
  id: 'J3'
})
// mcu.ic
const U5 = board.add(LQFP_64_10x10mm_P0_5mm, {
  translate: pt(1.469, 0.264), rotate: 0,
  id: 'U5'
})
// mcu.swd_pull.swdio.res
const R8 = board.add(R_0603_1608Metric, {
  translate: pt(1.263, 0.596), rotate: 0,
  id: 'R8'
})
// mcu.swd_pull.swclk.res
const R9 = board.add(R_0603_1608Metric, {
  translate: pt(1.419, 0.596), rotate: 0,
  id: 'R9'
})
// mcu.pwr_cap[0].cap
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(1.575, 0.596), rotate: 0,
  id: 'C9'
})
// mcu.pwr_cap[1].cap
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(1.731, 0.596), rotate: 0,
  id: 'C10'
})
// mcu.pwr_cap[2].cap
const C11 = board.add(C_0603_1608Metric, {
  translate: pt(1.887, 0.596), rotate: 0,
  id: 'C11'
})
// mcu.pwr_cap[3].cap
const C12 = board.add(C_0603_1608Metric, {
  translate: pt(2.043, 0.596), rotate: 0,
  id: 'C12'
})
// mcu.pwr_cap[4].cap
const C13 = board.add(C_0603_1608Metric, {
  translate: pt(2.198, 0.596), rotate: 0,
  id: 'C13'
})
// mcu.pwr_cap[5].cap
const C14 = board.add(C_0603_1608Metric, {
  translate: pt(1.263, 0.693), rotate: 0,
  id: 'C14'
})
// mcu.vbat_cap.cap
const C15 = board.add(C_0603_1608Metric, {
  translate: pt(1.419, 0.693), rotate: 0,
  id: 'C15'
})
// mcu.pwra_cap[0].cap
const C16 = board.add(C_0603_1608Metric, {
  translate: pt(1.575, 0.693), rotate: 0,
  id: 'C16'
})
// mcu.pwra_cap[1].cap
const C17 = board.add(C_0805_2012Metric, {
  translate: pt(2.043, 0.369), rotate: 0,
  id: 'C17'
})
// mcu.vref_cap[0].cap
const C18 = board.add(C_0603_1608Metric, {
  translate: pt(1.731, 0.693), rotate: 0,
  id: 'C18'
})
// mcu.vref_cap[1].cap
const C19 = board.add(C_0603_1608Metric, {
  translate: pt(1.887, 0.693), rotate: 0,
  id: 'C19'
})
// mcu.vref_cap[2].cap
const C20 = board.add(C_0805_2012Metric, {
  translate: pt(2.217, 0.369), rotate: 0,
  id: 'C20'
})
// mcu.crystal.package
const X1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(1.854, 0.398), rotate: 0,
  id: 'X1'
})
// mcu.crystal.cap_a
const C21 = board.add(C_0603_1608Metric, {
  translate: pt(2.043, 0.693), rotate: 0,
  id: 'C21'
})
// mcu.crystal.cap_b
const C22 = board.add(C_0603_1608Metric, {
  translate: pt(2.198, 0.693), rotate: 0,
  id: 'C22'
})
// can.conn
const J4 = board.add(Molex_DuraClik_vert_5pin, {
  translate: pt(0.000, 2.238), rotate: 0,
  id: 'J4'
})
// can.can_fuse.fuse
const F1 = board.add(R_0603_1608Metric, {
  translate: pt(0.231, 2.150), rotate: 0,
  id: 'F1'
})
// can.reg.ic
const U6 = board.add(SOT_23_5, {
  translate: pt(0.589, 1.770), rotate: 0,
  id: 'U6'
})
// can.reg.in_cap.cap
const C23 = board.add(C_0603_1608Metric, {
  translate: pt(0.387, 2.150), rotate: 0,
  id: 'C23'
})
// can.reg.out_cap.cap
const C24 = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 2.160), rotate: 0,
  id: 'C24'
})
// can.esd
const U7 = board.add(SOT_23, {
  translate: pt(0.583, 1.943), rotate: 0,
  id: 'U7'
})
// can.transceiver.ic
const U8 = board.add(SOP_8_6_62x9_15mm_P2_54mm, {
  translate: pt(0.234, 1.893), rotate: 0,
  id: 'U8'
})
// can.transceiver.logic_cap.cap
const C25 = board.add(C_0603_1608Metric, {
  translate: pt(0.543, 2.150), rotate: 0,
  id: 'C25'
})
// can.transceiver.can_cap.cap
const C26 = board.add(C_0603_1608Metric, {
  translate: pt(0.699, 2.150), rotate: 0,
  id: 'C26'
})
// sd
const J5 = board.add(SD_Kyocera_145638009511859+, {
  translate: pt(0.565, 1.122), rotate: 0,
  id: 'J5'
})
// cd_pull.res
const R10 = board.add(R_0603_1608Metric, {
  translate: pt(2.721, 2.385), rotate: 0,
  id: 'R10'
})
// xbee.ic
const U9 = board.add(XBEE, {
  translate: pt(1.641, 2.453), rotate: 0,
  id: 'U9'
})
// xbee.vdd_cap_0.cap
const C27 = board.add(C_0603_1608Metric, {
  translate: pt(1.544, 2.385), rotate: 0,
  id: 'C27'
})
// xbee.vdd_cap_1.cap
const C28 = board.add(C_0603_1608Metric, {
  translate: pt(1.544, 2.482), rotate: 0,
  id: 'C28'
})
// xbee_assoc.package
const D2 = board.add(LED_0603_1608Metric, {
  translate: pt(0.840, 2.385), rotate: 0,
  id: 'D2'
})
// xbee_assoc.res
const R11 = board.add(R_0603_1608Metric, {
  translate: pt(0.839, 2.482), rotate: 0,
  id: 'R11'
})
// rtc.ic
const U10 = board.add(SOIC_16W_7_5x10_3mm_P1_27mm, {
  translate: pt(1.109, 1.915), rotate: 0,
  id: 'U10'
})
// rtc.vdd_res.res
const R12 = board.add(R_0603_1608Metric, {
  translate: pt(1.440, 1.848), rotate: 0,
  id: 'R12'
})
// rtc.vdd_cap_0.cap
const C29 = board.add(C_0603_1608Metric, {
  translate: pt(1.440, 1.945), rotate: 0,
  id: 'C29'
})
// rtc.vdd_cap_1.cap
const C30 = board.add(C_0805_2012Metric, {
  translate: pt(1.449, 1.741), rotate: 0,
  id: 'C30'
})
// rtc.vbat_cap.cap
const C31 = board.add(C_0603_1608Metric, {
  translate: pt(1.440, 2.042), rotate: 0,
  id: 'C31'
})
// rtc.bbs_cap.cap
const C32 = board.add(C_0603_1608Metric, {
  translate: pt(0.934, 2.196), rotate: 0,
  id: 'C32'
})
// eink.ic
const U11 = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(2.644, 1.032), rotate: 0,
  id: 'U11'
})
// eink.boost_sw
const Q2 = board.add(SOT_23, {
  translate: pt(3.115, 0.906), rotate: 0,
  id: 'Q2'
})
// eink.boost_ind
const L2 = board.add(L_0805_2012Metric, {
  translate: pt(2.979, 1.223), rotate: 0,
  id: 'L2'
})
// eink.boost_res
const R13 = board.add(R_0603_1608Metric, {
  translate: pt(3.146, 1.219), rotate: 0,
  id: 'R13'
})
// eink.boot_cap
const C33 = board.add(C_0805_2012Metric, {
  translate: pt(2.804, 1.228), rotate: 0,
  id: 'C33'
})
// eink.vdd_cap0.cap
const C34 = board.add(C_0603_1608Metric, {
  translate: pt(2.346, 1.348), rotate: 0,
  id: 'C34'
})
// eink.vdd_cap1.cap
const C35 = board.add(C_0603_1608Metric, {
  translate: pt(2.502, 1.348), rotate: 0,
  id: 'C35'
})
// eink.vslr_cap
const C36 = board.add(C_0603_1608Metric, {
  translate: pt(2.658, 1.348), rotate: 0,
  id: 'C36'
})
// eink.vdhr_cap
const C37 = board.add(C_0603_1608Metric, {
  translate: pt(2.813, 1.348), rotate: 0,
  id: 'C37'
})
// eink.vddd_cap
const C38 = board.add(C_0603_1608Metric, {
  translate: pt(2.969, 1.348), rotate: 0,
  id: 'C38'
})
// eink.vdh_cap
const C39 = board.add(C_0603_1608Metric, {
  translate: pt(3.125, 1.348), rotate: 0,
  id: 'C39'
})
// eink.vgh_cap
const C40 = board.add(C_0603_1608Metric, {
  translate: pt(2.346, 1.445), rotate: 0,
  id: 'C40'
})
// eink.vdl_cap
const C41 = board.add(C_0603_1608Metric, {
  translate: pt(2.502, 1.445), rotate: 0,
  id: 'C41'
})
// eink.vgl_cap
const C42 = board.add(C_0603_1608Metric, {
  translate: pt(2.658, 1.445), rotate: 0,
  id: 'C42'
})
// eink.vcom_cap
const C43 = board.add(C_0603_1608Metric, {
  translate: pt(2.813, 1.445), rotate: 0,
  id: 'C43'
})
// eink.boost_dio
const D3 = board.add(D_SOD_123, {
  translate: pt(3.132, 1.058), rotate: 0,
  id: 'D3'
})
// eink.vgl_dio
const D4 = board.add(D_SOD_123, {
  translate: pt(2.380, 1.235), rotate: 0,
  id: 'D4'
})
// eink.boot_dio
const D5 = board.add(D_SOD_123, {
  translate: pt(2.605, 1.235), rotate: 0,
  id: 'D5'
})
// ext
const U12 = board.add(PinHeader_1x06_P2_54mm_Vertical, {
  translate: pt(3.414, 1.410), rotate: 0,
  id: 'U12'
})
// rgb1.package
const D6 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(0.041, 2.411), rotate: 0,
  id: 'D6'
})
// rgb1.red_res
const R14 = board.add(R_0603_1608Metric, {
  translate: pt(0.180, 2.385), rotate: 0,
  id: 'R14'
})
// rgb1.green_res
const R15 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.535), rotate: 0,
  id: 'R15'
})
// rgb1.blue_res
const R16 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.535), rotate: 0,
  id: 'R16'
})
// rgb2.package
const D7 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(0.432, 2.411), rotate: 0,
  id: 'D7'
})
// rgb2.red_res
const R17 = board.add(R_0603_1608Metric, {
  translate: pt(0.571, 2.385), rotate: 0,
  id: 'R17'
})
// rgb2.green_res
const R18 = board.add(R_0603_1608Metric, {
  translate: pt(0.449, 2.535), rotate: 0,
  id: 'R18'
})
// rgb2.blue_res
const R19 = board.add(R_0603_1608Metric, {
  translate: pt(0.605, 2.535), rotate: 0,
  id: 'R19'
})
// rgb3.package
const D8 = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(3.258, 1.758), rotate: 0,
  id: 'D8'
})
// rgb3.red_res
const R20 = board.add(R_0603_1608Metric, {
  translate: pt(3.397, 1.731), rotate: 0,
  id: 'R20'
})
// rgb3.green_res
const R21 = board.add(R_0603_1608Metric, {
  translate: pt(3.275, 1.881), rotate: 0,
  id: 'R21'
})
// rgb3.blue_res
const R22 = board.add(R_0603_1608Metric, {
  translate: pt(3.431, 1.881), rotate: 0,
  id: 'R22'
})
// sw1.package
const SW1 = board.add(SW_Push_SPST_NO_Alps_SKRK, {
  translate: pt(2.102, 2.423), rotate: 0,
  id: 'SW1'
})
// sw1_pull.res
const R23 = board.add(R_0603_1608Metric, {
  translate: pt(2.956, 2.385), rotate: 0,
  id: 'R23'
})
// sw2.package
const SW2 = board.add(SW_Push_SPST_NO_Alps_SKRK, {
  translate: pt(2.437, 2.423), rotate: 0,
  id: 'SW2'
})
// sw2_pull.res
const R24 = board.add(R_0603_1608Metric, {
  translate: pt(3.191, 2.385), rotate: 0,
  id: 'R24'
})
// v12sense.div.top_res
const R25 = board.add(R_0603_1608Metric, {
  translate: pt(1.818, 2.385), rotate: 0,
  id: 'R25'
})
// v12sense.div.bottom_res
const R26 = board.add(R_0603_1608Metric, {
  translate: pt(1.818, 2.482), rotate: 0,
  id: 'R26'
})
// v5sense.div.top_res
const R27 = board.add(R_0603_1608Metric, {
  translate: pt(1.309, 2.385), rotate: 0,
  id: 'R27'
})
// v5sense.div.bottom_res
const R28 = board.add(R_0603_1608Metric, {
  translate: pt(1.309, 2.482), rotate: 0,
  id: 'R28'
})
// vscsense.div.top_res
const R29 = board.add(R_0603_1608Metric, {
  translate: pt(1.074, 2.385), rotate: 0,
  id: 'R29'
})
// vscsense.div.bottom_res
const R30 = board.add(R_0603_1608Metric, {
  translate: pt(1.074, 2.482), rotate: 0,
  id: 'R30'
})

board.setNetlist([
  {name: "gnd", pads: [["J1", "1"], ["J1", "3"], ["U1", "2"], ["J5", "3"], ["J5", "6"], ["J5", "SH"], ["U12", "3"], ["J2", "A1"], ["J2", "B12"], ["J2", "B1"], ["J2", "A12"], ["U2", "1"], ["C6", "2"], ["U4", "1"], ["U5", "21"], ["U5", "14"], ["U5", "26"], ["U5", "27"], ["U5", "55"], ["U5", "56"], ["U9", "10"], ["U9", "14"], ["R11", "2"], ["U10", "5"], ["U10", "8"], ["U11", "17"], ["U11", "8"], ["SW1", "2"], ["SW2", "2"], ["U8", "4"], ["R26", "2"], ["R28", "2"], ["R30", "2"], ["J2", "S1"], ["R13", "2"], ["C36", "2"], ["C37", "2"], ["C38", "2"], ["C39", "2"], ["C40", "2"], ["C41", "2"], ["C42", "2"], ["C43", "2"], ["D5", "1"], ["C1", "2"], ["U3", "2"], ["C7", "2"], ["C8", "2"], ["C9", "2"], ["C10", "2"], ["C11", "2"], ["C12", "2"], ["C13", "2"], ["C14", "2"], ["C15", "2"], ["C16", "2"], ["C17", "2"], ["C18", "2"], ["C19", "2"], ["C20", "2"], ["X1", "2"], ["X1", "4"], ["C27", "2"], ["C28", "2"], ["C29", "2"], ["C30", "2"], ["C31", "2"], ["C32", "2"], ["C34", "2"], ["C35", "2"], ["R4", "2"], ["R7", "2"], ["R9", "1"], ["C25", "2"], ["R1", "1"], ["R2", "1"], ["J3", "3"], ["J3", "5"], ["J3", "9"], ["C21", "2"], ["C22", "2"], ["C3", "2"], ["C4", "2"], ["C5", "2"]]},
  {name: "vin", pads: [["J1", "2"], ["U2", "3"], ["R25", "1"], ["U2", "5"], ["C1", "1"], ["C3", "1"]]},
  {name: "v5", pads: [["R27", "1"], ["J2", "A4"], ["J2", "B9"], ["J2", "B4"], ["J2", "A9"], ["R5", "1"], ["U3", "5"], ["U3", "6"], ["R6", "1"], ["R3", "1"], ["D1", "1"], ["U4", "3"], ["C5", "1"], ["C7", "1"], ["L1", "2"], ["C4", "1"]]},
  {name: "v3v3", pads: [["J5", "4"], ["U12", "2"], ["U4", "2"], ["U5", "20"], ["U5", "13"], ["U5", "18"], ["U5", "41"], ["U5", "22"], ["U5", "37"], ["U5", "52"], ["U5", "57"], ["R10", "1"], ["U9", "1"], ["U11", "10"], ["U11", "9"], ["D6", "2"], ["D7", "2"], ["D8", "2"], ["R23", "1"], ["R24", "1"], ["U8", "1"], ["R12", "1"], ["C8", "1"], ["L2", "1"], ["J3", "1"], ["C9", "1"], ["C10", "1"], ["C11", "1"], ["C12", "1"], ["C13", "1"], ["C14", "1"], ["C15", "1"], ["C16", "1"], ["C17", "1"], ["C18", "1"], ["C19", "1"], ["C20", "1"], ["C27", "1"], ["C28", "1"], ["C34", "1"], ["C35", "1"], ["R8", "1"], ["C25", "1"]]},
  {name: "usb_conn.usb.dp", pads: [["U5", "47"], ["J2", "A6"], ["J2", "B6"]]},
  {name: "usb_conn.usb.dm", pads: [["U5", "48"], ["J2", "A7"], ["J2", "B7"]]},
  {name: "can.controller.txd", pads: [["U5", "51"], ["U8", "3"]]},
  {name: "can.controller.rxd", pads: [["U5", "53"], ["U8", "2"]]},
  {name: "sd.spi.sck", pads: [["U5", "17"], ["J5", "5"]]},
  {name: "sd.spi.mosi", pads: [["U5", "15"], ["J5", "2"]]},
  {name: "sd.spi.miso", pads: [["U5", "19"], ["J5", "7"]]},
  {name: "sd.cs", pads: [["U5", "11"], ["J5", "1"]]},
  {name: "cd_pull.io", pads: [["U5", "16"], ["J5", "10"], ["R10", "2"]]},
  {name: "xbee.data.rx", pads: [["U5", "58"], ["U9", "3"]]},
  {name: "xbee.data.tx", pads: [["U5", "50"], ["U9", "2"]]},
  {name: "xbee.associate", pads: [["U9", "15"], ["D2", "2"]]},
  {name: "rtc.spi.sck", pads: [["U5", "5"], ["U10", "1"], ["U11", "12"]]},
  {name: "rtc.spi.mosi", pads: [["U5", "6"], ["U10", "2"], ["U11", "11"]]},
  {name: "rtc.spi.miso", pads: [["U5", "7"], ["U10", "3"]]},
  {name: "rtc.cs", pads: [["U5", "64"], ["U10", "4"]]},
  {name: "bat.pwr", pads: [["U1", "1"], ["U10", "15"], ["C31", "1"]]},
  {name: "eink.busy", pads: [["U5", "1"], ["U11", "16"]]},
  {name: "eink.reset", pads: [["U5", "2"], ["U11", "15"]]},
  {name: "eink.dc", pads: [["U5", "3"], ["U11", "14"]]},
  {name: "eink.cs", pads: [["U5", "4"], ["U11", "13"]]},
  {name: "ext.data.rx", pads: [["U5", "60"], ["U12", "5"]]},
  {name: "ext.data.tx", pads: [["U5", "61"], ["U12", "4"]]},
  {name: "ext.cts", pads: [["U5", "62"], ["U12", "1"]]},
  {name: "ext.rts", pads: [["U5", "59"], ["U12", "6"]]},
  {name: "mcu.gpio.rgb1_red", pads: [["U5", "31"], ["R14", "2"]]},
  {name: "mcu.gpio.rgb1_green", pads: [["U5", "32"], ["R15", "2"]]},
  {name: "mcu.gpio.rgb1_blue", pads: [["U5", "30"], ["R16", "2"]]},
  {name: "mcu.gpio.rgb2_red", pads: [["U5", "28"], ["R17", "2"]]},
  {name: "mcu.gpio.rgb2_green", pads: [["U5", "29"], ["R18", "2"]]},
  {name: "mcu.gpio.rgb2_blue", pads: [["U5", "25"], ["R19", "2"]]},
  {name: "mcu.gpio.rgb3_red", pads: [["U5", "46"], ["R20", "2"]]},
  {name: "mcu.gpio.rgb3_green", pads: [["U5", "39"], ["R21", "2"]]},
  {name: "mcu.gpio.rgb3_blue", pads: [["U5", "34"], ["R22", "2"]]},
  {name: "sw1.out", pads: [["U5", "33"], ["SW1", "1"], ["R23", "2"]]},
  {name: "sw2.out", pads: [["U5", "23"], ["SW2", "1"], ["R24", "2"]]},
  {name: "v12sense.output", pads: [["U5", "10"], ["R25", "2"], ["R26", "1"]]},
  {name: "v5sense.output", pads: [["U5", "9"], ["R27", "2"], ["R28", "1"]]},
  {name: "buffer.sc_out", pads: [["C6", "1"], ["R29", "1"], ["Q1", "2"], ["D1", "2"]]},
  {name: "vscsense.output", pads: [["U5", "8"], ["R29", "2"], ["R30", "1"]]},
  {name: "usb_conn.conn.cc.cc1", pads: [["J2", "A5"], ["R1", "2"]]},
  {name: "usb_conn.conn.cc.cc2", pads: [["J2", "B5"], ["R2", "2"]]},
  {name: "pwr_5v.fb.output", pads: [["U2", "4"], ["R3", "2"], ["R4", "1"]]},
  {name: "pwr_5v.vbst_cap.neg", pads: [["C2", "2"], ["U2", "2"], ["L1", "1"]]},
  {name: "pwr_5v.vbst_cap.pos", pads: [["C2", "1"], ["U2", "6"]]},
  {name: "buffer.fet.source", pads: [["Q1", "3"], ["R5", "2"], ["U3", "4"]]},
  {name: "buffer.set.output", pads: [["U3", "3"], ["R6", "2"], ["R7", "1"]]},
  {name: "buffer.fet.gate", pads: [["Q1", "1"], ["U3", "1"]]},
  {name: "mcu.xtal_node.xi", pads: [["U5", "36"], ["X1", "1"], ["C21", "1"]]},
  {name: "mcu.xtal_node.xo", pads: [["U5", "35"], ["X1", "3"], ["C22", "1"]]},
  {name: "mcu.swd_node.swdio", pads: [["U5", "44"], ["J3", "2"], ["R8", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["U5", "40"], ["J3", "4"], ["R9", "2"]]},
  {name: "mcu.reset_node", pads: [["U5", "45"], ["J3", "10"]]},
  {name: "mcu.swd.swo", pads: [["U5", "12"], ["J3", "6"]]},
  {name: "mcu.swd.tdi", pads: [["J3", "8"]]},
  {name: "mcu.ic.xtal_rtc.xtal_in", pads: [["U5", "42"]]},
  {name: "mcu.ic.xtal_rtc.xtal_out", pads: [["U5", "43"]]},
  {name: "can.can.canh", pads: [["J4", "4"], ["U7", "2"], ["U8", "7"]]},
  {name: "can.can.canl", pads: [["J4", "5"], ["U7", "1"], ["U8", "6"]]},
  {name: "can.conn.pwr", pads: [["J4", "2"], ["F1", "1"]]},
  {name: "can.can_fuse.pwr_out", pads: [["F1", "2"], ["U6", "1"], ["U6", "3"], ["C23", "1"]]},
  {name: "can.conn.gnd", pads: [["J4", "3"], ["U7", "3"], ["U6", "2"], ["U8", "5"], ["C23", "2"], ["C24", "2"], ["C26", "2"]]},
  {name: "can.transceiver.can_pwr", pads: [["U8", "8"], ["U6", "5"], ["C26", "1"], ["C24", "1"]]},
  {name: "sd.wp", pads: [["J5", "11"]]},
  {name: "xbee.rssi", pads: [["U9", "6"]]},
  {name: "xbee_assoc.res.a", pads: [["R11", "1"], ["D2", "1"]]},
  {name: "rtc.clkout", pads: [["U10", "7"]]},
  {name: "rtc.int", pads: [["U10", "13"]]},
  {name: "rtc.ic.pwr", pads: [["U10", "16"], ["R12", "2"], ["C29", "1"], ["C30", "1"]]},
  {name: "rtc.ic.bbs", pads: [["U10", "14"], ["C32", "1"]]},
  {name: "eink.boost_ind.b", pads: [["L2", "2"], ["Q2", "3"], ["C33", "1"], ["D3", "2"]]},
  {name: "eink.boost_sw.gate", pads: [["Q2", "1"], ["U11", "23"]]},
  {name: "eink.boost_sw.source", pads: [["Q2", "2"], ["R13", "1"], ["U11", "22"]]},
  {name: "eink.ic.vslr", pads: [["U11", "21"], ["C36", "1"]]},
  {name: "eink.ic.vdhr", pads: [["U11", "20"], ["C37", "1"]]},
  {name: "eink.ic.vddd", pads: [["U11", "7"], ["C38", "1"]]},
  {name: "eink.ic.vdh", pads: [["U11", "5"], ["C39", "1"]]},
  {name: "eink.ic.vgh", pads: [["U11", "4"], ["C40", "1"], ["D3", "1"]]},
  {name: "eink.ic.vdl", pads: [["U11", "3"], ["C41", "1"]]},
  {name: "eink.ic.vgl", pads: [["U11", "2"], ["C42", "1"], ["D4", "2"]]},
  {name: "eink.ic.vcom", pads: [["U11", "1"], ["C43", "1"]]},
  {name: "eink.vgl_dio.cathode", pads: [["D4", "1"], ["C33", "2"], ["D5", "2"]]},
  {name: "rgb1.red_res.a", pads: [["R14", "1"], ["D6", "3"]]},
  {name: "rgb1.green_res.a", pads: [["R15", "1"], ["D6", "4"]]},
  {name: "rgb1.blue_res.a", pads: [["R16", "1"], ["D6", "1"]]},
  {name: "rgb2.red_res.a", pads: [["R17", "1"], ["D7", "3"]]},
  {name: "rgb2.green_res.a", pads: [["R18", "1"], ["D7", "4"]]},
  {name: "rgb2.blue_res.a", pads: [["R19", "1"], ["D7", "1"]]},
  {name: "rgb3.red_res.a", pads: [["R20", "1"], ["D8", "3"]]},
  {name: "rgb3.green_res.a", pads: [["R21", "1"], ["D8", "4"]]},
  {name: "rgb3.blue_res.a", pads: [["R22", "1"], ["D8", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.6070866141732285, 2.6814960629921263);
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


