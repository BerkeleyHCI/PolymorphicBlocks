from typing import Dict, List, Union, Set

from electronics_model import CircuitPort


class VariantPinRemapper:
  def __init__(self, mapping: Dict[str, CircuitPort]):
    self.mapping = mapping

  def remap(self, remap: Dict[str, Union[str, List[str]]]) -> Dict[str, CircuitPort]:
    output_dict: Dict[str, CircuitPort] = {}
    remapped_names: Set[str] = set()
    for (orig_name, orig_port) in self.mapping.items():
      assert orig_name in remap, f"missing remap rule for {orig_name}"
      remapped_names.add(orig_name)
      remapping = remap[orig_name]
      if isinstance(remapping, str):
        assert remapping not in output_dict, f"duplicate remap to {remapping}"
        output_dict[remapping] = orig_port
      elif isinstance(remapping, list):
        for remap_name in remapping:
          assert remap_name not in output_dict, f"duplicate remap to {remap_name}"
          output_dict[remap_name] = orig_port
      else:
        raise NotImplementedError(f"unknown remap rule {remap[orig_name]} for {orig_name}")
    missed_names = set(self.mapping.keys()).difference(remapped_names)
    assert not missed_names, f"pins not remapped: {missed_names}"

    return output_dict
