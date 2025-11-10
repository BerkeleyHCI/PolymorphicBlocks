const board = new PCB();

// led.package
const D1 = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 0.029), rotate: 0,
  id: 'D1'
})
// led.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 0.126), rotate: 0,
  id: 'R1'
})

board.setNetlist([
  {name: "led.signal", pads: [["D1", "2"]]},
  {name: "gnd.gnd", pads: [["R1", "2"]]},
  {name: "led.res.a", pads: [["R1", "1"], ["D1", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(0.23484251968503939, 0.27283464566929133);
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


