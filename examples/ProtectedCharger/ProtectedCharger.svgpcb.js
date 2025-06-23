const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.501, 0.935), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.540, 0.935), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.501, 0.974), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 0.165), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 0.420), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 0.420), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const batt_conn = board.add(JST_PH_S2B_PH_K_1x02_P2_00mm_Horizontal, {
  translate: pt(0.633, 0.266), rotate: 0,
  id: 'batt_conn'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 0.972), rotate: 0,
  id: 'tp_gnd_tp'
})
const tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 0.972), rotate: 0,
  id: 'tp_tp'
})
const pmos_r1 = board.add(R_0603_1608Metric, {
  translate: pt(0.511, 0.769), rotate: 0,
  id: 'pmos_r1'
})
const pmos_r2 = board.add(R_0603_1608Metric, {
  translate: pt(0.667, 0.769), rotate: 0,
  id: 'pmos_r2'
})
const pmos_mp1 = board.add(SOT_23, {
  translate: pt(0.528, 0.633), rotate: 0,
  id: 'pmos_mp1'
})
const pmos_mp2 = board.add(SOT_23, {
  translate: pt(0.719, 0.633), rotate: 0,
  id: 'pmos_mp2'
})
const charger_ic = board.add(SOT_23_5, {
  translate: pt(0.081, 0.633), rotate: 0,
  id: 'charger_ic'
})
const charger_vdd_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.268, 0.605), rotate: 0,
  id: 'charger_vdd_cap_cap'
})
const charger_vbat_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 0.778), rotate: 0,
  id: 'charger_vbat_cap_cap'
})
const charger_prog_res = board.add(R_0603_1608Metric, {
  translate: pt(0.231, 0.769), rotate: 0,
  id: 'charger_prog_res'
})
const charge_led_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.971, 0.595), rotate: 0,
  id: 'charge_led_package'
})
const charge_led_res = board.add(R_0603_1608Metric, {
  translate: pt(0.971, 0.693), rotate: 0,
  id: 'charge_led_res'
})
const pmos_load_fet = board.add(SOT_23, {
  translate: pt(1.223, 0.633), rotate: 0,
  id: 'pmos_load_fet'
})
const pwr_pins = board.add(JST_PH_S3B_PH_K_1x03_P2_00mm_Horizontal, {
  translate: pt(1.023, 0.266), rotate: 0,
  id: 'pwr_pins'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.416732283464567, 1.1279527559055118);
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


