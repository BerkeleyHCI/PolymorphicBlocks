const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.518, 0.839), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.557, 0.839), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.518, 0.879), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_uart_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 0.165), rotate: 0,
  id: 'usb_uart_conn'
})
const usb_uart_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 0.420), rotate: 0,
  id: 'usb_uart_cc_pull_cc1_res'
})
const usb_uart_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 0.420), rotate: 0,
  id: 'usb_uart_cc_pull_cc2_res'
})
const vusb_protect_diode = board.add(D_SOD_323, {
  translate: pt(0.816, 0.604), rotate: 0,
  id: 'vusb_protect_diode'
})
const usbconv_ic = board.add(QFN_28_1EP_5x5mm_P0_5mm_EP3_35x3_35mm, {
  translate: pt(0.122, 0.689), rotate: 0,
  id: 'usbconv_ic'
})
const usbconv_regin_cap0_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.342, 0.595), rotate: 0,
  id: 'usbconv_regin_cap0_cap'
})
const usbconv_regin_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.342, 0.692), rotate: 0,
  id: 'usbconv_regin_cap1_cap'
})
const usbconv_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.879), rotate: 0,
  id: 'usbconv_vdd_cap_cap'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(1.073, 0.633), rotate: 0,
  id: 'usb_esd'
})
const led_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.577, 0.595), rotate: 0,
  id: 'led_package'
})
const led_res = board.add(R_0603_1608Metric, {
  translate: pt(0.576, 0.693), rotate: 0,
  id: 'led_res'
})
const reg_3v3_ic = board.add(SOT_23_5, {
  translate: pt(0.878, 0.067), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.855, 0.332), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(0.887, 0.219), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const out_conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.608, 0.370), rotate: 0,
  id: 'out_conn'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.187992125984252, 1.0255905511811025);
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


