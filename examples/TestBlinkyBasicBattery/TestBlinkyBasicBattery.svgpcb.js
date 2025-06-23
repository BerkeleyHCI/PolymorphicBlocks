const board = new PCB();

const bat_cell_0_ = board.add(BatteryHolder_Keystone_2460_1xAA, {
  translate: pt(0.108, 0.343), rotate: 0,
  id: 'bat_cell_0_'
})
const bat_cell_1_ = board.add(BatteryHolder_Keystone_2460_1xAA, {
  translate: pt(0.108, 1.067), rotate: 0,
  id: 'bat_cell_1_'
})
const bat_cell_2_ = board.add(BatteryHolder_Keystone_2460_1xAA, {
  translate: pt(0.108, 1.791), rotate: 0,
  id: 'bat_cell_2_'
})
const bat_cell_3_ = board.add(BatteryHolder_Keystone_2460_1xAA, {
  translate: pt(0.108, 2.516), rotate: 0,
  id: 'bat_cell_3_'
})
const mcu = board.add(XIAO_RP2040_SMD, {
  translate: pt(2.730, 0.410), rotate: 0,
  id: 'mcu'
})
const led_package = board.add(LED_0603_1608Metric, {
  translate: pt(3.180, 0.029), rotate: 0,
  id: 'led_package'
})
const led_res = board.add(R_0603_1608Metric, {
  translate: pt(3.180, 0.126), rotate: 0,
  id: 'led_res'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.356102362204725, 2.9763779527559056);
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


