/* 
@version: v0.1.0

a basic starter design 
*/

/* -- DECLARE_PCB -- */
const board = new PCB();

/* -- DECLARE_COMPONENTS -- */
const sk6812_ec15 = footprint({"1":{"pos":[-0.017716535433070866,0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"2":{"pos":[-0.017716535433070866,-0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"3":{"pos":[0.017716535433070866,-0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"4":{"pos":[0.017716535433070866,0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]}});

/* -- 7-segment parameters -- */
// using segment conventions from https://en.wikipedia.org/wiki/Seven-segment_display#/media/File:7_Segment_Display_with_Labeled_Segments.svg
const xPitch = 31 / 25.4  // space between segments F and B, E and C
const yPitch = 33.2 / 25.4  // space between segments A and G, G and D
// note, top pitch is ~33.5, bottom pitch is ~32.8
const xLength = 21 / 25.4  // length of segments A, G, D
const yLength = 23 / 25.4  // length of segments F, B, E, C

const slope = 0.15  // slope of segments F, B, E, C, in mm x distance per-mm of y

const segmentLeds = 2  // LEDs per segment

digitSpacing = 47.35 / 25.4
const digitCenters = [  // point at center of segment F
  pt(-digitSpacing*2, 0),
  pt(-digitSpacing*1, 0),
  pt(digitSpacing*1, 0),
  pt(digitSpacing*2, 0),
]

/* -- ADD_COMPONENTS -- */

// creates a line of LEDs for the segment between p1 and p2, for an array of led names
// returns the array of created LEDs
function drawLine(p1, p2, rot, names) {
  output = []
  board.wire(path(p1, p2), 0.01, "F.SilkS")
  dist = Math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

  diff = [p2[0]-p1[0], p2[1]-p1[1]]
  incr = [diff[0] / names.length, diff[1] / names.length]
  curr = [p1[0] + incr[0] / 2, p1[1] + incr[1] / 2]

  var lastLed = null
  names.forEach(function (name, i) {
    const led = board.add(sk6812_ec15, { translate: curr, rotate: rot, label: name })
    curr = pAdd(curr, incr)
    output.push(led)

    if (lastLed != null) {
      board.wire(path(lastLed.pad("3"), led.pad("1")), 0.01)
    }
    lastLed = led
  });
  
  return output
}

// Adds two points
function pAdd(pt1, delta) {
  return pt1.map((e,i) => e + delta[i])
}

// Applies slope correction to a point, in a coordinate system where Y=0 is no slope
function pSlope(pt) {
  return [pt[0] + pt[1] * slope, pt[1]]
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
  prefix = "D"

  const segA = drawLine(pAdd(digitCenter, pSlope([-xLength/2, yPitch])), pAdd(digitCenter, pSlope([xLength/2, yPitch])), 
           0, createNames(prefix, segmentLeds, ledNum + 0*segmentLeds))
  const segB = drawLine(pAdd(digitCenter, pSlope([xPitch/2, yLength + yMargin])), pAdd(digitCenter, pSlope([xPitch/2, yMargin])), 
           -90, createNames(prefix, segmentLeds, ledNum + 1*segmentLeds))
  const segC = drawLine(pAdd(digitCenter, pSlope([xPitch/2, - yMargin])), pAdd(digitCenter, pSlope([xPitch/2, -yMargin - yLength])), 
           -90, createNames(prefix, segmentLeds, ledNum + 2*segmentLeds))
  const segD = drawLine(pAdd(digitCenter, pSlope([xLength/2, -yPitch])), pAdd(digitCenter, pSlope([-xLength/2, -yPitch])), 
           180, createNames(prefix, segmentLeds, ledNum + 3*segmentLeds))
  const segE = drawLine(pAdd(digitCenter, pSlope([-xPitch/2, -yMargin - yLength])), pAdd(digitCenter, pSlope([-xPitch/2, -yMargin])), 
           90, createNames(prefix, segmentLeds, ledNum + 4*segmentLeds))
  const segF = drawLine(pAdd(digitCenter, pSlope([-xPitch/2, yMargin])), pAdd(digitCenter, pSlope([-xPitch/2, yMargin + yLength])), 
           90, createNames(prefix, segmentLeds, ledNum + 5*segmentLeds))
  const segG = drawLine(pAdd(digitCenter, pSlope([-xLength/2, 0])), pAdd(digitCenter, pSlope([xLength/2, 0])), 
           180, createNames(prefix, segmentLeds, ledNum + 6*segmentLeds))
  ledNum = ledNum + 2
  
  console.log(digitCenter)

}




// board.wire(path( led.pad("4"), [0, 0.15], [-0.1, 0.15], [-0.15, 0.3], [-0.05, 0.3],), 0.01)

/* -- BOARD_SIZE_SHAPE -- */
const interior = path(
  [-0.5, 0.5],
  [0.5, 0.5],
  [0.5, -0.5],
  [-0.5, -0.5],
);

board.addShape("interior", interior);

/* -- ADD_WIRES -- */
board.wire(path(), 0.03);

/* -- RENDER_PCB -- */
const limit0 = pt(-0.55, -0.55);
const limit1 = pt(0.55, 0.55);
const xMin = Math.min(limit0[0], limit1[0]);
const xMax = Math.max(limit0[0], limit1[0]);
const yMin = Math.min(limit0[1], limit1[1]);
const yMax = Math.max(limit0[1], limit1[1]);

renderPCB({
  pcb: board,
  layerColors: {
    "interior": "#002d00ff",
    "B.Cu": "#ff4c007f",
    "F.Cu": "#ff8c00cc",
    "B.Mask": "#00000000",
    "F.Mask": "#00000000",
    "F.SilkS": "#80208080",
    "padLabels": "#ffff99e5",
    "componentLabels": "#00e5e5e5",
  },
  limits: {
    x: [xMin, xMax],
    y: [yMin, yMax]
  },
  mm_per_unit: 25.4
});

