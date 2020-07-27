from os.path import join as path_join

import pytest

from pydesc.chemistry.base import Atom
from pydesc.chemistry.factories import BioPythonAtomSetFactory
from pydesc.chemistry.martini import MartiniResidue
from pydesc.structure import StructureLoader


@pytest.fixture
def martini_structure_path(structures_dir):
    return path_join(structures_dir, "martini")


def test_martini(martini_structure_path):
    factory = BioPythonAtomSetFactory(classes=[MartiniResidue])
    loader = StructureLoader(atom_set_factory=factory)
    path = path_join(martini_structure_path, "gpcr_d.pdb")
    stc = loader.load_structures(path=path)[0]

    assert len(stc) > 0
    for residue in stc:
        assert isinstance(residue, MartiniResidue)
        assert len(tuple(residue.iter_bb_atoms())) == 1
        assert len(tuple(residue.iter_nbb_atoms())) == (len(residue) - 1)
        assert isinstance(residue.last_cs, Atom)
        if residue.name in ("GLY", "ALA"):
            assert residue.last_cs == residue.atoms["BB"]
            continue
        last_cs = max(
            [k for k in residue.atoms if "SC" in k], key=lambda name: int(name[-1])
        )
        assert residue.last_cs == residue.atoms[last_cs]
