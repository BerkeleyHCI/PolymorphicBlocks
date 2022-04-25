## Process for generating a JLC pick-and-place file

From EDG: export with NetlistGenerator.py set to refdes mode and LCSC parts

From KiCad: export both BoM and footprint position files (in CSV)

Post-process BoM CSV:

- Replace `;` with `,` to make it an actual CSV

- Rename these columns:
  
  - Designation -> JLCPCB Part #

- Add a Comment column

Post-process position CSV:

- Rename these columns:
  
  - Ref -> Designator
  
  - PosX -> Mid X
  
  - PosY -> Mid Y
  
  - Rot -> Rotation
  
  - Side -> Layer
  
- Diodes may need a 180 rotation