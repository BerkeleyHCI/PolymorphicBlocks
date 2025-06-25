const board = new PCB();

// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.146, 2.762), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.185, 2.762), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.146, 2.801), rotate: 0,
  id: 'H3'
})
// mcu
const U1 = board.add(Freenove_ESP32S3_WROOM_Expansion, {
  translate: pt(0.160, 1.960), rotate: 0,
  id: 'U1'
})
// tp_gnd.tp
const TP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.976, 2.799), rotate: 0,
  id: 'TP1'
})
// tp_usb.tp
const TP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.477, 2.799), rotate: 0,
  id: 'TP2'
})
// tp_3v3.tp
const TP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.226, 2.799), rotate: 0,
  id: 'TP3'
})
// reg_12v.ic
const U2 = board.add(SOT_23_5, {
  translate: pt(1.467, 2.363), rotate: 0,
  id: 'U2'
})
// reg_12v.fb.div.top_res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(1.444, 2.615), rotate: 0,
  id: 'R1'
})
// reg_12v.fb.div.bottom_res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(1.600, 2.615), rotate: 0,
  id: 'R2'
})
// reg_12v.power_path.inductor
const L1 = board.add(L_1210_3225Metric, {
  translate: pt(1.676, 2.359), rotate: 0,
  id: 'L1'
})
// reg_12v.power_path.in_cap.cap
const C1 = board.add(C_0805_2012Metric, {
  translate: pt(1.453, 2.508), rotate: 0,
  id: 'C1'
})
// reg_12v.power_path.out_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(1.626, 2.508), rotate: 0,
  id: 'C2'
})
// reg_12v.rect
const D1 = board.add(D_SOD_323, {
  translate: pt(1.796, 2.507), rotate: 0,
  id: 'D1'
})
// tp_12v.tp
const TP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.727, 2.799), rotate: 0,
  id: 'TP4'
})
// mic.ic
const U3 = board.add(Knowles_LGA_5_3_5x2_65mm, {
  translate: pt(1.448, 2.841), rotate: 0,
  id: 'U3'
})
// mic.pwr_cap.cap
const C3 = board.add(C_0603_1608Metric, {
  translate: pt(1.444, 2.987), rotate: 0,
  id: 'C3'
})
// photodiode.r
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(3.848, 2.542), rotate: 0,
  id: 'R3'
})
// photodiode.pd
const D2 = board.add(Osram_BPW34S_SMD, {
  translate: pt(3.947, 2.385), rotate: 0,
  id: 'D2'
})
// oled22.device.conn
const J1 = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(1.715, 1.577), rotate: 0,
  id: 'J1'
})
// oled22.lcd
const U4 = board.add(Lcd_Er_Oled022_1_Outline, {
  translate: pt(2.580, 0.607), rotate: 0,
  id: 'U4'
})
// oled22.iref_res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(2.736, 1.413), rotate: 0,
  id: 'R4'
})
// oled22.vcomh_cap.cap
const C4 = board.add(C_1206_3216Metric, {
  translate: pt(2.202, 1.430), rotate: 0,
  id: 'C4'
})
// oled22.vdd_cap1.cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(2.892, 1.413), rotate: 0,
  id: 'C5'
})
// oled22.vdd_cap2.cap
const C6 = board.add(C_0805_2012Metric, {
  translate: pt(2.398, 1.423), rotate: 0,
  id: 'C6'
})
// oled22.vcc_cap1.cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(3.048, 1.413), rotate: 0,
  id: 'C7'
})
// oled22.vcc_cap2.cap
const C8 = board.add(C_0805_2012Metric, {
  translate: pt(2.572, 1.423), rotate: 0,
  id: 'C8'
})
// oled_rst.ic
const U5 = board.add(SOT_23, {
  translate: pt(2.716, 2.829), rotate: 0,
  id: 'U5'
})
// oled_pull.res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(3.970, 2.791), rotate: 0,
  id: 'R5'
})
// spk_drv.ic
const U6 = board.add(Maxim_WLP_9_1_595x1_415_Layout3x3_P0_4mm_Ball0_27mm_Pad0_25mm_NSMD, {
  translate: pt(1.699, 2.829), rotate: 0,
  id: 'U6'
})
// spk_drv.pwr_cap0.cap
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(1.860, 2.964), rotate: 0,
  id: 'C9'
})
// spk_drv.pwr_cap1.cap
const C10 = board.add(C_0805_2012Metric, {
  translate: pt(1.695, 2.974), rotate: 0,
  id: 'C10'
})
// spk.conn
const J2 = board.add(PinHeader_1x02_P2_54mm_Horizontal, {
  translate: pt(2.107, 2.933), rotate: 0,
  id: 'J2'
})
// servo[0].conn
const J3 = board.add(PinHeader_1x03_P2_54mm_Horizontal, {
  translate: pt(2.048, 2.566), rotate: 0,
  id: 'J3'
})
// servo[1].conn
const J4 = board.add(PinHeader_1x03_P2_54mm_Horizontal, {
  translate: pt(2.652, 2.566), rotate: 0,
  id: 'J4'
})
// ws2812bArray.led[0]
const D3 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.405), rotate: 0,
  id: 'D3'
})
// ws2812bArray.led[1]
const D4 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.405), rotate: 0,
  id: 'D4'
})
// ws2812bArray.led[2]
const D5 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.405), rotate: 0,
  id: 'D5'
})
// ws2812bArray.led[3]
const D6 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.405), rotate: 0,
  id: 'D6'
})
// ws2812bArray.led[4]
const D7 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.661), rotate: 0,
  id: 'D7'
})
// ws2812bArray.led[5]
const D8 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.661), rotate: 0,
  id: 'D8'
})
// ws2812bArray.led[6]
const D9 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.661), rotate: 0,
  id: 'D9'
})
// ws2812bArray.led[7]
const D10 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.661), rotate: 0,
  id: 'D10'
})
// ws2812bArray.led[8]
const D11 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.917), rotate: 0,
  id: 'D11'
})
// ws2812bArray.led[9]
const D12 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.917), rotate: 0,
  id: 'D12'
})
// ws2812bArray.led[10]
const D13 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.917), rotate: 0,
  id: 'D13'
})
// ws2812bArray.led[11]
const D14 = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.917), rotate: 0,
  id: 'D14'
})
// extNeopixels.conn
const J5 = board.add(PinHeader_1x03_P2_54mm_Horizontal, {
  translate: pt(3.256, 2.566), rotate: 0,
  id: 'J5'
})

board.setNetlist([
  {name: "gnd", pads: [["U1", "21"], ["U5", "1"], ["TP1", "1"], ["U2", "2"], ["U3", "3"], ["D2", "2"], ["U6", "C2"], ["J3", "3"], ["J4", "3"], ["D3", "3"], ["D4", "3"], ["D5", "3"], ["D6", "3"], ["D7", "3"], ["D8", "3"], ["D9", "3"], ["D10", "3"], ["D11", "3"], ["D12", "3"], ["D13", "3"], ["D14", "3"], ["J5", "3"], ["U3", "2"], ["R4", "2"], ["C3", "2"], ["J1", "3"], ["J1", "1"], ["J1", "24"], ["J1", "2"], ["J1", "12"], ["J1", "11"], ["J1", "16"], ["J1", "17"], ["J1", "18"], ["J1", "19"], ["J1", "20"], ["C4", "2"], ["C5", "2"], ["C6", "2"], ["C7", "2"], ["C8", "2"], ["C9", "2"], ["C10", "2"], ["R2", "2"], ["J1", "7"], ["J1", "10"], ["J1", "8"], ["C1", "2"], ["C2", "2"]]},
  {name: "vusb", pads: [["U1", "20"], ["TP2", "1"], ["U2", "5"], ["U6", "A1"], ["U6", "A2"], ["J3", "2"], ["J4", "2"], ["D3", "1"], ["D4", "1"], ["D5", "1"], ["D6", "1"], ["D7", "1"], ["D8", "1"], ["D9", "1"], ["D10", "1"], ["D11", "1"], ["D12", "1"], ["D13", "1"], ["D14", "1"], ["J5", "1"], ["U2", "4"], ["C9", "1"], ["C10", "1"], ["L1", "1"], ["C1", "1"]]},
  {name: "v3v3", pads: [["U1", "1"], ["U5", "3"], ["TP3", "1"], ["U3", "5"], ["R3", "1"], ["R5", "1"], ["C3", "1"], ["J1", "5"], ["C5", "1"], ["C6", "1"], ["J1", "6"]]},
  {name: "v12", pads: [["TP4", "1"], ["D1", "1"], ["R1", "1"], ["C2", "1"], ["J1", "23"], ["C7", "1"], ["C8", "1"]]},
  {name: "mic.clk", pads: [["U3", "4"], ["U1", "12"]]},
  {name: "mic.data", pads: [["U3", "1"], ["U1", "19"]]},
  {name: "photodiode.out", pads: [["U1", "38"], ["R3", "2"], ["D2", "1"]]},
  {name: "oled22.i2c.scl", pads: [["U1", "4"], ["J1", "13"]]},
  {name: "oled22.i2c.sda", pads: [["U1", "3"], ["J1", "14"], ["J1", "15"]]},
  {name: "oled_rst.nreset", pads: [["U5", "2"], ["R5", "2"], ["J1", "9"]]},
  {name: "spk_drv.i2s.sck", pads: [["U1", "35"], ["U6", "C1"]]},
  {name: "spk_drv.i2s.ws", pads: [["U1", "37"], ["U6", "C3"]]},
  {name: "spk_drv.i2s.sd", pads: [["U1", "36"], ["U6", "B1"]]},
  {name: "spk_drv.out.a", pads: [["U6", "A3"], ["J2", "1"]]},
  {name: "spk_drv.out.b", pads: [["U6", "B3"], ["J2", "2"]]},
  {name: "servo[0].pwm", pads: [["U1", "25"], ["J3", "1"]]},
  {name: "servo[1].pwm", pads: [["U1", "24"], ["J4", "1"]]},
  {name: "ws2812bArray.din", pads: [["U1", "26"], ["D3", "4"]]},
  {name: "ws2812bArray.dout", pads: [["D14", "2"], ["J5", "2"]]},
  {name: "reg_12v.fb.output", pads: [["U2", "3"], ["R1", "2"], ["R2", "1"]]},
  {name: "reg_12v.power_path.switch", pads: [["U2", "1"], ["L1", "2"], ["D1", "2"]]},
  {name: "oled22.iref_res.a", pads: [["R4", "1"], ["J1", "21"]]},
  {name: "oled22.device.vcomh", pads: [["J1", "22"], ["C4", "1"]]},
  {name: "ws2812bArray.led[0].dout", pads: [["D3", "2"], ["D4", "4"]]},
  {name: "ws2812bArray.led[1].dout", pads: [["D4", "2"], ["D5", "4"]]},
  {name: "ws2812bArray.led[2].dout", pads: [["D5", "2"], ["D6", "4"]]},
  {name: "ws2812bArray.led[3].dout", pads: [["D6", "2"], ["D7", "4"]]},
  {name: "ws2812bArray.led[4].dout", pads: [["D7", "2"], ["D8", "4"]]},
  {name: "ws2812bArray.led[5].dout", pads: [["D8", "2"], ["D9", "4"]]},
  {name: "ws2812bArray.led[6].dout", pads: [["D9", "2"], ["D10", "4"]]},
  {name: "ws2812bArray.led[7].dout", pads: [["D10", "2"], ["D11", "4"]]},
  {name: "ws2812bArray.led[8].dout", pads: [["D11", "2"], ["D12", "4"]]},
  {name: "ws2812bArray.led[9].dout", pads: [["D12", "2"], ["D13", "4"]]},
  {name: "ws2812bArray.led[10].dout", pads: [["D13", "2"], ["D14", "4"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.303543307086614, 3.142913385826772);
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


