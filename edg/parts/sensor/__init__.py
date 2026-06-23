from .Temp_Shtc3 import Shtc3
from .Temp_TexasInstruments import Hdc1080, Tmp1075n

from .Imu_Lsm6ds3trc import Lsm6ds3trc
from .Imu_Lsm6dsv16x import Lsm6dsv16x

from .Mag_A1304 import A1304
from .MagSwitch_Ah1806 import Ah1806
from .Mag_Qmc5883 import Qmc5883l, Qmc5883p

from .FlirLepton import FlirLepton
from .Camera_Ov2640_Fpc24 import Ov2640, Ov2640_Fpc24

from .Distance_Vl53l0x import Vl53l0x, Vl53l0xConnector, Vl53l0xArray
from .DistanceArray_Vl53l5cx import Vl53l5cx
from .EnvironmentalSensor_Bme680 import Bme680
from .LightSensor_Bh1750 import Bh1750
from .LightSensor_As7341 import As7341
from .Rtc_Pcf2129 import Pcf2129

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
