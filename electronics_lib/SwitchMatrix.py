from typing import cast

from electronics_abstract_parts import *


class SwitchMatrix(HumanInterface, GeneratorBlock):
  """A switch matrix that generates (rows * cols) switches while only using max(rows, cols) IOs, by arranging
  them in a matrix, having the driver drive one col low at a time and reading which rows are low
  (with all cols weakly pulled high).
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

    self.generator(self.generate, nrows, ncols)

  def generate(self, rows: int, cols: int):
    # col voltage is used as a proxy for voltage, since (properly) using the row voltage causes a circular dependency
    cols_voltage = self.cols.hull(lambda port: port.link().voltage)
    diode_model = Diode(current=(0, 0)*Amp, reverse_voltage=cols_voltage, voltage_drop=self.voltage_drop)

    row_ports = {}
    for row in range(rows):
      row_ports[row] = self.rows.append_elt(DigitalSingleSource.empty(), str(row))

    self.sw = ElementDict[Switch]()
    self.d = ElementDict[Diode]()
    for col in range(cols):
      col_port = cast(DigitalSink, self.cols.append_elt(DigitalSink.empty(), str(col)))
      col_port_model = DigitalSink()  # ideal, negligible current draw (assumed) and thresholds checked at other side
      for (row, row_port) in row_ports.items():
        sw = self.sw[f"{col},{row}"] = self.Block(Switch(
          voltage=row_port.link().voltage,
          current=row_port.link().current_drawn
        ))
        d = self.d[f"{col},{row}"] = self.Block(diode_model)
        lowest_output = col_port.link().voltage.lower() + d.actual_voltage_drop.lower()
        highest_output = col_port.link().output_thresholds.lower() + d.actual_voltage_drop.upper()
        self.connect(d.anode.adapt_to(DigitalSingleSource(
          voltage_out=(lowest_output, highest_output),
          output_thresholds=(highest_output, float('inf')),
          low_signal_driver=True
        )), row_port)
        self.connect(d.cathode, sw.a)
        self.connect(sw.b.adapt_to(col_port_model), col_port)

    self.rows.defined()
    self.cols.defined()
