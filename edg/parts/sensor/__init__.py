from .image import *
from .imu import *
from .magnetic import *
from .temperature import *

from .Distance_Vl53l0x import Vl53l0x, Vl53l0xConnector, Vl53l0xArray
from .EnvironmentalSensor_Bme680 import Bme680
from .LightSensor_Bh1750 import Bh1750
from .LightSensor_As7341 import As7341

from .Microphone_Sd18ob261 import Sd18ob261

# compatibility shims
import deprecated as __deprecated  # not to be exported


from ...abstract_parts import DeprecatedBlock


@__deprecated.deprecated("new naming convention")
class Vl53l0xApplication(Vl53l0x, DeprecatedBlock):
    pass


@__deprecated.deprecated("new naming convention")
class Imu_Lsm6ds3trc(Lsm6ds3trc, DeprecatedBlock):
    pass


@__deprecated.deprecated("new naming convention")
class Mag_Qmc5883l(Qmc5883l, DeprecatedBlock):
    pass
