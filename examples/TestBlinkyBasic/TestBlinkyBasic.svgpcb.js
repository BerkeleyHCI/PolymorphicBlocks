const board = new PCB();

// mcu.device
const U1 = board.add(XIAO_RP2040_SMD, {
  translate: pt(0.348, 0.410), rotate: 0,
  id: 'U1'
})
// led.package
const D1 = board.add(LED_0603_1608Metric, {
  translate: pt(0.877, 0.029), rotate: 0,
  id: 'D1'
})
// led.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.876, 0.126), rotate: 0,
  id: 'R1'
})

board.setNetlist([
  {name: "mcu.gnd", pads: [["U1", "13"], ["R1", "2"]]},
  {name: "mcu.pwr_out", pads: [["U1", "12"]]},
  {name: "mcu.vusb_out", pads: [["U1", "14"]]},
  {name: "led.signal", pads: [["U1", "7"], ["D1", "2"]]},
  {name: "led.package.k", pads: [["D1", "1"], ["R1", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.0529527559055119, 0.9986220472440945);
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


