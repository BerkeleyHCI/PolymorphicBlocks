from typing import cast

from electronics_abstract_parts import *


class SwitchMatrix(HumanInterface, GeneratorBlock):
  """A switch matrix, such as for a keyboard, that generates (nrows * ncols) switches while only
  using max(nrows, ncols) IOs.

  Internally, the switches are in a matrix, with the driver driving one col low at a time while
  reading which rows are low (with the other cols weakly pulled high).
  This uses the Switch abstract class, which can be refined into e.g. a tactile switch or mechanical keyswitch.

  This generates per-switch diodes which allows multiple keys to be pressed simultaneously.
  Diode anodes are attached to the rows, while cathodes go through each switch to the cols.
  """
  @init_in_parent
  def __init__(self, nrows: IntLike, ncols: IntLike, voltage_drop: RangeLike = (0, 0.7)*Volt):
    super().__init__()

    self.rows = self.Port(Vector(DigitalSingleSource.empty()))
    self.cols = self.Port(Vector(DigitalSink.empty()))
    self.voltage_drop = self.ArgParameter(voltage_drop)

    self.nrows = self.ArgParameter(nrows)
    self.ncols = self.ArgParameter(ncols)
    self.generator_param(self.nrows, self.ncols)

  def generate(self):
    super().generate()
    row_ports = {}
    for row in range(self.get(self.nrows)):
      row_ports[row] = self.rows.append_elt(DigitalSingleSource.empty(), str(row))

    self.sw = ElementDict[Switch]()
    self.d = ElementDict[Diode]()
    for col in range(self.get(self.ncols)):
      col_port = cast(DigitalSink, self.cols.append_elt(DigitalSink.empty(), str(col)))
      col_port_model = DigitalSink()  # ideal, negligible current draw (assumed) and thresholds checked at other side
      for (row, row_port) in row_ports.items():
        sw = self.sw[f"{col},{row}"] = self.Block(Switch(
          voltage=row_port.link().voltage,
          current=row_port.link().current_drawn
        ))
        d = self.d[f"{col},{row}"] = self.Block(Diode(
          current=row_port.link().current_drawn,
          # col voltage is used as a proxy, since (properly) using the row voltage causes a circular dependency
          reverse_voltage=col_port.link().voltage,
          voltage_drop=self.voltage_drop
        ))
        lowest_output = col_port.link().voltage.lower() + d.actual_voltage_drop.lower()
        highest_output = col_port.link().output_thresholds.lower() + d.actual_voltage_drop.upper()
        self.connect(d.anode.adapt_to(DigitalSingleSource(
          voltage_out=(lowest_output, highest_output),
          output_thresholds=(highest_output, float('inf')),
          low_signal_driver=True
        )), row_port)
        self.connect(d.cathode, sw.sw)
        self.connect(sw.com.adapt_to(col_port_model), col_port)

    self.rows.defined()
    self.cols.defined()
