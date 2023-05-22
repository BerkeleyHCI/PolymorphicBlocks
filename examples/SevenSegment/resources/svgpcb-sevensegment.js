/* 
@version: v0.1.0

a basic starter design 
*/

/* -- DECLARE_PCB -- */
const board = new PCB();

/* -- DECLARE_COMPONENTS -- */
const m2_5 = footprint({"1":{"pos":[0,0],"shape":"M 0.0610236220472441 0 L 0.060986448105496006 0.002129693696412461 L 0.060874971570973525 0.004256792689110009 L 0.06068932826066235 0.006378705435624523 L 0.06042974435233993 0.008492846712129978 L 0.060096536109012694 0.01059664076313945 L 0.05969010949359838 0.012687524439666416 L 0.05921095967432262 0.014762950322026968 L 0.05865967042143285 0.016820389823478298 L 0.0580369133959641 0.018857336270912146 L 0.05734344733142355 0.020871307958849863 L 0.05658011710939057 0.022859851173018253 L 0.05574785273015872 0.024820543179822456 L 0.054847668179673584 0.02675099517807362 L 0.05388066019414712 0.028648855209375226 L 0.052848006923853545 0.030511811023622045 L 0.051750966497734655 0.03233759289612077 L 0.05059087549056356 0.034123976392899914 L 0.0493691472945342 0.0358687850808399 L 0.048087270397260594 0.03756989317932167 L 0.046746806568284095 0.03922522815016283 L 0.045349388956297684 0.04083277322268623 L 0.04389672009940588 0.04239056985084432 L 0.04239056985084432 0.04389672009940587 L 0.04083277322268623 0.045349388956297684 L 0.039225228150162834 0.046746806568284095 L 0.03756989317932167 0.0480872703972606 L 0.0358687850808399 0.0493691472945342 L 0.03412397639289991 0.05059087549056357 L 0.03233759289612077 0.051750966497734655 L 0.030511811023622055 0.05284800692385354 L 0.02864885520937523 0.05388066019414711 L 0.026750995178073625 0.054847668179673584 L 0.024820543179822456 0.05574785273015872 L 0.02285985117301825 0.05658011710939057 L 0.02087130795884987 0.05734344733142354 L 0.01885733627091215 0.0580369133959641 L 0.016820389823478298 0.05865967042143285 L 0.014762950322026965 0.05921095967432262 L 0.012687524439666423 0.059690109493598376 L 0.010596640763139455 0.060096536109012694 L 0.00849284671212998 0.06042974435233993 L 0.006378705435624522 0.06068932826066235 L 0.004256792689110005 0.060874971570973525 L 0.0021296936964124674 0.060986448105496006 L 3.736619170626767e-18 0.0610236220472441 L -0.00212969369641246 0.060986448105496006 L -0.00425679268911001 0.060874971570973525 L -0.006378705435624528 0.06068932826066235 L -0.008492846712129973 0.06042974435233993 L -0.010596640763139448 0.060096536109012694 L -0.012687524439666416 0.05969010949359838 L -0.014762950322026971 0.05921095967432262 L -0.01682038982347829 0.05865967042143285 L -0.018857336270912142 0.058036913395964104 L -0.020871307958849863 0.05734344733142355 L -0.022859851173018256 0.05658011710939057 L -0.02482054317982246 0.05574785273015872 L -0.02675099517807363 0.05484766817967358 L -0.028648855209375233 0.05388066019414711 L -0.030511811023622035 0.052848006923853545 L -0.032337592896120766 0.05175096649773466 L -0.0341239763928999 0.05059087549056357 L -0.03586878508083989 0.0493691472945342 L -0.03756989317932167 0.0480872703972606 L -0.039225228150162834 0.046746806568284095 L -0.04083277322268623 0.045349388956297684 L -0.04239056985084433 0.04389672009940587 L -0.04389672009940588 0.042390569850844315 L -0.04534938895629767 0.04083277322268624 L -0.04674680656828409 0.03922522815016284 L -0.048087270397260594 0.037569893179321676 L -0.04936914729453419 0.035868785080839904 L -0.05059087549056356 0.034123976392899914 L -0.051750966497734655 0.03233759289612077 L -0.052848006923853545 0.030511811023622045 L -0.05388066019414712 0.02864885520937522 L -0.054847668179673584 0.026750995178073615 L -0.05574785273015871 0.02482054317982247 L -0.056580117109390565 0.022859851173018267 L -0.05734344733142354 0.020871307958849873 L -0.0580369133959641 0.018857336270912153 L -0.05865967042143285 0.0168203898234783 L -0.05921095967432262 0.014762950322026968 L -0.05969010949359838 0.012687524439666415 L -0.060096536109012694 0.010596640763139447 L -0.06042974435233993 0.008492846712129971 L -0.06068932826066235 0.006378705435624539 L -0.060874971570973525 0.004256792689110022 L -0.060986448105496006 0.0021296936964124713 L -0.0610236220472441 7.473238341253534e-18 L -0.060986448105496006 -0.0021296936964124566 L -0.060874971570973525 -0.0042567926891100075 L -0.06068932826066235 -0.0063787054356245244 L -0.06042974435233992 -0.008492846712129984 L -0.060096536109012694 -0.010596640763139459 L -0.059690109493598376 -0.012687524439666427 L -0.05921095967432262 -0.014762950322026954 L -0.05865967042143285 -0.016820389823478287 L -0.058036913395964104 -0.01885733627091214 L -0.05734344733142355 -0.02087130795884986 L -0.05658011710939057 -0.022859851173018253 L -0.05574785273015872 -0.024820543179822456 L -0.05484766817967358 -0.026750995178073625 L -0.05388066019414711 -0.02864885520937523 L -0.05284800692385354 -0.030511811023622055 L -0.05175096649773466 -0.032337592896120766 L -0.050590875490563576 -0.0341239763928999 L -0.049369147294534205 -0.03586878508083989 L -0.0480872703972606 -0.03756989317932166 L -0.046746806568284095 -0.03922522815016283 L -0.045349388956297684 -0.04083277322268623 L -0.04389672009940587 -0.04239056985084433 L -0.04239056985084432 -0.04389672009940588 L -0.040832773222686226 -0.04534938895629769 L -0.03922522815016284 -0.04674680656828409 L -0.037569893179321655 -0.0480872703972606 L -0.035868785080839904 -0.04936914729453419 L -0.034123976392899893 -0.050590875490563576 L -0.03233759289612078 -0.051750966497734655 L -0.030511811023622076 -0.052848006923853524 L -0.028648855209375223 -0.05388066019414712 L -0.026750995178073642 -0.05484766817967357 L -0.02482054317982245 -0.055747852730158726 L -0.02285985117301827 -0.056580117109390565 L -0.020871307958849852 -0.05734344733142355 L -0.018857336270912156 -0.0580369133959641 L -0.01682038982347828 -0.05865967042143286 L -0.014762950322026971 -0.05921095967432262 L -0.012687524439666444 -0.059690109493598376 L -0.01059664076313945 -0.060096536109012694 L -0.008492846712130001 -0.06042974435233992 L -0.006378705435624517 -0.060689328260662354 L -0.004256792689110026 -0.060874971570973525 L -0.0021296936964124483 -0.060986448105496006 L -1.12098575118803e-17 -0.0610236220472441 L 0.00212969369641248 -0.060986448105496006 L 0.004256792689110004 -0.06087497157097353 L 0.006378705435624493 -0.060689328260662354 L 0.00849284671212998 -0.06042974435233993 L 0.010596640763139428 -0.0600965361090127 L 0.012687524439666422 -0.059690109493598376 L 0.01476295032202695 -0.059210959674322626 L 0.016820389823478308 -0.058659670421432844 L 0.018857336270912135 -0.058036913395964104 L 0.02087130795884988 -0.05734344733142354 L 0.02285985117301825 -0.05658011710939057 L 0.024820543179822428 -0.05574785273015873 L 0.02675099517807362 -0.054847668179673584 L 0.028648855209375206 -0.053880660194147126 L 0.030511811023622055 -0.05284800692385354 L 0.03233759289612076 -0.05175096649773467 L 0.03412397639289992 -0.05059087549056356 L 0.035868785080839884 -0.049369147294534205 L 0.03756989317932168 -0.04808727039726059 L 0.03922522815016283 -0.0467468065682841 L 0.040832773222686206 -0.045349388956297705 L 0.04239056985084432 -0.04389672009940588 L 0.04389672009940586 -0.04239056985084434 L 0.045349388956297684 -0.040832773222686226 L 0.04674680656828408 -0.03922522815016285 L 0.0480872703972606 -0.03756989317932166 L 0.04936914729453419 -0.03586878508083991 L 0.050590875490563576 -0.034123976392899893 L 0.051750966497734655 -0.03233759289612078 L 0.052848006923853524 -0.030511811023622076 L 0.05388066019414711 -0.028648855209375226 L 0.05484766817967357 -0.026750995178073646 L 0.055747852730158726 -0.024820543179822453 L 0.056580117109390565 -0.022859851173018274 L 0.05734344733142355 -0.020871307958849856 L 0.0580369133959641 -0.018857336270912163 L 0.05865967042143285 -0.016820389823478284 L 0.05921095967432262 -0.014762950322026977 L 0.059690109493598376 -0.01268752443966645 L 0.060096536109012694 -0.010596640763139454 L 0.06042974435233992 -0.008492846712130004 L 0.06068932826066235 -0.00637870543562452 L 0.060874971570973525 -0.004256792689110029 L 0.060986448105496006 -0.002129693696412452 L 0.0610236220472441 0 ","layers":["F.Cu","B.Cu","F.Mask","B.Mask"],"drill":{"diameter":0.1062992125984252,"start":"F.Cu","end":"B.Cu","plated":true}}});
const sk6812_ec15 = footprint({"1":{"pos":[-0.017716535433070866,0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"2":{"pos":[-0.017716535433070866,-0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"3":{"pos":[0.017716535433070866,-0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]},"4":{"pos":[0.017716535433070866,0.017716535433070866],"shape":"M -0.00984251968503937 0.00984251968503937 L 0.00984251968503937 0.00984251968503937 L 0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 -0.00984251968503937 L -0.00984251968503937 0.00984251968503937 ","layers":["F.Cu","F.Paste","F.Mask"]}});
const skrtlae010 = footprint({"2":{"pos":[0,0.03543307086614173],"shape":"M -0.011811023622047244 0.03543307086614173 L 0.011811023622047244 0.03543307086614173 L 0.011811023622047244 -0.03543307086614173 L -0.011811023622047244 -0.03543307086614173 L -0.011811023622047244 0.03543307086614173 ","layers":["F.Cu","F.Paste","F.Mask"]},"1_1":{"pos":[0.04822834645669292,0.03543307086614173],"shape":"M -0.014763779527559055 0.03543307086614173 L 0.014763779527559055 0.03543307086614173 L 0.014763779527559055 -0.03543307086614173 L -0.014763779527559055 -0.03543307086614173 L -0.014763779527559055 0.03543307086614173 ","layers":["F.Cu","F.Paste","F.Mask"]},"1_2":{"pos":[-0.04822834645669292,0.03543307086614173],"shape":"M -0.014763779527559055 0.03543307086614173 L 0.014763779527559055 0.03543307086614173 L 0.014763779527559055 -0.03543307086614173 L -0.014763779527559055 -0.03543307086614173 L -0.014763779527559055 0.03543307086614173 ","layers":["F.Cu","F.Paste","F.Mask"]},"MP_1":{"pos":[-0.07283464566929135,-0.04133858267716536],"shape":"M -0.025590551181102362 0.017716535433070866 L 0.025590551181102362 0.017716535433070866 L 0.025590551181102362 -0.017716535433070866 L -0.025590551181102362 -0.017716535433070866 L -0.025590551181102362 0.017716535433070866 ","layers":["F.Cu","F.Paste","F.Mask"]},"MP_2":{"pos":[0.07283464566929135,-0.04133858267716536],"shape":"M -0.025590551181102362 0.017716535433070866 L 0.025590551181102362 0.017716535433070866 L 0.025590551181102362 -0.017716535433070866 L -0.025590551181102362 -0.017716535433070866 L -0.025590551181102362 0.017716535433070866 ","layers":["F.Cu","F.Paste","F.Mask"]}});

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


// Generate LED chain for segments
//
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


// Generate outline
//
var outlineElts = []
for (digitCenter of digitCenters) {  // outline closed-path for each segment
  const segmentOutline = geo.path([
    // upper segment
    segPt(digitCenter, [-xPitch/2 - outlineWidth/2, yMargin + yLength + outlineWidth/4]),  // /4 is arbitrary to make it line up
    segPt(digitCenter, [-xLength/2 - outlineWidth/4, yPitch + outlineWidth/2]),
    segPt(digitCenter, [xLength/2 + outlineWidth/4, yPitch + outlineWidth/2]),
    segPt(digitCenter, [xPitch/2 + outlineWidth/2, yMargin + yLength + outlineWidth/4]),
    // lower segment
    segPt(digitCenter, [xPitch/2 + outlineWidth/2, -yMargin - yLength - outlineWidth/4]),
    segPt(digitCenter, [xLength/2 + outlineWidth/4, -yPitch - outlineWidth/2]),
    segPt(digitCenter, [-xLength/2 - outlineWidth/4, -yPitch - outlineWidth/2]),
    segPt(digitCenter, [-xPitch/2 - outlineWidth/2, -yMargin - yLength - outlineWidth/4]),
  ])

  const segmentCutouts = geo.union(
    geo.path([  // upper cutout
      segPt(digitCenter, [-xPitch/2 + outlineWidth/2, yPitch - outlineWidth/2]),  // A
      segPt(digitCenter, [xPitch/2 - outlineWidth/2, yPitch - outlineWidth/2]),  // A2
      segPt(digitCenter, [xPitch/2 - outlineWidth/2, outlineWidth/2]),  // B2
      segPt(digitCenter, [-xPitch/2 + outlineWidth/2, outlineWidth/2]),  // G1
      // segPt(digitCenter, [-xPitch/2 + outlineWidth/2, yPitch - outlineWidth/2]),
    ]),
    geo.path([  // lower cutout
      segPt(digitCenter, [-xPitch/2 + outlineWidth/2, -outlineWidth/2]),
      segPt(digitCenter, [xPitch/2 - outlineWidth/2, -outlineWidth/2]),
      segPt(digitCenter, [xPitch/2 - outlineWidth/2, -yPitch + outlineWidth/2]),
      segPt(digitCenter, [-xPitch/2 + outlineWidth/2, -yPitch + outlineWidth/2]),
      // segPt(digitCenter, [-xPitch/2 + outlineWidth/2, -outlineWidth/2]),
    ])
  )
  
  const segmentWithCutout = geo.difference(segmentOutline, segmentCutouts)  
  outlineElts.push(segmentWithCutout)
}

for (i=0; i<digitCenters.length - 1; i++) {  // outline closed-path (joiner) between each segment
  const xDelta = outlineWidth / 4  // make the joiner overlap into the segment to avoid exact-intersection which seems to confuse the union algo
  const joiner = geo.path([
    segPt(digitCenters[i], [xPitch/2 + outlineWidth/2 - xDelta, outlineJoinerWidth/2]),
    segPt(digitCenters[i+1], [-xPitch/2 - outlineWidth/2 + xDelta, outlineJoinerWidth/2]),
    segPt(digitCenters[i+1], [-xPitch/2 - outlineWidth/2 + xDelta, -outlineJoinerWidth/2]),
    segPt(digitCenters[i], [xPitch/2 + outlineWidth/2 - xDelta, -outlineJoinerWidth/2]),
  ])
  outlineElts.push(joiner)
}

var unionOutline = outlineElts[0]
for (i=1; i<outlineElts.length; i++) {
  unionOutline = geo.union(unionOutline, outlineElts[i])
}

board.addShape("interior", unionOutline);


// Generate mechanical mounting holes
//
for (i=0; i<digitCenters.length - 1; i+=2) {  // clearance holes in left- and right-side joiners
  const center = pCenter(digitCenters[i], digitCenters[i+1])
  board.add(mountingHole, {translate: segPt(center, [0, mountingHolePitch/2])})
  board.add(mountingHole, {translate: segPt(center, [0, -mountingHolePitch/2])})
}

const mount1 = board.add(m2_5, { translate: [6.7 / 25.4, 20.5 / 25.5], label: "mount1" })
const mount2 = board.add(m2_5, { translate: [-9.6 / 25.4, -26.8 / 25.4], label: "mount2" })


// Generate switches
//
const switchPitch = 26.5/3 / 25.4

function createSwitch(pt, rot, name) {  // creates a switch with associated routing, and returns it; pt is the board outline intersection
  const sw = board.add(skrtlae010, { translate: pAdd(pt, degToVector(rot-90, 1.5 / 25.4)), rotate: rot + 180, label: name })
  for (gndPad of ["1_1", "1_2"]) {
     const gndVia1Pos = pAdd(sw.pad(gndPad), degToVector(rot - 90, ledViaOffset + 0.5 / 25.4))
    board.wire([
      sw.pad(gndPad), gndVia1Pos
    ], traceWidth)
    board.add(traceVia, {translate: gndVia1Pos})
  }
  return sw
}

for (i=0; i<4; i++) {
  const sw = createSwitch(segPt([0, 0], [(i - 1.5) * switchPitch, outlineJoinerWidth/2]), 0, "sw" + i)
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
