import os.path
import pickle

import pytest

from pydesc.config import ConfigManager
from pydesc.contacts.criteria import RC_DISTANCE, DEFAULT_PROTEIN
from pydesc.contacts.maps import ContactMapCalculator
from pydesc.structure import StructureLoader
from tests.conftest import TEST_CMAPS_DIR
from tests.conftest import TEST_STRUCTURES_DIR

ConfigManager.warnings.set("quiet", True)


def test_rc_contact_map(structure_file_w_type):
    sl = StructureLoader()
    path_str = os.path.join(TEST_STRUCTURES_DIR, structure_file_w_type)
    structures = sl.load_structures(path=path_str)

    for structure in structures:
        cm_calc = ContactMapCalculator(
            structure_obj=structure,
            contact_criterion_obj=RC_DISTANCE
        )
        cm = cm_calc.calculate_contact_map()
        assert len(cm) > 0, "No contacts in structure %s" % str(structure)
        for (k1, k2), v in cm:
            length = (structure[k1].rc - structure[k2].rc).calculate_length()
            assert length < 10


def test_golden_standard_pydesc_criterion_protein(protein_file):
    fname = os.path.split(protein_file)[1]
    structure_name = os.path.splitext(fname)[0]
    path_str = os.path.join(TEST_CMAPS_DIR, "%s_default.cmp" % structure_name)
    with open(path_str, "rb") as fh:
        golden_cmap_dict = pickle.load(fh)

    sl = StructureLoader()
    pth = os.path.join(TEST_STRUCTURES_DIR, protein_file)
    structure = sl.load_structures(path=pth)[0]

    cm_calc = ContactMapCalculator(structure, DEFAULT_PROTEIN)
    cm = cm_calc.calculate_contact_map()
    res = {frozenset(k): v for k, v in list(cm._contacts.items())}

    assert golden_cmap_dict == res


def test_golden_standard_rc_protein(protein_file):
    fname = os.path.split(protein_file)[1]
    structure_name = os.path.splitext(fname)[0]
    path_str = os.path.join(TEST_CMAPS_DIR, "%s_rc.cmp" % structure_name)
    with open(path_str, "rb") as fh:
        golden_cmap_dict = pickle.load(fh)

    sl = StructureLoader()
    path_str = os.path.join(TEST_STRUCTURES_DIR, protein_file)
    structure = sl.load_structures(path=path_str)[0]

    cm_calc = ContactMapCalculator(
        structure_obj=structure,
        contact_criterion_obj=RC_DISTANCE,
    )
    cm = cm_calc.calculate_contact_map()

    res = {frozenset(k): v for k, v in list(cm._contacts.items())}

    assert golden_cmap_dict == res


@pytest.mark.system
def test_1no5_default_criteria_cmap():
    sl = StructureLoader()
    structure, = sl.load_structures("1no5")

    cmc = ContactMapCalculator(structure, DEFAULT_PROTEIN)
    cmap = cmc.calculate_contact_map()

    assert len(cmap) > 30
