const board = new PCB();

// bat.cell[0]
const U1 = board.add(BatteryHolder_Keystone_2460_1xAA, {
  translate: pt(0.108, 0.343), rotate: 0,
  id: 'U1'
})
// bat.cell[1]
const U2 = board.add(BatteryHolder_Keystone_2460_1xAA, {
  translate: pt(0.108, 1.067), rotate: 0,
  id: 'U2'
})
// bat.cell[2]
const U3 = board.add(BatteryHolder_Keystone_2460_1xAA, {
  translate: pt(0.108, 1.791), rotate: 0,
  id: 'U3'
})
// bat.cell[3]
const U4 = board.add(BatteryHolder_Keystone_2460_1xAA, {
  translate: pt(0.108, 2.516), rotate: 0,
  id: 'U4'
})
// mcu
const U5 = board.add(XIAO_RP2040_SMD, {
  translate: pt(2.730, 0.410), rotate: 0,
  id: 'U5'
})
// led.package
const D1 = board.add(LED_0603_1608Metric, {
  translate: pt(3.180, 0.029), rotate: 0,
  id: 'D1'
})
// led.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(3.180, 0.126), rotate: 0,
  id: 'R1'
})

board.setNetlist([
  {name: "mcu.pwr_vin", pads: [["U4", "1"]]},
  {name: "mcu.gnd", pads: [["U5", "13"], ["U1", "2"], ["R1", "2"]]},
  {name: "led.signal", pads: [["U5", "7"], ["D1", "2"]]},
  {name: "bat.cell[0].pwr", pads: [["U1", "1"], ["U2", "2"]]},
  {name: "bat.cell[1].pwr", pads: [["U2", "1"], ["U3", "2"]]},
  {name: "bat.cell[2].pwr", pads: [["U3", "1"], ["U4", "2"]]},
  {name: "mcu.pwr_out", pads: [["U5", "12"]]},
  {name: "mcu.vusb_out", pads: [["U5", "14"]]},
  {name: "led.res.a", pads: [["R1", "1"], ["D1", "1"]]}
])

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


