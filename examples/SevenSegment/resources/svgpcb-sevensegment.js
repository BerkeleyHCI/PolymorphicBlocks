/* 
@version: v0.1.0

a basic starter design 
*/

/* -- DECLARE_PCB -- */
const board = new PCB();

/* -- DECLARE_COMPONENTS -- */
const sk6812_ec15 = footprint({"1":{"pos":[-0.017716535433070866,0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"2":{"pos":[-0.017716535433070866,-0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"3":{"pos":[0.017716535433070866,-0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"4":{"pos":[0.017716535433070866,0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]}});

/* -- 7-segment parameters -- */
digitSpacing = 47.35 / 25.4
groupSpacing = 83.5 / 25.4
outerSpacing = 178 / 25.4
const digitCenters = [  // point at center of segment F
  pt(-outerSpacing/2, 0),
  pt(-groupSpacing/2, 0),
  pt(groupSpacing/2, 0),
  pt(outerSpacing/2, 0),
]

// GEOMETRY PARAMETERS
// using segment conventions from https://en.wikipedia.org/wiki/Seven-segment_display#/media/File:7_Segment_Display_with_Labeled_Segments.svg
const segmentLeds = 2  // LEDs per segment

const slope = 0.15  // slope of segments F, B, E, C, in mm x distance per-mm of y

const xPitch = 31 / 25.4  // space between segments F and B, E and C
const yPitch = 33.2 / 25.4  // space between segments A and G, G and D
// note, top pitch is ~33.5, bottom pitch is ~32.8
const xLength = 21 / 25.4  // length of segments A, G, D
const yLength = 23 / 25.4  // length of segments F, B, E, C

const colonPitch = 27.8 / 25.4
const metaXPitch = 23 / 25.4
const metaYPitch = 43.2 / 25.4

// MECHANICAL PARAMETERS
const outlineWidth = 8 / 25.4  // width of each segment for board outline purposes
const outlineJoinerWidth = 58 / 25.4  // width of the joiner (horizontal joiner between 7-segments) for outline purposes

const colonBossDia = 8 / 25.4

const mountingHolePitch = 44.5 / 25.4
const mountingHole = via(4.5 / 25.4, 0 / 25.4)

// ELECTRICAL PARAMETERS
const prefix = "D"

const silkWidth = 0.1 / 25.4
const traceWidth = 0.2 / 25.4
const traceVia = via(0.3 / 25.4, 0.7 / 25.4)

const traceCornerFilet = 2 / 25.4
const ledViaOffset = 1 / 25.4
const traceParallelOffset = 2 / 25.4


// Vector helpers
function pAdd(pt1, delta) {  // adds two points
  return pt1.map((e,i) => e + delta[i])
}

function pDiff(pos, neg) {  // return the difference between two points
  return pos.map((e,i) => e - neg[i])
}

function pCenter(pt1, pt2) {  // returns the midpoint
  return pt1.map((e,i) => (e + pt2[i]) / 2)
}

function vScale(v, scale) {  // returns a vector scaled by some factor
  return v.map((e,i) => (e  * scale))
}

function vProject(v, ref) {  // returns the projection of v onto a reference vector
  const aDotb = v[0]*ref[0] + v[1]*ref[1]
  const bDotb = ref[0]*ref[0] + ref[1]*ref[1]
  return vScale(ref, aDotb / bDotb)
}

function smoothPath(pt1, pt2, pt1Slope, pt2Slope=null) {  // return the path(...) components for a curve between two points, with entry and exit slope
  if (pt2Slope == null) {
    pt2Slope = pt1Slope
  } 
  const center = pCenter(pt1, pt2)
  const pt1Projection = vProject(pDiff(pt2, pt1), pt1Slope)
  const pt2Projection = vProject(pDiff(pt2, pt1), pt2Slope)
  return [
    pt1,
    ["cubic",
     pAdd(pt1, vScale(pt1Projection, 0.33)),
     center,
     pDiff(pt2, vScale(pt2Projection, 0.33)),
    ],
    pt2
  ]
}

function degToVector(deg, len=1) {  // given a slope in degrees, convert it to a vector
  return [Math.cos(deg * Math.PI / 180) * len, Math.sin(deg * Math.PI / 180) * len]
}


/* -- ADD_COMPONENTS -- */

function createLed(pt, rot, name) {  // creates a LED with associated routing, and returns it
  const led = board.add(sk6812_ec15, { translate: pt, rotate: rot, label: name })
  const gndViaPos = pAdd(led.pad("4"), degToVector(rot, ledViaOffset))
  board.wire([
    led.pad("4"), gndViaPos
  ], traceWidth)
  board.add(traceVia, {translate: gndViaPos})
  return led
}

// creates a line of LEDs for the segment between p1 and p2, for an array of led names
// returns the array of created LEDs
function generateSegment(pt1, pt2, rot, names) {
  output = []
  board.wire([pt1, pt2], silkWidth, "F.SilkS")
  dist = Math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)

  diff = pDiff(pt2, pt1)
  incr = [diff[0] / names.length, diff[1] / names.length]
  halfIncr = [incr[0] / 2, incr[1] / 2]
  curr = [pt1[0] + incr[0] / 2, pt1[1] + incr[1] / 2]

  const wirePoints = []

  // create LEDs and add points to the list
  names.forEach(function (name, i) {
    const led = createLed(curr, rot, name)
    output.push(led)
    wirePoints.push(led.pad("1"))
    wirePoints.push(led.pad("3"))

    curr = pAdd(curr, incr)
  })

  // wire up points
  board.wire(path(
    ...smoothPath(pt1, wirePoints[0], diff, degToVector(rot))
  ), traceWidth)
  for (i=1; i<wirePoints.length - 1; i+=2) {
    board.wire(path(
      ...smoothPath(wirePoints[i], wirePoints[i+1], degToVector(rot))
    ), traceWidth)
  }
  board.wire(path(
    ...smoothPath(wirePoints[wirePoints.length - 1], pt2, degToVector(rot), diff)
  ), traceWidth)
  
  return output
}

// Applies center-offset and slope correction to a (relative) vector, in a coordinate system where Y=0 is no slope
function segPt(center, pt) {
  return pAdd(center, [pt[0] + pt[1] * slope, pt[1]])
}

function createNames(prefix, count, startIndex) {
  output = []
  for (var i=0; i<count; i++) {
    output.push(prefix + (startIndex + i))
  }
  return output
}

const yMargin = (yPitch - yLength) / 2

var ledNum = 0
for (digitCenter of digitCenters) {
  const a1 = segPt(digitCenter, [-xLength/2, yPitch])
  const a2 = segPt(digitCenter, [xLength/2, yPitch])
  const segA = generateSegment(a1, a2,
           0, createNames(prefix, segmentLeds, ledNum + 0*segmentLeds))

  const b1 = segPt(digitCenter, [xPitch/2, yLength + yMargin])
  const b2 = segPt(digitCenter, [xPitch/2, yMargin])
  board.wire(path(
    a2,
    ["fillet", traceCornerFilet, segPt(digitCenter, [xPitch/2, yPitch])],
    b1
  ), traceWidth)
  const segB = generateSegment(b1, b2, 
           -90, createNames(prefix, segmentLeds, ledNum + 1*segmentLeds))
  board.add(traceVia, {translate: b2})

  const c1 = segPt(digitCenter, [xPitch/2, - yMargin])
  const c2 = segPt(digitCenter, [xPitch/2, -yMargin - yLength])
  board.wire([
    b2, c1
  ], traceWidth, "B.Cu")
  board.add(traceVia, {translate: c1})
  const segC = generateSegment(c1, c2, 
           -90, createNames(prefix, segmentLeds, ledNum + 2*segmentLeds))

  const d1 = segPt(digitCenter, [xLength/2, -yPitch])
  const d2 = segPt(digitCenter, [-xLength/2, -yPitch])
  board.wire(path(
    c2,
    ["fillet", traceCornerFilet, segPt(digitCenter, [xPitch/2, -yPitch])],
    d1
  ), traceWidth)
  const segD = generateSegment(d1, d2,
           180, createNames(prefix, segmentLeds, ledNum + 3*segmentLeds))

  const e1 = segPt(digitCenter, [-xPitch/2, -yMargin - yLength])
  const e2 = segPt(digitCenter, [-xPitch/2, -yMargin])
  board.wire(path(
    d2,
    ["fillet", traceCornerFilet, segPt(digitCenter, [-xPitch/2, -yPitch])],
    e1
  ), traceWidth)
  const segE = generateSegment(e1, e2, 
           90, createNames(prefix, segmentLeds, ledNum + 4*segmentLeds))
  board.add(traceVia, {translate: e2})
  
  const f1 = segPt(digitCenter, [-xPitch/2, yMargin])
  const f2 = segPt(digitCenter, [-xPitch/2, yMargin + yLength])
  board.wire([
    e2, f1
  ], traceWidth, "B.Cu")
  board.add(traceVia, {translate: f1})
  const segF = generateSegment(f1, f2, 
           90, createNames(prefix, segmentLeds, ledNum + 5*segmentLeds))

  // outer parallel trace segment for prev g2 -> a1
  const f2o = segPt(f2, [-traceParallelOffset, 0])
  const f1o = segPt(f1, [-traceParallelOffset, -traceParallelOffset])
  const p2o = segPt(digitCenter, [-xPitch / 2 - (xPitch - xLength)/2, 0])
  board.add(traceVia, {translate: p2o})
  board.wire(path(
    p2o,
    ["fillet", traceCornerFilet, segPt(digitCenter, [-xPitch/2 - traceParallelOffset, 0])],
    f1o,
  ), traceWidth, "B.Cu")
  board.add(traceVia, {translate: f1o})
  board.wire([
    f1o, f2o
  ], traceWidth)
  board.wire(path(
    ...smoothPath(f2o, segPt(f2, [0, traceParallelOffset*2]), [slope, 1]),
    ["fillet", traceCornerFilet, segPt(digitCenter, [-xPitch/2, yPitch])],
    a1
  ), traceWidth)

  // inner parallel trace segment for f2 -> g1
  const f2i = segPt(f2, [traceParallelOffset, 0])
  const f1i = segPt(f1, [traceParallelOffset, -traceParallelOffset])
  board.wire(path(
    f2,
    ["fillet", traceCornerFilet, segPt(f2, [0, traceParallelOffset / 2])],
    segPt(f2, [traceParallelOffset / 2, traceParallelOffset / 2]),
    ["fillet", traceCornerFilet, segPt(f2, [traceParallelOffset, traceParallelOffset / 2])],
    f2i
  ), traceWidth)
  board.wire([
    f2i, f1i
  ], traceWidth)
  board.add(traceVia, {translate: f1i})

  const g1 = segPt(digitCenter, [-xLength/2, 0])
  const g2 = segPt(digitCenter, [xLength/2, 0])
  board.wire(path(
    f1i,
    ["fillet", traceCornerFilet, segPt(digitCenter, [-xPitch/2 + traceParallelOffset, 0])],
    g1
  ), traceWidth, "B.Cu")
  board.add(traceVia, {translate: g1})
  const segG = generateSegment(g1, g2, 
           0, createNames(prefix, segmentLeds, ledNum + 6*segmentLeds))
  board.add(traceVia, {translate: g2})
  
  ledNum = ledNum + 7*segmentLeds
}

const c1 = createLed(segPt([0, 0], [0, colonPitch/2]), -90, "C1")
const c2 = createLed(segPt([0, 0], [0, -colonPitch/2]), -90, "C2")

const m1 = createLed(segPt([0, 0], [-metaXPitch/2, metaYPitch/2]), 0, "M1")
const m2 = createLed(segPt([0, 0], [metaXPitch/2, metaYPitch/2]), 0, "M2")

const my = createLed(segPt([0, 0], [-metaXPitch/2, -metaYPitch/2]), 0, "My")  // opaque
const m4 = createLed(segPt([0, 0], [metaXPitch/2, -metaYPitch/2]), 0, "M4")


// Generate mounting holes between left and right groups of digits
for (i=0; i<digitCenters.length - 1; i+=2) {
  const center = pCenter(digitCenters[i], digitCenters[i+1])
  board.add(mountingHole, {translate: segPt(center, [0, mountingHolePitch/2])})
  board.add(mountingHole, {translate: segPt(center, [0, -mountingHolePitch/2])})
}


// Generate outline
for (digitCenter of digitCenters) {
  board.wire([  // top outline
    segPt(digitCenter, [-xPitch/2 - outlineWidth/2, outlineJoinerWidth/2]),
    segPt(digitCenter, [-xPitch/2 - outlineWidth/2, yMargin + yLength + outlineWidth/4]),  // /4 is arbitrary to make it line up
    segPt(digitCenter, [-xLength/2 - outlineWidth/4, yPitch + outlineWidth/2]),
    segPt(digitCenter, [xLength/2 + outlineWidth/4, yPitch + outlineWidth/2]),
    segPt(digitCenter, [xPitch/2 + outlineWidth/2, yMargin + yLength + outlineWidth/4]),
    segPt(digitCenter, [xPitch/2 + outlineWidth/2, outlineJoinerWidth/2]),
  ], traceWidth, "Edge.Cuts")

  board.wire([  // bottom outline
    segPt(digitCenter, [-xPitch/2 - outlineWidth/2, -outlineJoinerWidth/2]),
    segPt(digitCenter, [-xPitch/2 - outlineWidth/2, -yMargin - yLength - outlineWidth/4]),
    segPt(digitCenter, [-xLength/2 - outlineWidth/4, -yPitch - outlineWidth/2]),
    segPt(digitCenter, [xLength/2 + outlineWidth/4, -yPitch - outlineWidth/2]),
    segPt(digitCenter, [xPitch/2 + outlineWidth/2, -yMargin - yLength - outlineWidth/4]),
    segPt(digitCenter, [xPitch/2 + outlineWidth/2, -outlineJoinerWidth/2]),
  ], traceWidth, "Edge.Cuts")
  
  board.wire([  // top cutout
    segPt(digitCenter, [-xPitch/2 + outlineWidth/2, yPitch - outlineWidth/2]),  // A
    segPt(digitCenter, [xPitch/2 - outlineWidth/2, yPitch - outlineWidth/2]),  // A2
    segPt(digitCenter, [xPitch/2 - outlineWidth/2, outlineWidth/2]),  // B2
    segPt(digitCenter, [-xPitch/2 + outlineWidth/2, outlineWidth/2]),  // G1
    segPt(digitCenter, [-xPitch/2 + outlineWidth/2, yPitch - outlineWidth/2]),
  ], traceWidth, "Edge.Cuts")
  
  board.wire([  // bottom cutout
    segPt(digitCenter, [-xPitch/2 + outlineWidth/2, -outlineWidth/2]),
    segPt(digitCenter, [xPitch/2 - outlineWidth/2, -outlineWidth/2]),
    segPt(digitCenter, [xPitch/2 - outlineWidth/2, -yPitch + outlineWidth/2]),
    segPt(digitCenter, [-xPitch/2 + outlineWidth/2, -yPitch + outlineWidth/2]),
    segPt(digitCenter, [-xPitch/2 + outlineWidth/2, -outlineWidth/2]),
  ], traceWidth, "Edge.Cuts")
}

board.wire([  // left closure
  segPt(digitCenters[0], [-xPitch/2 - outlineWidth/2, outlineJoinerWidth/2]),
  segPt(digitCenters[0], [-xPitch/2 - outlineWidth/2, -outlineJoinerWidth/2]),
], traceWidth, "Edge.Cuts")
for (i=0; i<digitCenters.length - 1; i++) {
  board.wire([  // top joiner
    segPt(digitCenters[i], [xPitch/2 + outlineWidth/2, outlineJoinerWidth/2]),
    segPt(digitCenters[i+1], [-xPitch/2 - outlineWidth/2, outlineJoinerWidth/2]),
  ], traceWidth, "Edge.Cuts")
  board.wire([  // bottom joiner
    segPt(digitCenters[i], [xPitch/2 + outlineWidth/2, -outlineJoinerWidth/2]),
    segPt(digitCenters[i+1], [-xPitch/2 - outlineWidth/2, -outlineJoinerWidth/2]),
  ], traceWidth, "Edge.Cuts")
}
board.wire([  // right closure
  segPt(digitCenters[digitCenters.length-1], [xPitch/2 + outlineWidth/2, outlineJoinerWidth/2]),
  segPt(digitCenters[digitCenters.length-1], [xPitch/2 + outlineWidth/2, -outlineJoinerWidth/2]),
], traceWidth, "Edge.Cuts")


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

