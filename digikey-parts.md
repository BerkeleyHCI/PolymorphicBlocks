# Digikey Parts
Instructions for how to download required parts tables, because we believe that the DigiKey Terms of Use forbid us from redistributing our copy.

_Know of open-source parts tables that we could use instead?
Or do you represent DigiKey and think we've read the Terms of Use too strictly?
**Please let us know!**_


## General Procedure
For each part category in the [List of Parts Tables](#list-of-parts-tables):
1. Navigate to the linked category, or from the [DigiKey product list](https://www.digikey.com/products/en), eg "Ceramic Capacitors".
1. Select basic filters:
   - "Stock Status" = "In Stock" and "Normally Stocking"
   - "Packaging" = "Cut Tape (CT)" (this avoids the high minimum quantities for Tape & Reel, and the reeling fee for Digi-Reel)
1. Select parametric filters as needed, eg "Series" = "CL" and Capacitance as specified.
1. Apply selected filters.
1. Sort by "Quantity Available" (as a proxy for popularity).
1. Set "Results per Page" to the maximum (500).
1. At the bottom right of the page, click "Download Table".
1. Save the downloaded file with the indicated name, into `electronics_lib/resources/`.
   - Where there are multiple CSV files listed and ending with a number, eg `_1.csv`, `_2.csv`, the number indicates the page: "Download Table" only downloads the contents of the current page.
     You will need to download the pages separately.
     If there are more pages than file numbers, ignore the latter pages.


## List of Parts Tables
_Some documentation may be out of date_

- `Digikey_Crystals_3.2x2.5_1.csv`, `Digikey_Crystals_3.2x2.5_2.csv`: [Crystals](https://www.digikey.com/products/en/crystals-oscillators-resonators/crystals/171)
  - "Size / Dimension" = "0.126" L x 0.098" W (3.20mm x 2.50mm)" 
- `Digikey_Diodes_SOD123_SOD323.csv`: [Diodes - Rectifiers - Single](https://www.digikey.com/products/en/discrete-semiconductor-products/diodes-rectifiers-single/280)
  - "Package / Case" = "SOD-123" (and its variations), "SC-76, SOD-323", "SC-90, SOD-323F"
- `Digikey_Diodes_DO214.csv`: [Diodes - Rectifiers - Single](https://www.digikey.com/products/en/discrete-semiconductor-products/diodes-rectifiers-single/280)
  - "Package / Case" = "DO-214AA, SMB", "DO-214AB, SMC", "DO-214AC, SMA", "DO-214AC, SMA Flat Leads"
- `Digikey_Diodes_DPak_DDPak.csv`: [Diodes - Rectifiers - Single](https://www.digikey.com/products/en/discrete-semiconductor-products/diodes-rectifiers-single/280)
  - "Package / Case" = "TO-252-3, DPak (2 Leads + Tab), SC-63", "TO-263-3, D²Pak (2 Leads + Tab), TO-263AB" 
- `Digikey_Inductors_MurataDfe.csv`: [Fixed Inductors](https://www.digikey.com/products/en/inductors-coils-chokes/fixed-inductors/71)
  - "Series" = all variations of "DFE"
  - "Package / Case" = "0806 (2016 Metric)", "1008 (2520 Metric)", "1210 (3225 Metric)"
- `Digikey_Inductors_Shielded_BournsSRR_1005_1210_1260.csv`: [Fixed Inductors](https://www.digikey.com/products/en/inductors-coils-chokes/fixed-inductors/71)
  - "Series" = all variations of "SRR1005", "SRR1210", "SRR1260"
- `Digikey_Inductors_TaiyoYudenNr.csv`: [Fixed Inductors](https://www.digikey.com/products/en/inductors-coils-chokes/fixed-inductors/71)
  - "Series" = "NR" 
  - "Shielding" = "Shielded"
  - "Size / Dimension" = "0.118" L x 0.118" W (3.00mm x 3.00mm)", "0.157" L x 0.157" W (4.00mm x 4.00mm)", "0.193" L x 0.193" W (4.90mm x 4.90mm)", "0.236" L x 0.236" W (6.00mm x 6.00mm)"
- `Digikey_Inductors_TdkMlz.csv`: [Fixed Inductors](https://www.digikey.com/products/en/inductors-coils-chokes/fixed-inductors/71)
  - "Series" = "MLZ"
  - "Package / Case" = "0603 (1608 Metric)", "0805 (2012 Metric)"
- `Digikey_MLCC_SamsungCl_1pF_E12.csv`, `Digikey_MLCC_SamsungCl_1nF_E6.csv`, `Digikey_MLCC_SamsungCl_1uF_E3.csv`: [Ceramic Capacitors](https://www.digikey.com/products/en/capacitors/ceramic-capacitors/60)
  - "Series" = "CL"
  - "Temperature Coefficient" = "C0G / NP0", "X5R", "X6S", "X7R"
  - "Package / Case" = "0402 (1005 Metric)", "0603 (1608 Metric)", "0805 (2012 Metric)", "1206 (3216 Metric)", "1210 (3225 Metric)"
  - "Capacitance": select the E3 / E6 / E12 values from the decades (eg, `1pF_E12.csv` means 1 pF to 820 pF in E12 values)
- `Digikey_MLCC_YageoCc_1pF_E12_1.csv`, `Digikey_MLCC_YageoCc_1pF_E12_2.csv`, `Digikey_MLCC_YageoCc_1nF_E6_1.csv`, `Digikey_MLCC_YageoCc_1nF_E6_2.csv`, `Digikey_MLCC_YageoCc_1uF_E3.csv`: [Ceramic Capacitors](https://www.digikey.com/products/en/capacitors/ceramic-capacitors/60)
  - "Series" = "CC"
  - Other parameters same as above
- `Digikey_NFETs.csv`: [Transistors - FETs, MOSFETs - Single](https://www.digikey.com/products/en/discrete-semiconductor-products/transistors-fets-mosfets-single/278)
  - "FET Type": "N-Channel"
  - "Technology": "MOSFET (Metal Oxide)"
  - "FET Feature": "Standard"
  - "Package / Case": "TO-236-3, SC-59, SOT-23-3", "TO-261-4, TO-261AA", "TO-252-3, DPak (2 Leads + Tab), SC-63", "TO-263-3, D²Pak (2 Leads + Tab), TO-263AB"
- `Digikey_PFETs.csv`: [Transistors - FETs, MOSFETs - Single](https://www.digikey.com/products/en/discrete-semiconductor-products/transistors-fets-mosfets-single/278)
  - "FET Type": "P-Channel"
  - Other parameters same as above
- `Digikey_ZenerDiodes_SOD123_SOD323.csv`: [Diodes - Zener - Single](https://www.digikey.com/products/en/discrete-semiconductor-products/diodes-zener-single/287)
  - "Package / Case" = "SOD-123", "SOD-123F", "SC-76, SOD-323", "SC-90, SOD-323F"
- `Digikey_ZenerDiodes_DO214.csv`: [Diodes - Zener - Single](https://www.digikey.com/products/en/discrete-semiconductor-products/diodes-zener-single/287)
  - "Package / Case" = "DO-214AA, SMB", "DO-214AB, SMC", "DO-214AC, SMA", "DO-214AC, SMA Flat Leads"
