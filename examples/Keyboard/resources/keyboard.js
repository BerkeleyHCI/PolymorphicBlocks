// @version: v0.1.0
/* -- DECLARE_COMPONENTS -- */
const R_1206 = footprint({"1":{"shape":"M -0.032,0.034L 0.032,0.034L 0.032,-0.034L -0.032,-0.034L -0.032,0.034","pos":[-0.06,0],"layers":["F.Cu","F.Mask"],"index":1},"2":{"shape":"M -0.032,0.034L 0.032,0.034L 0.032,-0.034L -0.032,-0.034L -0.032,0.034","pos":[0.06,0],"layers":["F.Cu","F.Mask"],"index":2}});
const button_6mm = {"L1":{"shape":"M -0.04,0.03L 0.04,0.03L 0.04,-0.03L -0.04,-0.03L -0.04,0.03","pos":[-0.125,0.08],"layers":["F.Cu"],"index":1},"R1":{"shape":"M -0.04,0.03L 0.04,0.03L 0.04,-0.03L -0.04,-0.03L -0.04,0.03","pos":[-0.125,-0.08],"layers":["F.Cu"],"index":2},"R2":{"shape":"M -0.04,0.03L 0.04,0.03L 0.04,-0.03L -0.04,-0.03L -0.04,0.03","pos":[0.125,-0.08],"layers":["F.Cu"],"index":3},"L2":{"shape":"M -0.04,0.03L 0.04,0.03L 0.04,-0.03L -0.04,-0.03L -0.04,0.03","pos":[0.125,0.08],"layers":["F.Cu"],"index":4}}
// *** THIS LINE BREAKS - this was drag'n'drop from the KiCad footprint
// const SW_Hotswap_Kailh_MX_ddj = footprint({"1":{"pos":[-0.27893700787401576,0.1],"shape":"M -0.05019685039370078 -0.04429133858267716 L -0.050122085398682126 -0.04514590638615615 L -0.04990006211016687 -0.0459745085793586 L -0.049537526593427354 -0.04675196850393701 L -0.04904549430668788 -0.04745466343349675 L -0.04843891540200068 -0.04806124233818394 L -0.04773622047244094 -0.04855327462492341 L -0.04695876054786254 -0.048915810141662935 L -0.046130158354660084 -0.04913783343017819 L -0.0452755905511811 -0.049212598425196846 L 0.0452755905511811 -0.049212598425196846 L 0.046130158354660084 -0.04913783343017819 L 0.046958760547862535 -0.048915810141662935 L 0.04773622047244094 -0.04855327462492342 L 0.04843891540200068 -0.04806124233818394 L 0.04904549430668788 -0.04745466343349675 L 0.04953752659342735 -0.04675196850393701 L 0.04990006211016687 -0.04597450857935861 L 0.050122085398682126 -0.04514590638615615 L 0.05019685039370078 -0.04429133858267716 L 0.05019685039370078 0.04429133858267716 L 0.050122085398682126 0.04514590638615615 L 0.04990006211016687 0.0459745085793586 L 0.049537526593427354 0.04675196850393701 L 0.04904549430668788 0.04745466343349675 L 0.04843891540200068 0.04806124233818394 L 0.04773622047244094 0.04855327462492341 L 0.04695876054786254 0.048915810141662935 L 0.046130158354660084 0.04913783343017819 L 0.0452755905511811 0.049212598425196846 L -0.0452755905511811 0.049212598425196846 L -0.046130158354660084 0.04913783343017819 L -0.046958760547862535 0.048915810141662935 L -0.04773622047244094 0.04855327462492342 L -0.04843891540200068 0.04806124233818394 L -0.04904549430668788 0.04745466343349675 L -0.04953752659342735 0.04675196850393701 L -0.04990006211016687 0.04597450857935861 L -0.050122085398682126 0.04514590638615615 L -0.05019685039370078 0.04429133858267716 L -0.05019685039370078 -0.04429133858267716 ","layers":["B.Cu","B.Mask","B.Paste"]},"2":{"pos":[0.22999999999999998,0.2],"shape":"M -0.05019685039370078 -0.04429133858267716 L -0.050122085398682126 -0.04514590638615615 L -0.04990006211016687 -0.0459745085793586 L -0.049537526593427354 -0.04675196850393701 L -0.04904549430668788 -0.04745466343349675 L -0.04843891540200068 -0.04806124233818394 L -0.04773622047244094 -0.04855327462492341 L -0.04695876054786254 -0.048915810141662935 L -0.046130158354660084 -0.04913783343017819 L -0.0452755905511811 -0.049212598425196846 L 0.0452755905511811 -0.049212598425196846 L 0.046130158354660084 -0.04913783343017819 L 0.046958760547862535 -0.048915810141662935 L 0.04773622047244094 -0.04855327462492342 L 0.04843891540200068 -0.04806124233818394 L 0.04904549430668788 -0.04745466343349675 L 0.04953752659342735 -0.04675196850393701 L 0.04990006211016687 -0.04597450857935861 L 0.050122085398682126 -0.04514590638615615 L 0.05019685039370078 -0.04429133858267716 L 0.05019685039370078 0.04429133858267716 L 0.050122085398682126 0.04514590638615615 L 0.04990006211016687 0.0459745085793586 L 0.049537526593427354 0.04675196850393701 L 0.04904549430668788 0.04745466343349675 L 0.04843891540200068 0.04806124233818394 L 0.04773622047244094 0.04855327462492341 L 0.04695876054786254 0.048915810141662935 L 0.046130158354660084 0.04913783343017819 L 0.0452755905511811 0.049212598425196846 L -0.0452755905511811 0.049212598425196846 L -0.046130158354660084 0.04913783343017819 L -0.046958760547862535 0.048915810141662935 L -0.04773622047244094 0.04855327462492342 L -0.04843891540200068 0.04806124233818394 L -0.04904549430668788 0.04745466343349675 L -0.04953752659342735 0.04675196850393701 L -0.04990006211016687 0.04597450857935861 L -0.050122085398682126 0.04514590638615615 L -0.05019685039370078 0.04429133858267716 L -0.05019685039370078 -0.04429133858267716 ","layers":["B.Cu","B.Mask","B.Paste"]}});

// constants
const width = 1;
const height = 1;

const zero = 0  // fixes one axis degrees of freedom

let dimensionCtlPt = pt(0.35, -0.2)
let kXCount = Math.abs(Math.round(dimensionCtlPt[0] / 0.05))  // number of columns (x dimension)
let kYCount = Math.abs(Math.round(dimensionCtlPt[1] / 0.05))  // number of rows (y dimension)
let rowSpacingPt = pt(zero, 0.35)
let colSpacingPt = pt(0.65, 0.15)  // this also acts as the Y offset handle for col 1
const spacingOffsetX = colSpacingPt[0]
let spacingPts = [
  [0, 0],
  colSpacingPt,
  pt(spacingOffsetX * 2, 0.2),
  pt(spacingOffsetX * 3, 0.15),
  pt(spacingOffsetX * 4, 0.05),
  pt(spacingOffsetX * 5, 0),
  pt(spacingOffsetX * 6, 0)
]
  
let diodeOffset = pt(0.25, 0)
const diodeOffsetX = diodeOffset[0]  // fixes X degrees of freedom
const diodeOffsetY = diodeOffset[1]  // workaround to allow drag to work as expected
let diodeViaPt = pt(diodeOffsetX, diodeOffsetY+0.15)
let viaTemplate = via(0.02, 0.035)

let centerChannel = pt(0.05, zero)

let traceSize = 0.015

/* -- DECLARE_PCB -- */
let board = new PCB();

/* -- ADD_COMPONENTS -- */
allColWirePoints = []
for (let yIndex=0; yIndex < kYCount; yIndex++) {
  colWirePoints = []
  rowDiodeVias = []

  for (let xIndex=0; xIndex < kXCount; xIndex++) {
    index = yIndex * kXCount + xIndex + 1
    
    buttonPos = [colSpacingPt[0] * xIndex, spacingPts[xIndex][1] + rowSpacingPt[1] * yIndex]
    // *** COMPONENTS ADDED HERE - name doesn't show up
    button = board.add(button_6mm, { translate: buttonPos, rotate: 0, id: `switch[${xIndex}][${yIndex}]` })
    diodePos = [buttonPos[0] + diodeOffset[0], buttonPos[1] + diodeOffset[1]]
    // *** COMPONENTS ADDED HERE - name doesn't show up
    diode = board.add(R_1206, { translate: diodePos, rotate: 90, id: `diode[${xIndex}][${yIndex}]` })

    // create stub wire for button -> column common line
    colWirePoint = [centerChannel[0] + buttonPos[0], button.padY("L2")]
    board.wire([colWirePoint,
                button.pad("L2")
               ], traceSize, "F.Cu")
    colWirePoints.push(colWirePoint)

    // create wire for button -> diode
    board.wire([button.pad("R2"),
                ["chamfer", 0.02, [diode.padX(1), button.padY("R2")]],  // TODO needs to be parametric
                diode.pad(1)
               ], traceSize, "F.Cu")
    diodeViaPos = [diodePos[0] + diodeViaPt[0] - diodeOffset[0], diodePos[1] + diodeViaPt[1] - diodeOffset[1]]
    diodeVia = board.add(viaTemplate, {translate: diodeViaPos})
    board.wire([diode.pad(2), diodeVia.pos], traceSize)
    
    if (rowDiodeVias.length > 0) {
      board.wire([rowDiodeVias[rowDiodeVias.length - 1].pos, diodeVia.pos], traceSize, "B.Cu")      
    }
    rowDiodeVias.push(diodeVia)
  }
  allColWirePoints.push(colWirePoints)
}

// Inter-row wiring
for (let xIndex=0; xIndex < allColWirePoints[0].length; xIndex++) {
  board.wire([allColWirePoints[0][xIndex],
              allColWirePoints[allColWirePoints.length - 1][xIndex]
             ], traceSize, "F.Cu")
}


/* -- RENDER_PCB -- */
renderPCB({
  pcb: board,
  layerColors: {
/* "F.Mask": "#000000ff", */
 "B.Cu": "#ff4c007f",
 "F.Cu": "#ff8c00cc",
 "padLabels": "#ffff99e5",
},
  limits: {
    x: [-width/2, width/2],
    y: [-height/2, height/2]
  },
  mm_per_unit: 25.4
});