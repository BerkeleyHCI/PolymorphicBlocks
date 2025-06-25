const board = new PCB();

// jlc_th.th1
const UH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.670, 1.198), rotate: 0,
  id: 'UH1'
})
// jlc_th.th2
const UH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.709, 1.198), rotate: 0,
  id: 'UH2'
})
// jlc_th.th3
const UH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.670, 1.237), rotate: 0,
  id: 'UH3'
})
// usb_uart.conn
const UJ1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.857, 0.165), rotate: 0,
  id: 'UJ1'
})
// usb_uart.cc_pull.cc1.res
const UR1 = board.add(R_0402_1005Metric, {
  translate: pt(1.142, 0.019), rotate: 0,
  id: 'UR1'
})
// usb_uart.cc_pull.cc2.res
const UR2 = board.add(R_0402_1005Metric, {
  translate: pt(1.142, 0.095), rotate: 0,
  id: 'UR2'
})
// vusb_protect.diode
const UD1 = board.add(D_SOD_323, {
  translate: pt(0.298, 1.235), rotate: 0,
  id: 'UD1'
})
// usbconv.ic
const UU1 = board.add(QFN_28_1EP_5x5mm_P0_5mm_EP3_35x3_35mm, {
  translate: pt(0.850, 0.881), rotate: 0,
  id: 'UU1'
})
// usbconv.regin_cap0.cap
const UC1 = board.add(C_0402_1005Metric, {
  translate: pt(1.047, 0.778), rotate: 0,
  id: 'UC1'
})
// usbconv.regin_cap1.cap
const UC2 = board.add(C_0402_1005Metric, {
  translate: pt(1.047, 0.853), rotate: 0,
  id: 'UC2'
})
// usbconv.vdd_cap.cap
const UC3 = board.add(C_0402_1005Metric, {
  translate: pt(1.047, 0.929), rotate: 0,
  id: 'UC3'
})
// usb_esd
const UU2 = board.add(SOT_23, {
  translate: pt(0.555, 1.265), rotate: 0,
  id: 'UU2'
})
// reg_3v3.ic
const UU3 = board.add(SOT_23_5, {
  translate: pt(0.445, 0.826), rotate: 0,
  id: 'UU3'
})
// reg_3v3.in_cap.cap
const UC4 = board.add(C_0402_1005Metric, {
  translate: pt(0.574, 0.951), rotate: 0,
  id: 'UC4'
})
// reg_3v3.out_cap.cap
const UC5 = board.add(C_0805_2012Metric, {
  translate: pt(0.431, 0.971), rotate: 0,
  id: 'UC5'
})
// out.conn
const UJ2 = board.add(PinHeader_2x03_P2_54mm_EdgeInline, {
  translate: pt(0.159, 0.321), rotate: 0,
  id: 'UJ2'
})
// auto.q_en
const UQ1 = board.add(SOT_323_SC_70, {
  translate: pt(0.067, 0.811), rotate: 0,
  id: 'UQ1'
})
// auto.q_boot
const UQ2 = board.add(SOT_323_SC_70, {
  translate: pt(0.067, 0.952), rotate: 0,
  id: 'UQ2'
})
// auto.dtr_res
const UR3 = board.add(R_0402_1005Metric, {
  translate: pt(0.210, 0.920), rotate: 0,
  id: 'UR3'
})
// auto.rts_res
const UR4 = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.061), rotate: 0,
  id: 'UR4'
})
// led.package
const UD2 = board.add(LED_0603_1608Metric, {
  translate: pt(1.259, 0.788), rotate: 0,
  id: 'UD2'
})
// led.res
const UR5 = board.add(R_0402_1005Metric, {
  translate: pt(1.237, 0.875), rotate: 0,
  id: 'UR5'
})
// led_en.package
const UD3 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 1.227), rotate: 0,
  id: 'UD3'
})
// led_en.res
const UR6 = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.314), rotate: 0,
  id: 'UR6'
})

board.setNetlist([
  {name: "Uvusb", pads: [["UJ1", "A4"], ["UJ1", "B9"], ["UJ1", "B4"], ["UJ1", "A9"], ["UD1", "1"], ["UU1", "7"], ["UU1", "8"], ["UU3", "1"], ["UU3", "3"], ["UC1", "1"], ["UC2", "1"], ["UC4", "1"]]},
  {name: "Ugnd", pads: [["UU2", "3"], ["UJ1", "A1"], ["UJ1", "B12"], ["UJ1", "B1"], ["UJ1", "A12"], ["UD1", "2"], ["UU1", "3"], ["UU1", "29"], ["UU3", "2"], ["UJ2", "5"], ["UJ1", "S1"], ["UC1", "2"], ["UC2", "2"], ["UC3", "2"], ["UC4", "2"], ["UC5", "2"], ["UR1", "1"], ["UR2", "1"]]},
  {name: "Uv3v3", pads: [["UU3", "5"], ["UJ2", "1"], ["UD2", "2"], ["UD3", "2"], ["UC5", "1"]]},
  {name: "Uusb_chain_0.d_P", pads: [["UJ1", "A6"], ["UJ1", "B6"], ["UU2", "2"], ["UU1", "4"]]},
  {name: "Uusb_chain_0.d_N", pads: [["UJ1", "A7"], ["UJ1", "B7"], ["UU2", "1"], ["UU1", "5"]]},
  {name: "Uusbconv.uart.tx", pads: [["UU1", "26"], ["UJ2", "4"]]},
  {name: "Uusbconv.uart.rx", pads: [["UU1", "25"], ["UJ2", "3"]]},
  {name: "Uusbconv.dtr", pads: [["UU1", "28"], ["UR3", "1"], ["UQ2", "2"]]},
  {name: "Uusbconv.rts", pads: [["UU1", "24"], ["UR4", "1"], ["UQ1", "2"], ["UR6", "2"]]},
  {name: "Uauto.en", pads: [["UQ1", "3"], ["UJ2", "6"]]},
  {name: "Uauto.boot", pads: [["UQ2", "3"], ["UJ2", "2"]]},
  {name: "Uusbconv.suspend", pads: [["UU1", "12"], ["UR5", "2"]]},
  {name: "Uusb_uart.conn.cc.cc1", pads: [["UJ1", "A5"], ["UR1", "2"]]},
  {name: "Uusb_uart.conn.cc.cc2", pads: [["UJ1", "B5"], ["UR2", "2"]]},
  {name: "Uusbconv.nsuspend", pads: [["UU1", "11"]]},
  {name: "Uusbconv.ri", pads: [["UU1", "2"]]},
  {name: "Uusbconv.dcd", pads: [["UU1", "1"]]},
  {name: "Uusbconv.dsr", pads: [["UU1", "27"]]},
  {name: "Uusbconv.cts", pads: [["UU1", "23"]]},
  {name: "Uusbconv.ic.vdd", pads: [["UU1", "6"], ["UU1", "9"], ["UC3", "1"]]},
  {name: "Uauto.dtr_res.b", pads: [["UR3", "2"], ["UQ1", "1"]]},
  {name: "Uauto.rts_res.b", pads: [["UR4", "2"], ["UQ2", "1"]]},
  {name: "Uled.res.a", pads: [["UR5", "1"], ["UD2", "1"]]},
  {name: "Uled_en.res.a", pads: [["UR6", "1"], ["UD3", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.4356299212598427, 1.4503937007874017);
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


