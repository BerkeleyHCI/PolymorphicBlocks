const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.235, 1.763), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.274, 1.763), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.235, 1.802), rotate: 0,
  id: 'jlc_th_th3'
})
const mcu = board.add(FEATHERWING_NODIM, {
  translate: pt(0.392, 1.763), rotate: 0,
  id: 'mcu'
})
const motor_pwr_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.096, 1.286), rotate: 0,
  id: 'motor_pwr_conn'
})
const sw1_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.753, 0.919), rotate: 0,
  id: 'sw1_package'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(1.872, 1.185), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(1.872, 1.282), rotate: 0,
  id: 'ledr_res'
})
const ledg_package = board.add(LED_0603_1608Metric, {
  translate: pt(2.342, 1.185), rotate: 0,
  id: 'ledg_package'
})
const ledg_res = board.add(R_0603_1608Metric, {
  translate: pt(2.341, 1.282), rotate: 0,
  id: 'ledg_res'
})
const ledb_package = board.add(LED_0603_1608Metric, {
  translate: pt(2.107, 1.185), rotate: 0,
  id: 'ledb_package'
})
const ledb_res = board.add(R_0603_1608Metric, {
  translate: pt(2.106, 1.282), rotate: 0,
  id: 'ledb_res'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 1.519), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 1.616), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const i2c_tp_tp_scl_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.629, 1.193), rotate: 0,
  id: 'i2c_tp_tp_scl_tp'
})
const i2c_tp_tp_sda_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.629, 1.307), rotate: 0,
  id: 'i2c_tp_tp_sda_tp'
})
const i2c_conn = board.add(JST_PH_B4B_PH_K_1x04_P2_00mm_Vertical, {
  translate: pt(1.112, 1.286), rotate: 0,
  id: 'i2c_conn'
})
const ref_div_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 1.519), rotate: 0,
  id: 'ref_div_div_top_res'
})
const ref_div_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 1.616), rotate: 0,
  id: 'ref_div_div_bottom_res'
})
const ref_buf_amp_ic = board.add(SOT_23_5, {
  translate: pt(0.952, 0.874), rotate: 0,
  id: 'ref_buf_amp_ic'
})
const ref_buf_amp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.929, 1.009), rotate: 0,
  id: 'ref_buf_amp_vdd_cap_cap'
})
const ref_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.271, 1.528), rotate: 0,
  id: 'ref_tp_tp'
})
const hall_conn = board.add(JST_PH_B5B_PH_K_1x05_P2_00mm_Vertical, {
  translate: pt(0.486, 1.286), rotate: 0,
  id: 'hall_conn'
})
const hall_pull_res_u__res = board.add(R_0603_1608Metric, {
  translate: pt(2.376, 0.029), rotate: 0,
  id: 'hall_pull_res_u__res'
})
const hall_pull_res_v__res = board.add(R_0603_1608Metric, {
  translate: pt(2.376, 0.126), rotate: 0,
  id: 'hall_pull_res_v__res'
})
const hall_pull_res_w__res = board.add(R_0603_1608Metric, {
  translate: pt(2.376, 0.222), rotate: 0,
  id: 'hall_pull_res_w__res'
})
const hall_tp_tp_u__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.134, 0.037), rotate: 0,
  id: 'hall_tp_tp_u__tp'
})
const hall_tp_tp_v__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.134, 0.152), rotate: 0,
  id: 'hall_tp_tp_v__tp'
})
const hall_tp_tp_w__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.134, 0.266), rotate: 0,
  id: 'hall_tp_tp_w__tp'
})
const vsense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.519), rotate: 0,
  id: 'vsense_div_top_res'
})
const vsense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.616), rotate: 0,
  id: 'vsense_div_bottom_res'
})
const vsense_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.521, 1.528), rotate: 0,
  id: 'vsense_tp_tp'
})
const isense_sense_res_res = board.add(R_1206_3216Metric, {
  translate: pt(1.359, 0.044), rotate: 0,
  id: 'isense_sense_res_res'
})
const isense_amp_amp_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.084, 0.106), rotate: 0,
  id: 'isense_amp_amp_ic'
})
const isense_amp_amp_vdd_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.336, 0.166), rotate: 0,
  id: 'isense_amp_amp_vdd_cap_cap'
})
const isense_amp_r1 = board.add(R_0603_1608Metric, {
  translate: pt(0.997, 0.281), rotate: 0,
  id: 'isense_amp_r1'
})
const isense_amp_r2 = board.add(R_0603_1608Metric, {
  translate: pt(1.153, 0.281), rotate: 0,
  id: 'isense_amp_r2'
})
const isense_amp_rf = board.add(R_0603_1608Metric, {
  translate: pt(1.309, 0.281), rotate: 0,
  id: 'isense_amp_rf'
})
const isense_amp_rg = board.add(R_0603_1608Metric, {
  translate: pt(0.997, 0.378), rotate: 0,
  id: 'isense_amp_rg'
})
const isense_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.272, 1.528), rotate: 0,
  id: 'isense_tp_tp'
})
const isense_clamp_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.792), rotate: 0,
  id: 'isense_clamp_res'
})
const bldc_drv_ic = board.add(HTSSOP_28_1EP_4_4x9_7mm_P0_65mm_EP2_85x5_4mm_ThermalVias, {
  translate: pt(0.152, 0.201), rotate: 0,
  id: 'bldc_drv_ic'
})
const bldc_drv_vm_cap_bulk_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.407, 0.480), rotate: 0,
  id: 'bldc_drv_vm_cap_bulk_cap'
})
const bldc_drv_vm_cap1_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.580, 0.480), rotate: 0,
  id: 'bldc_drv_vm_cap1_cap'
})
const bldc_drv_vm_cap2_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.754, 0.480), rotate: 0,
  id: 'bldc_drv_vm_cap2_cap'
})
const bldc_drv_v3p3_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.660), rotate: 0,
  id: 'bldc_drv_v3p3_cap_cap'
})
const bldc_drv_cp_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 0.660), rotate: 0,
  id: 'bldc_drv_cp_cap'
})
const bldc_drv_vcp_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.660), rotate: 0,
  id: 'bldc_drv_vcp_cap'
})
const bldc_drv_pgnd_res_1__res_res = board.add(R_2512_6332Metric, {
  translate: pt(0.493, 0.076), rotate: 0,
  id: 'bldc_drv_pgnd_res_1__res_res'
})
const bldc_drv_pgnd_res_2__res_res = board.add(R_2512_6332Metric, {
  translate: pt(0.493, 0.266), rotate: 0,
  id: 'bldc_drv_pgnd_res_2__res_res'
})
const bldc_drv_pgnd_res_3__res_res = board.add(R_2512_6332Metric, {
  translate: pt(0.150, 0.517), rotate: 0,
  id: 'bldc_drv_pgnd_res_3__res_res'
})
const bldc_fault_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.020, 1.528), rotate: 0,
  id: 'bldc_fault_tp_tp'
})
const bldc_en_tp_tp_1__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.633, 0.037), rotate: 0,
  id: 'bldc_en_tp_tp_1__tp'
})
const bldc_en_tp_tp_2__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.633, 0.152), rotate: 0,
  id: 'bldc_en_tp_tp_2__tp'
})
const bldc_en_tp_tp_3__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.633, 0.266), rotate: 0,
  id: 'bldc_en_tp_tp_3__tp'
})
const bldc_in_tp_tp_1__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.883, 0.037), rotate: 0,
  id: 'bldc_in_tp_tp_1__tp'
})
const bldc_in_tp_tp_2__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.883, 0.152), rotate: 0,
  id: 'bldc_in_tp_tp_2__tp'
})
const bldc_in_tp_tp_3__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.883, 0.266), rotate: 0,
  id: 'bldc_in_tp_tp_3__tp'
})
const bldc_conn = board.add(JST_PH_B3B_PH_K_1x03_P2_00mm_Vertical, {
  translate: pt(2.135, 0.937), rotate: 0,
  id: 'bldc_conn'
})
const curr_amp_1__amp_ic = board.add(SOT_23_5, {
  translate: pt(0.081, 0.874), rotate: 0,
  id: 'curr_amp_1__amp_ic'
})
const curr_amp_1__amp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.259, 0.836), rotate: 0,
  id: 'curr_amp_1__amp_vdd_cap_cap'
})
const curr_amp_1__r1 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.009), rotate: 0,
  id: 'curr_amp_1__r1'
})
const curr_amp_1__r2 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 1.009), rotate: 0,
  id: 'curr_amp_1__r2'
})
const curr_tp_1__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.772, 1.528), rotate: 0,
  id: 'curr_tp_1__tp'
})
const curr_amp_2__amp_ic = board.add(SOT_23_5, {
  translate: pt(1.231, 0.874), rotate: 0,
  id: 'curr_amp_2__amp_ic'
})
const curr_amp_2__amp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.409, 0.836), rotate: 0,
  id: 'curr_amp_2__amp_vdd_cap_cap'
})
const curr_amp_2__r1 = board.add(R_0603_1608Metric, {
  translate: pt(1.209, 1.009), rotate: 0,
  id: 'curr_amp_2__r1'
})
const curr_amp_2__r2 = board.add(R_0603_1608Metric, {
  translate: pt(1.365, 1.009), rotate: 0,
  id: 'curr_amp_2__r2'
})
const curr_tp_2__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.770, 1.528), rotate: 0,
  id: 'curr_tp_2__tp'
})
const curr_amp_3__amp_ic = board.add(SOT_23_5, {
  translate: pt(0.516, 0.874), rotate: 0,
  id: 'curr_amp_3__amp_ic'
})
const curr_amp_3__amp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.694, 0.836), rotate: 0,
  id: 'curr_amp_3__amp_vdd_cap_cap'
})
const curr_amp_3__r1 = board.add(R_0603_1608Metric, {
  translate: pt(0.494, 1.009), rotate: 0,
  id: 'curr_amp_3__r1'
})
const curr_amp_3__r2 = board.add(R_0603_1608Metric, {
  translate: pt(0.650, 1.009), rotate: 0,
  id: 'curr_amp_3__r2'
})
const curr_tp_3__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.022, 1.528), rotate: 0,
  id: 'curr_tp_3__tp'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.552755905511811, 1.9385826771653545);
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


