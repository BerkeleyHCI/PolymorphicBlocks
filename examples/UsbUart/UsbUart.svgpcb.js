const board = new PCB();

// jlc_th.th1
const UH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.997, 0.559), rotate: 0,
  id: 'UH1'
})
// jlc_th.th2
const UH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.037, 0.559), rotate: 0,
  id: 'UH2'
})
// jlc_th.th3
const UH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.997, 0.598), rotate: 0,
  id: 'UH3'
})
// usb_uart.conn
const UJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.769, 0.165), rotate: 0,
  id: 'UJ1'
})
// usb_uart.esd
const UU1 = board.add(SOT_23, {
  translate: pt(1.093, 0.067), rotate: 0,
  id: 'UU1'
})
// usb_uart.cc_pull.cc1
const UR1 = board.add(R_0603_1608Metric, {
  translate: pt(1.076, 0.202), rotate: 0,
  id: 'UR1'
})
// usb_uart.cc_pull.cc2
const UR2 = board.add(R_0603_1608Metric, {
  translate: pt(1.076, 0.299), rotate: 0,
  id: 'UR2'
})
// vusb_protect.diode
const UD1 = board.add(D_SOD_323, {
  translate: pt(0.816, 0.596), rotate: 0,
  id: 'UD1'
})
// usbconv.ic
const UU2 = board.add(QFN_28_1EP_5x5mm_P0_5mm_EP3_35x3_35mm, {
  translate: pt(0.122, 0.681), rotate: 0,
  id: 'UU2'
})
// usbconv.regin_cap0.cap
const UC1 = board.add(C_0603_1608Metric, {
  translate: pt(0.342, 0.588), rotate: 0,
  id: 'UC1'
})
// usbconv.regin_cap1.cap
const UC2 = board.add(C_0603_1608Metric, {
  translate: pt(0.342, 0.685), rotate: 0,
  id: 'UC2'
})
// usbconv.vdd_cap.cap
const UC3 = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.871), rotate: 0,
  id: 'UC3'
})
// led.package
const UD2 = board.add(LED_0603_1608Metric, {
  translate: pt(0.577, 0.588), rotate: 0,
  id: 'UD2'
})
// led.res
const UR3 = board.add(R_0603_1608Metric, {
  translate: pt(0.576, 0.685), rotate: 0,
  id: 'UR3'
})
// reg_3v3.ic
const UU3 = board.add(SOT_23_5, {
  translate: pt(0.341, 0.067), rotate: 0,
  id: 'UU3'
})
// reg_3v3.in_cap.cap
const UC4 = board.add(C_0603_1608Metric, {
  translate: pt(0.318, 0.332), rotate: 0,
  id: 'UC4'
})
// reg_3v3.out_cap.cap
const UC5 = board.add(C_1206_3216Metric, {
  translate: pt(0.350, 0.219), rotate: 0,
  id: 'UC5'
})
// out.conn
const UJ2 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.071, 0.370), rotate: 0,
  id: 'UJ2'
})

board.setNetlist([
  {name: "vusb", pads: [["UJ1", "A4"], ["UJ1", "A9"], ["UJ1", "B4"], ["UJ1", "B9"], ["UD1", "1"], ["UU2", "7"], ["UU2", "8"], ["UC1", "1"], ["UC2", "1"], ["UU3", "1"], ["UU3", "3"], ["UC4", "1"]]},
  {name: "gnd", pads: [["UJ1", "A1"], ["UJ1", "A12"], ["UJ1", "B1"], ["UJ1", "B12"], ["UJ1", "S1"], ["UU1", "3"], ["UR1", "1"], ["UR2", "1"], ["UD1", "2"], ["UU2", "29"], ["UU2", "3"], ["UC1", "2"], ["UC2", "2"], ["UC3", "2"], ["UR3", "2"], ["UU3", "2"], ["UC4", "2"], ["UC5", "2"], ["UJ2", "3"]]},
  {name: "v3v3", pads: [["UU3", "5"], ["UC5", "1"], ["UJ2", "4"]]},
  {name: "usb_uart.usb.dp", pads: [["UJ1", "A6"], ["UJ1", "B6"], ["UU1", "2"], ["UU2", "4"]]},
  {name: "usb_uart.usb.dm", pads: [["UJ1", "A7"], ["UJ1", "B7"], ["UU1", "1"], ["UU2", "5"]]},
  {name: "usb_uart.conn.cc.cc1", pads: [["UJ1", "A5"], ["UR1", "2"]]},
  {name: "usb_uart.conn.cc.cc2", pads: [["UJ1", "B5"], ["UR2", "2"]]},
  {name: "usbconv.suspend", pads: [["UU2", "12"]]},
  {name: "usbconv.nsuspend", pads: [["UU2", "11"], ["UD2", "2"]]},
  {name: "usbconv.uart.tx", pads: [["UU2", "26"], ["UJ2", "1"]]},
  {name: "usbconv.uart.rx", pads: [["UU2", "25"], ["UJ2", "2"]]},
  {name: "usbconv.ri", pads: [["UU2", "2"]]},
  {name: "usbconv.dcd", pads: [["UU2", "1"]]},
  {name: "usbconv.dtr", pads: [["UU2", "28"]]},
  {name: "usbconv.dsr", pads: [["UU2", "27"]]},
  {name: "usbconv.rts", pads: [["UU2", "24"]]},
  {name: "usbconv.cts", pads: [["UU2", "23"]]},
  {name: "usbconv.ic.vdd", pads: [["UU2", "6"], ["UU2", "9"], ["UC3", "1"]]},
  {name: "led.package.k", pads: [["UD2", "1"], ["UR3", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.2866141732283465, 1.0181102362204726);
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


