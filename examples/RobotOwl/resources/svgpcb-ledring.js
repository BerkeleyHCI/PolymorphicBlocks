/*
@version: v0.1.0

a basic starter design
*/

/* -- DECLARE_PCB -- */
const board = new PCB();

/* -- DECLARE_COMPONENTS -- */
const ws2812b = footprint({"1":{"pos":[-0.09645669291338584,0.06496062992125984],"shape":"M -0.02952755905511811 0.017716535433070866 L 0.02952755905511811 0.017716535433070866 L 0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 0.017716535433070866 ","layers":["F.Cu","F.Paste","F.Mask"]},"2":{"pos":[-0.09645669291338584,-0.06496062992125984],"shape":"M -0.02952755905511811 0.017716535433070866 L 0.02952755905511811 0.017716535433070866 L 0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 0.017716535433070866 ","layers":["F.Cu","F.Paste","F.Mask"]},"3":{"pos":[0.09645669291338584,-0.06496062992125984],"shape":"M -0.02952755905511811 0.017716535433070866 L 0.02952755905511811 0.017716535433070866 L 0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 0.017716535433070866 ","layers":["F.Cu","F.Paste","F.Mask"]},"4":{"pos":[0.09645669291338584,0.06496062992125984],"shape":"M -0.02952755905511811 0.017716535433070866 L 0.02952755905511811 0.017716535433070866 L 0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 0.017716535433070866 ","layers":["F.Cu","F.Paste","F.Mask"]}});
const sk6812_ec15 = footprint({"1":{"pos":[-0.017716535433070866,0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"2":{"pos":[-0.017716535433070866,-0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"3":{"pos":[0.017716535433070866,-0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"4":{"pos":[0.017716535433070866,0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]}});

const degToRad = Math.PI / 180  // multiply by degrees to get radians
const mmToUnits = 1 / 25.4  // multiply by mm to get svgpcb units

// GEOMETRY PARAMETERS
const ledCount = 12
const radius = 46  // mm
const ledStartAngle = 90 - 15
const ledEndAngle = ledStartAngle + -360 * (ledCount - 1) / (ledCount)  // end angle is the placement of the last LED
const ledRot = 90  // rotation of each unit

// ROUTING PARAMETERS
const powerWidth = 0.5  // mm, trace
const powerVia = via(0.5 / 25.4, 0.9/ 25.4)
const gndOffset = 2  // mm, distance from pad to via
const powerOffset = 1  // mm, distance from pad to power ring

const traceWidth = 0.2  // mm, trace


// HELPER FUNCTIONS
function pAdd(pt1, delta) {  // adds two points
  return pt1.map((e,i) => e + delta[i])
}

function pDiff(pos, neg) {  // return the difference between two points
  return pos.map((e,i) => e - neg[i])
}

function pCenter(pt1, pt2) {  // returns the midpoint
  return pt1.map((e,i) => (e + pt2[i]) / 2)
}

function vRotate(v, deg) {  // returns a vector rotated by some amount
  return [
    Math.cos(deg * degToRad) * v[0] - Math.sin(deg * degToRad) * v[1],
    Math.sin(deg * degToRad) * v[0] + Math.cos(deg * degToRad) * v[1],
  ]
}

function vScale(v, scale) {  // returns a vector scaled by some factor
  return v.map((e,i) => (e  * scale))
}

function vProject(v, ref) {  // returns the projection of v onto a reference vector
  const aDotb = v[0]*ref[0] + v[1]*ref[1]
  const bDotb = ref[0]*ref[0] + ref[1]*ref[1]
  return vScale(ref, aDotb / bDotb)
}

function smoothPath(pt1, pt2, pt1Angle, pt2Angle=null) {  // return the path(...) components for a curve between two points, with entry and exit slope
  function degToVector(deg, len=1) {  // given a slope in degrees, convert it to a vector
    return [Math.cos(deg * Math.PI / 180) * len, Math.sin(deg * Math.PI / 180) * len]
  }
  if (pt2Angle == null) {
    pt2Angle = pt1Angle
  }
  const pt1Projection = vProject(pDiff(pt2, pt1), degToVector(pt1Angle))
  const pt2Projection = vProject(pDiff(pt2, pt1), degToVector(pt2Angle))
  return [
    pt1,
    ["cubic",
     pAdd(pt1, vScale(pt1Projection, 0.33)),
     pCenter(pAdd(pt1, vScale(pt1Projection, 0.33)), pDiff(pt2, vScale(pt2Projection, 0.33))),
     pDiff(pt2, vScale(pt2Projection, 0.33)),
    ],
    pt2
  ]
}


// PARTS
board.add(powerVia, {translate: [0, 0]})  // origin for positioning handle

const ledIncrAngle = (ledEndAngle - ledStartAngle) / (ledCount - 1)

var prevPower = null
var prevData = null

for (i=0; i<ledCount; i++) {
  const ledAngle = ledStartAngle + ledIncrAngle * i
  const led = board.add(ws2812b, { translate: [Math.cos(ledAngle * degToRad) * radius * mmToUnits,
                                               Math.sin(ledAngle * degToRad) * radius * mmToUnits],
                                  rotate: ledAngle + ledRot, label: "led[" + i + "]" })

  const gndViaPos = pAdd(led.pad("3"), vRotate([-gndOffset * mmToUnits, 0], ledAngle - 90))
  const gndVia = board.add(powerVia, {translate: gndViaPos})
  board.wire([  // gnd trace + via
    led.pad("3"),
    gndViaPos
  ], powerWidth * mmToUnits)

  if (prevData != null) {
    board.wire(path(
      ...smoothPath(prevData, led.pad("4"),
                    ledAngle - ledIncrAngle + 90,
                    ledAngle + 90)
      ), traceWidth * mmToUnits)
  }
  prevData = led.pad("2")

  const powerOffsetPos = pAdd(led.pad("1"), vRotate([0, -powerOffset * mmToUnits], ledAngle - 90))
  board.wire([
    led.pad("1"),
    powerOffsetPos
  ], powerWidth * mmToUnits)
  if (prevPower != null) {
    board.wire(path(
      ...smoothPath(prevPower, powerOffsetPos,
                    ledAngle - ledIncrAngle + 90,
                    ledAngle + 90)
      ), powerWidth * mmToUnits)
  }
  prevPower = powerOffsetPos
}


/* -- RENDER_PCB -- */
renderPCB({
  pcb: board,
  layerColors: {
    "interior": "#002d00ff",
    "B.Cu": "#ff4c007f",
    "F.Cu": "#ff8c00cc",
    "B.Mask": "#00000000",
    "F.Mask": "#00000000",
    "F.SilkS": "#80208080",
    "Edge.Cuts": "#202020ff",
    "padLabels": "#ffff99e5",
    "componentLabels": "#00e5e5e5",
  },
  limits: {
    x: [-5, 5],
    y: [-2, 2]
  },
  mm_per_unit: 25.4
});
