from typing import cast

from electronics_abstract_parts import *


class SwitchMatrix(HumanInterface, GeneratorBlock):
  """A switch matrix that generates (rows * cols) switches while only using max(rows, cols) IOs, by arranging
  them in a matrix, having the driver drive one row high at a time and reading which cols are connected
  (with all cols weakly pulled low).
  This uses the Switch abstract class, which can be refined into e.g. a tactile switch or mechanical keyswitch.

  This generates per-switch diodes which allows multiple keys to be pressed simultaneously.
  Diode anodes are attached to the rows, while cathodes go through each switch to the cols.
  """
  @init_in_parent
  def __init__(self, nrows: IntLike, ncols: IntLike):
    super().__init__()

    self.rows = self.Port(Vector(DigitalSink.empty()))
    self.cols = self.Port(Vector(DigitalSingleSource.empty()))

    self.generator(self.generate, nrows, ncols)

  def generate(self, rows: int, cols: int):
    switch_model = Switch()
    max_voltage = self.rows.hull(lambda port: port.link().voltage)  # TODO assumes 0 is ground
    diode_model = Diode(current=(0, 0)*Amp, reverse_voltage=max_voltage)

    col_ports = {}
    for col in range(cols):
      col_ports[col] = self.cols.append_elt(DigitalSingleSource.empty(), str(col))

    self.sw = ElementDict[Switch]()
    self.d = ElementDict[Diode]()
    for row in range(rows):
      row_port = cast(DigitalSink, self.rows.append_elt(DigitalSink.empty(), str(row)))
      switch_b_model = DigitalSink()  # ideal, negligible current draw (assumed) and thresholds checked at other side
      for (col, col_port) in col_ports.items():
        sw = self.sw[f"{col},{row}"] = self.Block(switch_model)
        d = self.d[f"{col},{row}"] = self.Block(diode_model)
        self.connect(d.anode.adapt_to(switch_b_model), row_port)
        self.connect(d.cathode, sw.a)
        output_voltages = (row_port.link().output_thresholds.upper() - d.actual_voltage_drop.upper(),
                           row_port.link().voltage.upper() - d.actual_voltage_drop.lower())
        self.connect(sw.b.adapt_to(DigitalSingleSource(
          voltage_out=output_voltages, output_thresholds=output_voltages,
          pulldown_capable=False, high_signal_driver=True
        )), col_port)

    self.rows.defined()
    self.cols.defined()
