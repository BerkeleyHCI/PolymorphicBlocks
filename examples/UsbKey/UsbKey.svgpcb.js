const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.728, 0.561), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.768, 0.561), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.728, 0.601), rotate: 0,
  id: 'jlc_th_th3'
})
const usb = board.add(USB_A_Pads, {
  translate: pt(0.630, 0.463), rotate: 0,
  id: 'usb'
})
const reg_3v3_ic = board.add(UDFN_4_1EP_1x1mm_P0_65mm_EP0_48x0_48mm, {
  translate: pt(0.339, 0.591), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.340, 0.678), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const mcu_swd_conn = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(0.138, 0.365), rotate: 0,
  id: 'mcu_swd_conn'
})
const mcu_ic = board.add(QFN_32_1EP_5x5mm_P0_5mm_EP3_45x3_45mm, {
  translate: pt(0.123, 0.123), rotate: 0,
  id: 'mcu_ic'
})
const rgb_package = board.add(LED_Lumex_SML_LX0404SIUPGUSB, {
  translate: pt(0.035, 0.597), rotate: 0,
  id: 'rgb_package'
})
const rgb_red_res = board.add(R_0402_1005Metric, {
  translate: pt(0.147, 0.580), rotate: 0,
  id: 'rgb_red_res'
})
const rgb_green_res = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 0.690), rotate: 0,
  id: 'rgb_green_res'
})
const rgb_blue_res = board.add(R_0402_1005Metric, {
  translate: pt(0.149, 0.690), rotate: 0,
  id: 'rgb_blue_res'
})
const ts1_res = board.add(R_0402_1005Metric, {
  translate: pt(0.922, 0.580), rotate: 0,
  id: 'ts1_res'
})
const ts2_res = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 0.845), rotate: 0,
  id: 'ts2_res'
})
const tss_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.417, 0.845), rotate: 0,
  id: 'tss_cap'
})
const packed_mcu_vdda_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.227, 0.845), rotate: 0,
  id: 'packed_mcu_vdda_cap_cap'
})
const packed_mcu_vdd1_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.552, 0.590), rotate: 0,
  id: 'packed_mcu_vdd1_cap_cap'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.0771653543307087, 0.9818897637795276);
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


