from typing import Any, Tuple

from pydantic import BaseModel, RootModel, Field
import gzip

kTestingFilename = "../../../../jlcparts/web/public/data/CrystalsakaOscillatorsakaResonatorsCrystals.json.gz"
kSchemaLcsc = "lcsc"  # JLC part number
kSchemaPartName = "mfr"  # manufacturer part name
kSchemaDatasheet = "datasheet"  # URL
kSchemaAttributes = "attributes"  # attribute table

class JlcPartFile(BaseModel):
    category: str
    components: list[list[Any]]  # index-matched with schema
    jlcpart_schema: list[str] = Field(..., alias='schema')

class JlcPartValue(BaseModel):
    default: Tuple[str, str]  # value, type / units

class JlcPartAttributeEntry(BaseModel):
    format: str
    primary: str
    values: JlcPartValue

class JlcPartAttributes(RootModel):
    root: dict[str, JlcPartAttributeEntry]


if __name__ == "__main__":
    with gzip.open(kTestingFilename, 'r') as f:
        data = JlcPartFile.model_validate_json(f.read())
        print(len(data.components))
        print(data.category)
        print(data.components[0])
        print(JlcPartAttributes(**data.components[0][-1]))
