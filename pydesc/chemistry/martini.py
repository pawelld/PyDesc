from pydesc.chemistry.base import Mer
from pydesc.config import ConfigManager

ConfigManager.chemistry.new_branch("martiniresidue")
ConfigManager.chemistry.martiniresidue.set_default("backbone_atoms", ("BB",))


class MartiniResidue(Mer):
    @property
    def last_cs(self):
        self_len = len(self.atoms)
        try:
            return self.atoms[f"SC{self_len - 1}"]
        except KeyError:
            return self.atoms["BB"]
