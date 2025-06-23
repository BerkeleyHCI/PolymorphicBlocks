const board = new PCB();

const rgb_knob = NeopixelArrayCircular_4_rgb_knob(pt(0, 0))
const rgb_ring = NeopixelArrayCircular_24_rgb_ring(pt(0, 0))
const rgb_sw = NeopixelArrayCircular_6_rgb_sw(pt(0, 0))
const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.095, 2.890), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.135, 2.890), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.095, 2.929), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.115, 1.905), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(0.964, 2.160), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(1.120, 2.160), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const tp_pwr_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.741, 2.927), rotate: 0,
  id: 'tp_pwr_tp'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.240, 2.927), rotate: 0,
  id: 'tp_gnd_tp'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(2.403, 1.882), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.461, 2.092), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.297, 2.102), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.486, 2.927), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(1.988, 2.927), rotate: 0,
  id: 'prot_3v3_diode'
})
const mcu_ic = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vcc_cap0_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.419), rotate: 0,
  id: 'mcu_vcc_cap0_cap'
})
const mcu_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.403), rotate: 0,
  id: 'mcu_vcc_cap1_cap'
})
const mcu_prog_conn = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(2.096, 0.167), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.403), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.533), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.763, 2.919), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.763, 3.015), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const i2c_tp_tp_scl_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.702, 2.585), rotate: 0,
  id: 'i2c_tp_tp_scl_tp'
})
const i2c_tp_tp_sda_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.702, 2.699), rotate: 0,
  id: 'i2c_tp_tp_sda_tp'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(2.980, 2.957), rotate: 0,
  id: 'usb_esd'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 2.919), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 3.016), rotate: 0,
  id: 'ledr_res'
})
const ledy_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.293, 2.919), rotate: 0,
  id: 'ledy_package'
})
const ledy_res = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 3.016), rotate: 0,
  id: 'ledy_res'
})
const enc_package = board.add(RotaryEncoder_Alps_EC11J15_Switch, {
  translate: pt(0.394, 2.085), rotate: 0,
  id: 'enc_package'
})
const sw_0__package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(0.620, 2.659), rotate: 0,
  id: 'sw_0__package'
})
const sw_1__package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(3.957, 1.852), rotate: 0,
  id: 'sw_1__package'
})
const sw_2__package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.073, 2.659), rotate: 0,
  id: 'sw_2__package'
})
const sw_3__package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(0.167, 2.659), rotate: 0,
  id: 'sw_3__package'
})
const sw_4__package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.978, 2.659), rotate: 0,
  id: 'sw_4__package'
})
const sw_5__package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.526, 2.659), rotate: 0,
  id: 'sw_5__package'
})
const als_ic = board.add(HVSOF6, {
  translate: pt(3.956, 2.589), rotate: 0,
  id: 'als_ic'
})
const als_vcc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(4.122, 2.576), rotate: 0,
  id: 'als_vcc_cap_cap'
})
const als_dvi_res = board.add(R_0603_1608Metric, {
  translate: pt(3.945, 2.698), rotate: 0,
  id: 'als_dvi_res'
})
const als_dvi_cap = board.add(C_0603_1608Metric, {
  translate: pt(4.101, 2.698), rotate: 0,
  id: 'als_dvi_cap'
})
const dist_ic = board.add(ST_VL53L0X, {
  translate: pt(3.478, 1.798), rotate: 0,
  id: 'dist_ic'
})
const dist_vdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(3.613, 1.922), rotate: 0,
  id: 'dist_vdd_cap_0__cap'
})
const dist_vdd_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(3.449, 1.932), rotate: 0,
  id: 'dist_vdd_cap_1__cap'
})
const env_ic = board.add(Sensirion_DFN_4_1EP_2x2mm_P1mm_EP0_7x1_6mm, {
  translate: pt(3.459, 2.596), rotate: 0,
  id: 'env_ic'
})
const env_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.460, 2.714), rotate: 0,
  id: 'env_vdd_cap_cap'
})
const oled_device_conn = board.add(Hirose_FH12_30S_0_5SH_1x30_1MP_P0_50mm_Horizontal, {
  translate: pt(2.956, 1.054), rotate: 0,
  id: 'oled_device_conn'
})
const oled_lcd = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(3.066, 0.516), rotate: 0,
  id: 'oled_lcd'
})
const oled_c1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.815, 0.889), rotate: 0,
  id: 'oled_c1_cap'
})
const oled_c2_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.971, 0.889), rotate: 0,
  id: 'oled_c2_cap'
})
const oled_iref_res = board.add(R_0603_1608Metric, {
  translate: pt(3.469, 1.006), rotate: 0,
  id: 'oled_iref_res'
})
const oled_vcomh_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.477, 0.899), rotate: 0,
  id: 'oled_vcomh_cap_cap'
})
const oled_vdd_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.624, 1.006), rotate: 0,
  id: 'oled_vdd_cap1_cap'
})
const oled_vbat_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.780, 1.006), rotate: 0,
  id: 'oled_vbat_cap_cap'
})
const oled_vcc_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.650, 0.899), rotate: 0,
  id: 'oled_vcc_cap_cap'
})
const rgb_shift_ic = board.add(SOT_23_5, {
  translate: pt(3.183, 1.807), rotate: 0,
  id: 'rgb_shift_ic'
})
const rgb_shift_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.161, 1.942), rotate: 0,
  id: 'rgb_shift_vdd_cap_cap'
})
const rgb_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.490, 2.927), rotate: 0,
  id: 'rgb_tp_tp'
})
const io8_pur_res = board.add(R_0603_1608Metric, {
  translate: pt(2.728, 2.919), rotate: 0,
  id: 'io8_pur_res'
})
const spk_dac_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 2.919), rotate: 0,
  id: 'spk_dac_rc_r'
})
const spk_dac_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(0.528, 3.015), rotate: 0,
  id: 'spk_dac_rc_c'
})
const spk_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.235, 2.927), rotate: 0,
  id: 'spk_tp_tp'
})
const spk_drv_ic = board.add(MSOP_8_3x3mm_P0_65mm, {
  translate: pt(2.820, 1.809), rotate: 0,
  id: 'spk_drv_ic'
})
const spk_drv_pwr_cap0_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.926, 1.946), rotate: 0,
  id: 'spk_drv_pwr_cap0_cap'
})
const spk_drv_pwr_cap1_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.761, 1.956), rotate: 0,
  id: 'spk_drv_pwr_cap1_cap'
})
const spk_drv_inp_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.753, 2.063), rotate: 0,
  id: 'spk_drv_inp_cap'
})
const spk_drv_inn_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.909, 2.063), rotate: 0,
  id: 'spk_drv_inn_cap'
})
const spk_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.360, 2.677), rotate: 0,
  id: 'spk_conn'
})
const v5v_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.997, 2.919), rotate: 0,
  id: 'v5v_sense_div_top_res'
})
const v5v_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.997, 3.015), rotate: 0,
  id: 'v5v_sense_div_bottom_res'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.298425196850395, 3.162598425196851);
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

function NeopixelArrayCircular_4_rgb_knob(xy, rot=90, radius=1, startAngle=0, endAngle=360, powerRadiusOffset=0.2) {
  const kCount = 4

  // Global params
  const traceWidth = 0.015
  const powerWidth = 0.05
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {
    footprints: {},
    pts: {}
  }

  // Helper functions
  const degToRad = Math.PI / 180  // multiply by degrees to get radians
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

  const incrAngle = (endAngle - startAngle) / (kCount)

  var prevAngle = null
  var prevLed = null
  var prevGndOrigin = null
  var prevVinOrigin = null

  for (i=0; i<kCount; i++) {
    const angle = startAngle + incrAngle * i
    const origin = pAdd(xy, vRotate([radius, 0], angle))
    obj.footprints[`led[${i}]`] = led = board.add(LED_SK6812_EC15_1_5x1_5mm, {
      translate: origin,
      rotate: angle + rot,
      id: `rgb_knob_led_${i}_`
    })

    const gndOrigin = pAdd(xy, vRotate([radius - powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(gndOrigin, led.pad(4),
                    angle)
      ), powerWidth)

    const vinOrigin = pAdd(xy, vRotate([radius + powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(vinOrigin, led.pad(2),
                    angle)
      ), powerWidth)

    if (prevLed != null) {
      board.wire(path(
        ...smoothPath(prevLed.pad(3), led.pad(1),
                      prevAngle + 90, angle + 90)
        ), traceWidth)
      board.wire(path(
        ...smoothPath(prevGndOrigin, gndOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
      board.wire(path(
        ...smoothPath(prevVinOrigin, vinOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
    }

    prevAngle = angle
    prevLed = led
    prevVinOrigin = vinOrigin
    prevGndOrigin = gndOrigin
  }

  return obj
}

function NeopixelArrayCircular_24_rgb_ring(xy, rot=90, radius=1, startAngle=0, endAngle=360, powerRadiusOffset=0.2) {
  const kCount = 24

  // Global params
  const traceWidth = 0.015
  const powerWidth = 0.05
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {
    footprints: {},
    pts: {}
  }

  // Helper functions
  const degToRad = Math.PI / 180  // multiply by degrees to get radians
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

  const incrAngle = (endAngle - startAngle) / (kCount)

  var prevAngle = null
  var prevLed = null
  var prevGndOrigin = null
  var prevVinOrigin = null

  for (i=0; i<kCount; i++) {
    const angle = startAngle + incrAngle * i
    const origin = pAdd(xy, vRotate([radius, 0], angle))
    obj.footprints[`led[${i}]`] = led = board.add(LED_SK6812_EC15_1_5x1_5mm, {
      translate: origin,
      rotate: angle + rot,
      id: `rgb_ring_led_${i}_`
    })

    const gndOrigin = pAdd(xy, vRotate([radius - powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(gndOrigin, led.pad(4),
                    angle)
      ), powerWidth)

    const vinOrigin = pAdd(xy, vRotate([radius + powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(vinOrigin, led.pad(2),
                    angle)
      ), powerWidth)

    if (prevLed != null) {
      board.wire(path(
        ...smoothPath(prevLed.pad(3), led.pad(1),
                      prevAngle + 90, angle + 90)
        ), traceWidth)
      board.wire(path(
        ...smoothPath(prevGndOrigin, gndOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
      board.wire(path(
        ...smoothPath(prevVinOrigin, vinOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
    }

    prevAngle = angle
    prevLed = led
    prevVinOrigin = vinOrigin
    prevGndOrigin = gndOrigin
  }

  return obj
}

function NeopixelArrayCircular_6_rgb_sw(xy, rot=90, radius=1, startAngle=0, endAngle=360, powerRadiusOffset=0.2) {
  const kCount = 6

  // Global params
  const traceWidth = 0.015
  const powerWidth = 0.05
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {
    footprints: {},
    pts: {}
  }

  // Helper functions
  const degToRad = Math.PI / 180  // multiply by degrees to get radians
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

  const incrAngle = (endAngle - startAngle) / (kCount)

  var prevAngle = null
  var prevLed = null
  var prevGndOrigin = null
  var prevVinOrigin = null

  for (i=0; i<kCount; i++) {
    const angle = startAngle + incrAngle * i
    const origin = pAdd(xy, vRotate([radius, 0], angle))
    obj.footprints[`led[${i}]`] = led = board.add(LED_SK6812_EC15_1_5x1_5mm, {
      translate: origin,
      rotate: angle + rot,
      id: `rgb_sw_led_${i}_`
    })

    const gndOrigin = pAdd(xy, vRotate([radius - powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(gndOrigin, led.pad(4),
                    angle)
      ), powerWidth)

    const vinOrigin = pAdd(xy, vRotate([radius + powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(vinOrigin, led.pad(2),
                    angle)
      ), powerWidth)

    if (prevLed != null) {
      board.wire(path(
        ...smoothPath(prevLed.pad(3), led.pad(1),
                      prevAngle + 90, angle + 90)
        ), traceWidth)
      board.wire(path(
        ...smoothPath(prevGndOrigin, gndOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
      board.wire(path(
        ...smoothPath(prevVinOrigin, vinOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
    }

    prevAngle = angle
    prevLed = led
    prevVinOrigin = vinOrigin
    prevGndOrigin = gndOrigin
  }

  return obj
}

