/*
@version: v0.1.0

a basic starter design
*/

/* -- DECLARE_PCB -- */
const board = new PCB();

/* -- DECLARE_COMPONENTS -- */
const ws2812b = footprint({"1":{"pos":[-0.09645669291338584,0.06496062992125984],"shape":"M -0.02952755905511811 0.017716535433070866 L 0.02952755905511811 0.017716535433070866 L 0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 0.017716535433070866 ","layers":["F.Cu","F.Paste","F.Mask"]},"2":{"pos":[-0.09645669291338584,-0.06496062992125984],"shape":"M -0.02952755905511811 0.017716535433070866 L 0.02952755905511811 0.017716535433070866 L 0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 0.017716535433070866 ","layers":["F.Cu","F.Paste","F.Mask"]},"3":{"pos":[0.09645669291338584,-0.06496062992125984],"shape":"M -0.02952755905511811 0.017716535433070866 L 0.02952755905511811 0.017716535433070866 L 0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 0.017716535433070866 ","layers":["F.Cu","F.Paste","F.Mask"]},"4":{"pos":[0.09645669291338584,0.06496062992125984],"shape":"M -0.02952755905511811 0.017716535433070866 L 0.02952755905511811 0.017716535433070866 L 0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 -0.017716535433070866 L -0.02952755905511811 0.017716535433070866 ","layers":["F.Cu","F.Paste","F.Mask"]}});
const sk6812_ec15 = footprint({"1":{"pos":[-0.017716535433070866,0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"2":{"pos":[-0.017716535433070866,-0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"3":{"pos":[0.017716535433070866,-0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"4":{"pos":[0.017716535433070866,0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]}});

const ledFootprint = sk6812_ec15
const ledGndPad = "4"
const ledVinPad = "2"
const ledDinPad = "1"
const ledDoutPad = "3"

const degToRad = Math.PI / 180  // multiply by degrees to get radians
const mmToUnits = 1 / 25.4  // multiply by mm to get svgpcb units

// GEOMETRY PARAMETERS
const ledCount = 18
const ledRadius = 12.5  // mm
const ledStartAngle = 90 - (360/ledCount / 2)
const ledEndAngle = ledStartAngle + -360 * (ledCount - 1) / (ledCount)  // end angle is the placement of the last LED
const ledRot = 0  // rotation of each unit

// ROUTING PARAMETERS
const powerWidth = 0.5  // mm, trace
const powerHeightOffset = 1.25
const powerEscapeOffset = 0.5  // distance from center

const traceWidth = 0.2  // mm, trace
const traceSpacing = 0.2  // mm, clearance
const routingOffset = 2.0  // mm, distance from part center where we route everything


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

function createRadialLeds(count, rot, radius, startAngle, endAngle, prefix) {
  const incrAngle = (endAngle - startAngle) / (count - 1)

  var prevPower = null
  var prevData = null

  for (i=0; i<count; i++) {
    const angle = startAngle + incrAngle * i
    const origin = [Math.cos(angle * degToRad) * radius * mmToUnits,
                    Math.sin(angle * degToRad) * radius * mmToUnits]
    const led = board.add(ledFootprint, { translate: origin,
                                         rotate: angle + rot,
                                         label: prefix + "[" + i + "]" })

    dataInPoint = pAdd(origin, vRotate([-routingOffset * mmToUnits, 0], angle - 90))
    board.wire(path(
      ...smoothPath(dataInPoint, led.pad(ledDinPad),
                    angle + 90,
                    angle + 90)
      ), traceWidth * mmToUnits)
    if (prevData != null) {
      board.wire(path(
        ...smoothPath(prevData, dataInPoint,
                      angle - incrAngle + 90,
                      angle + 90)
        ), traceWidth * mmToUnits)
    }

    dataOutPoint = pAdd(origin, vRotate([routingOffset * mmToUnits, 0], angle - 90))
    board.wire(path(
      ...smoothPath(led.pad(ledDoutPad), dataOutPoint,
                    angle + 90,
                    angle + 90),
      ), traceWidth * mmToUnits)
    prevData = dataOutPoint

    powerRoutingHeight = traceWidth / 2 + traceSpacing + powerWidth / 2

    powerInPoint = pAdd(origin, vRotate([-routingOffset * mmToUnits, -powerRoutingHeight * mmToUnits], angle - 90))
    if (prevPower != null) {
      board.wire(path(
        ...smoothPath(prevPower, powerInPoint,
                      angle - incrAngle + 90,
                      angle + 90),
        ), powerWidth * mmToUnits)
    }

    powerInEscapePoint = pAdd(origin, vRotate([-powerEscapeOffset * mmToUnits, -powerHeightOffset * mmToUnits], angle - 90))
    powerOutEscapePoint = pAdd(origin, vRotate([powerEscapeOffset * mmToUnits, -powerHeightOffset * mmToUnits], angle - 90))
    powerOutPoint = pAdd(origin, vRotate([routingOffset * mmToUnits, -powerRoutingHeight * mmToUnits], angle - 90))
    board.wire(path(
        ...smoothPath(powerOutEscapePoint, led.pad(ledVinPad),
                      angle + 90,
                      angle),
        ), powerWidth * mmToUnits)
    board.wire(path(
        ...smoothPath(powerInPoint, powerInEscapePoint,
                      angle + 90,
                      angle + 90),
        powerOutEscapePoint,
        ...smoothPath(powerOutEscapePoint, powerOutPoint,
                    angle + 90,
                    angle + 90),
        ), powerWidth * mmToUnits)
    prevPower = powerOutPoint
  }
}

// PARTS
board.add(via(0.5 * mmToUnits, 0.9 * mmToUnits), {translate: [0, 0]})  // origin for positioning handle

createRadialLeds(ledCount, ledRot, ledRadius, ledStartAngle, ledEndAngle, "led")

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
