const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.670, 1.198), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.709, 1.198), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.670, 1.237), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_uart_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.857, 0.165), rotate: 0,
  id: 'usb_uart_conn'
})
const usb_uart_cc_pull_cc1_res = board.add(R_0402_1005Metric, {
  translate: pt(1.142, 0.019), rotate: 0,
  id: 'usb_uart_cc_pull_cc1_res'
})
const usb_uart_cc_pull_cc2_res = board.add(R_0402_1005Metric, {
  translate: pt(1.142, 0.095), rotate: 0,
  id: 'usb_uart_cc_pull_cc2_res'
})
const vusb_protect_diode = board.add(D_SOD_323, {
  translate: pt(0.298, 1.235), rotate: 0,
  id: 'vusb_protect_diode'
})
const usbconv_ic = board.add(QFN_28_1EP_5x5mm_P0_5mm_EP3_35x3_35mm, {
  translate: pt(0.850, 0.881), rotate: 0,
  id: 'usbconv_ic'
})
const usbconv_regin_cap0_cap = board.add(C_0402_1005Metric, {
  translate: pt(1.047, 0.778), rotate: 0,
  id: 'usbconv_regin_cap0_cap'
})
const usbconv_regin_cap1_cap = board.add(C_0402_1005Metric, {
  translate: pt(1.047, 0.853), rotate: 0,
  id: 'usbconv_regin_cap1_cap'
})
const usbconv_vdd_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(1.047, 0.929), rotate: 0,
  id: 'usbconv_vdd_cap_cap'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(0.555, 1.265), rotate: 0,
  id: 'usb_esd'
})
const reg_3v3_ic = board.add(SOT_23_5, {
  translate: pt(0.445, 0.826), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.574, 0.951), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.431, 0.971), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const out_conn = board.add(PinHeader_2x03_P2_54mm_EdgeInline, {
  translate: pt(0.159, 0.321), rotate: 0,
  id: 'out_conn'
})
const auto_q_en = board.add(SOT_323_SC_70, {
  translate: pt(0.067, 0.811), rotate: 0,
  id: 'auto_q_en'
})
const auto_q_boot = board.add(SOT_323_SC_70, {
  translate: pt(0.067, 0.952), rotate: 0,
  id: 'auto_q_boot'
})
const auto_dtr_res = board.add(R_0402_1005Metric, {
  translate: pt(0.210, 0.920), rotate: 0,
  id: 'auto_dtr_res'
})
const auto_rts_res = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.061), rotate: 0,
  id: 'auto_rts_res'
})
const led_package = board.add(LED_0603_1608Metric, {
  translate: pt(1.259, 0.788), rotate: 0,
  id: 'led_package'
})
const led_res = board.add(R_0402_1005Metric, {
  translate: pt(1.237, 0.875), rotate: 0,
  id: 'led_res'
})
const led_en_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 1.227), rotate: 0,
  id: 'led_en_package'
})
const led_en_res = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.314), rotate: 0,
  id: 'led_en_res'
})

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


