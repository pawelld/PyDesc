# Copyright 2017 Pawel Daniluk, Tymoteusz Oleniecki
#
# This file is part of PyDesc.
#
# PyDesc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyDesc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PyDesc.  If not, see <http://www.gnu.org/licenses/>.

"""
Unit tests for monomer.py.

Usage:
    python monomer_test.py [-v] [--fast]

    or

    python -m unittest [-v] monomer_test

Pawel, Tymoteusz
"""

import unittest

import types
import itertools
import numpy

import Bio.PDB

import syntax_check
from syntax_check import notest, testing, randomcoord, test_name_append

import pydesc.structure as structure
import pydesc.monomer as monomer
import pydesc.geometry as geometry
import pydesc.config as config
import pydesc.selection as selection
import pydesc.numberconverter as numcon
import tests
from pydesc.warnexcept import IncompleteChainableParticle as IncompleteChainableParticle

config.ConfigManager.warnings_and_exceptions.class_filters.set("UnknownParticleName", "ignore")
config.ConfigManager.warnings_and_exceptions.class_filters.set("IncompleteChainableParticle", "ignore")

fast = False

fast = True

syntax_check.module = monomer

TestSyntax = syntax_check.module_syntax()

notest(monomer.Atom.__iter__)
#notest(monomer.Atom.__getattr__)
#notest(monomer.Atom.__setattr__)

notest(monomer.Monomer.get_pdb_id)
notest(monomer.MonomerChainable.next_monomer)
notest(monomer.MonomerChainable.previous_monomer)
notest(monomer.Monomer.is_next)
notest(monomer.Monomer.is_prev)
notest(monomer.Monomer.get_representation)

notest(monomer.MonomerChainable.__metaclass__)
notest(monomer.MonomerChainable.__metaclass__.__call__)

notest(monomer.MonomerOther.__metaclass__)
notest(monomer.MonomerOther.__metaclass__.__call__)
notest(monomer.MonomerOther.next_monomer)
notest(monomer.MonomerOther.previous_monomer)

notest(monomer.Residue.calculate_cbx_legacy)

tests_performed = dict((x, False) for x in [
    'monomer.Ion',
    'monomer.Ligand',
    'monomer.Residue',
    'monomer.Nucleotide'
])

data_dir = tests.__path__[0] + '/data/test_structures/'

# pylint: disable=C0111


@testing(monomer.Atom)
@testing(monomer.Pseudoatom)
class AtomEnhancements(unittest.TestCase):

    """ TestCase for enhancements requested in monomer.Atom. """

    @testing(monomer.Atom.__init__)
#    @testing(monomer.Atom.__getitem__)
#    @testing(monomer.Atom.__setitem__)
    @unittest.expectedFailure
    def test_deprec(self):
        """ Deprecation of __getitem__ interface to Atom. """
        a = monomer.Atom(*randomcoord())
        syntax_check.test_deprec(self, lambda: a['name'], "__getitem__")
        syntax_check.test_deprec(self, lambda: a.__setitem__('name', 'aa'), "__setitem__")

    @unittest.expectedFailure
    def test_hashable(self):
        """ Check whether Atom is hashable. """
        a = monomer.Atom(*randomcoord())
        try:
            set([a])
        except:
            self.fail()

    @testing(monomer.Pseudoatom.__init__)
    @testing(monomer.Atom.vector)
    def test_pseudoatom_init(self):
        """Checks if Pseudoatoms are created both ways."""
        for d in range(100):
            random_coords = randomcoord()
            pa = monomer.Pseudoatom(*random_coords)
            pa2 = monomer.Pseudoatom(numpy_vec=numpy.array(random_coords))
            for i in zip(pa.vector, pa2.vector):
                self.assertEqual(*i)

@testing(monomer.Monomer)
class MonomerClassMethods(unittest.TestCase):

    @testing(monomer.Monomer.seq_3to1)
    @testing(monomer.Monomer.seq_1to3)
    def test_seqs(self):
        cls = monomer.Residue
        self.assertEqual(cls.seq_3to1('ALA'), 'A')
        self.assertEqual(cls.seq_1to3('A'), 'ALA')
        self.assertEqual(cls.seq_3to1('CYS'), 'C')
        self.assertEqual(cls.seq_1to3('C'), 'CYS')
        self.assertEqual(cls.seq_3to1('ASP'), 'D')
        self.assertEqual(cls.seq_1to3('D'), 'ASP')
        self.assertEqual(cls.seq_3to1('GLU'), 'E')
        self.assertEqual(cls.seq_1to3('E'), 'GLU')
        self.assertEqual(cls.seq_3to1('PHE'), 'F')
        self.assertEqual(cls.seq_1to3('F'), 'PHE')
        self.assertEqual(cls.seq_3to1('GLY'), 'G')
        self.assertEqual(cls.seq_1to3('G'), 'GLY')
        self.assertEqual(cls.seq_3to1('HIS'), 'H')
        self.assertEqual(cls.seq_1to3('H'), 'HIS')
        self.assertEqual(cls.seq_3to1('ILE'), 'I')
        self.assertEqual(cls.seq_1to3('I'), 'ILE')
        self.assertEqual(cls.seq_3to1('LYS'), 'K')
        self.assertEqual(cls.seq_1to3('K'), 'LYS')
        self.assertEqual(cls.seq_3to1('LEU'), 'L')
        self.assertEqual(cls.seq_1to3('L'), 'LEU')
        self.assertEqual(cls.seq_3to1('MET'), 'M')
        self.assertEqual(cls.seq_1to3('M'), 'MET')
        self.assertEqual(cls.seq_3to1('ASN'), 'N')
        self.assertEqual(cls.seq_1to3('N'), 'ASN')
        self.assertEqual(cls.seq_3to1('PRO'), 'P')
        self.assertEqual(cls.seq_1to3('P'), 'PRO')
        self.assertEqual(cls.seq_3to1('GLN'), 'Q')
        self.assertEqual(cls.seq_1to3('Q'), 'GLN')
        self.assertEqual(cls.seq_3to1('ARG'), 'R')
        self.assertEqual(cls.seq_1to3('R'), 'ARG')
        self.assertEqual(cls.seq_3to1('SER'), 'S')
        self.assertEqual(cls.seq_1to3('S'), 'SER')
        self.assertEqual(cls.seq_3to1('THR'), 'T')
        self.assertEqual(cls.seq_1to3('T'), 'THR')
        self.assertEqual(cls.seq_3to1('TRP'), 'W')
        self.assertEqual(cls.seq_1to3('W'), 'TRP')
        self.assertEqual(cls.seq_3to1('TYR'), 'Y')
        self.assertEqual(cls.seq_1to3('Y'), 'TYR')
        self.assertEqual(cls.seq_3to1('VAL'), 'V')
        self.assertEqual(cls.seq_1to3('V'), 'VAL')
        cls = monomer.Nucleotide
        self.assertEqual(cls.seq_3to1('  A'), 'A')
        self.assertEqual(cls.seq_1to3('A'), '  A')
        self.assertEqual(cls.seq_3to1('  U'), 'U')
        self.assertEqual(cls.seq_1to3('U'), '  U')
        self.assertEqual(cls.seq_3to1('  G'), 'G')
        self.assertEqual(cls.seq_1to3('G'), '  G')
        self.assertEqual(cls.seq_3to1('  C'), 'C')
        self.assertEqual(cls.seq_1to3('C'), '  C')
        self.assertEqual(cls.seq_3to1(' DA'), 'A')
        self.assertEqual(cls.seq_3to1(' DT'), 'T')
        self.assertEqual(cls.seq_1to3('T'), ' DT')
        self.assertEqual(cls.seq_3to1(' DG'), 'G')
        self.assertEqual(cls.seq_3to1(' DC'), 'C')


def make_monomertestbasic(strname, cls):
    """ Create and return a MonomerTestBasic test case for a given structure and monomer class. """

    @testing(cls)
    @testing(monomer.Monomer)
    @testing(monomer.MonomerChainable)
    @test_name_append(cls, strname)
    class MonomerTestBasic(unittest.TestCase):

        def setUp(self):
            self.pdb_structure = Bio.PDB.PDBParser(QUIET=True).get_structure(strname, data_dir + '%s.pdb' % strname)
            self.ress = filter(lambda x: x is not None, map(monomer.Monomer.create_monomers, self.pdb_structure.get_residues()))

        @testing(cls.__init__)
        @testing(monomer.Monomer.__init__)
        @testing(monomer.MonomerChainable.__init__)
        def test_init(self):
            for res in self.pdb_structure.get_residues():
                res_id = res.get_id()[0]
                if not res_id.startswith('H_') and not res_id.startswith('W'):
                    try:
                        cls(res)
                    except KeyError as error:
                        try:
                            res[str(error).strip()]
                        except:
                            pass
                        else:
                            raise error

        @testing(monomer.Monomer.get_config)
        def test_get_config(self):
            config.ConfigManager.monomer.residue.set_default('test', 1)
            config.ConfigManager.monomer.nucleotide.set_default('test', 2)
            config.ConfigManager.monomer.ligand.set_default('test', 3)
            config.ConfigManager.monomer.ion.set_default('test', 4)
            test_dict = {monomer.Residue: 1, monomer.Nucleotide: 2, monomer.Ligand: 3, monomer.Ion: 4}
            for i in self.ress:
                for cls, res in i.items():
                    if cls == monomer.MonomerOther:
                        cls = res.__class__
                    self.assertEqual(test_dict[cls], res.get_config('test'), "")

                    class TestMonomer(cls):
                        pass

                    artif = TestMonomer(res.pdb_residue)
                    self.assertEqual(test_dict[cls], artif.get_config('test'))

        
        @testing(monomer.Monomer.select)
        def test_select(self):
            nc = numcon.NumberConverter(self.pdb_structure)
            class S:
                converter = nc
            for i in self.ress:
                for res in i.values():
                    res.structure = S
                    pid = res.pdb_residue.get_full_id()
                    pids = numcon.PDB_id.from_string(pid[2] + str(pid[3][1]) + pid[3][2])
                    res.ind = nc.get_ind(pids)
                    s = res.select()
                    self.assertEquals(len(s.ids), 1)
                    self.assertEquals(pids, s.ids[0])

        @testing(monomer.MonomerChainable.adjusted_length)
        def test_adjusted_length(self):
            ress = filter(lambda x: any(isinstance(key, monomer.Residue) for key in x), self.ress)
            for i in zip(ress[:-1], ress[1:]):
                m1 = i[0][monomer.Residue]
                m2 = i[1][monomer.Residue]
                m1.next_monomer = m2
                m2.previous_monomer = m1
            for i in self.ress:
                if i in ress:
                    self.assertTrue(i[monomer.Residue].adjusted_lenght() <= 3)
                else:
                    if monomer.Residue in i:
                        self.assertIsNone(i[monomer.Residue].adjusted_length())

    return MonomerTestBasic


def make_monomertest(strname, cls):
    """ Create and return a MonomerTest test case for a given structure and monomer class. """

    @testing(cls)
    @testing(monomer.Monomer)
    @testing(monomer.ABCMetamonomer)
    @testing(monomer.ABCMetamonomer.__call__)
    @testing(monomer.Monomer.__metaclass__)
    @testing(monomer.Monomer.__metaclass__.__class__)
    # TO I believe four above units are tested here
    @testing(monomer.MonomerChainable)
    @test_name_append(cls, strname)
    class MonomerTest(unittest.TestCase):
        cont_excl = {
            '1no5': [52], '1pxq': [], '2lp2': [], '3ftk': [], '3lgb': [],
            '3tk0': [], '1asz': [], '1gax': [], '3g88': [], '3m6x': [], '3npn': [38]}

        def setUp(self):
            self.load_mers(strname, data_dir + '%s.pdb' % strname, cls)

        #~ @testing(monomer.MonomerChainable.is_next)
        #~ def test_next(self):
            #~ ww = []
            #~ for pi, p in enumerate(self.l):
                #~ for ni, n in enumerate(self.l):
                    #~ if pi < ni:
                        #~ with warnings.catch_warnings(record=True) as w:
                            #~ v = p.is_next(n)
                            #~ if len(w):
                                #~ ww += w

                        #~ if ni - pi != 1:
                            #~ self.assertFalse(
                                #~ v, "Mers %s %s are not connected." %
                                #~ #(str(self.pdbl[pi]), str(self.pdbl[ni])))
                                    #~ #TO -- hoping for more informable msg
                                #~ (str(p), str(n)))
                        #~ else:
                            #~ if not pi in self.cont_excl.get(self.pdb_structure.get_id(), []):
                                #~ self.assertTrue(
                                    #~ v, "Mers %s %s are connected." %
                                    #~ #(str(self.pdbl[pi]), str(self.pdbl[ni])))
                                    #~ #TO -- hoping for more informable msg
                                    #~ (str(p), str(n)))

            #~ syntax_check.warning_message(self, ww)
        #TO -- is_next uses attribute 'next_monomer" which is set by Structure.__init__
        #so it's not going to work with unbound mers used here

        def load_mers(self, name, filename, cls):
            self.pdb_structure = Bio.PDB.PDBParser(
                QUIET=True).get_structure(name, filename)

            self.pdbl = []
            self.l = []

            for res in self.pdb_structure.get_residues():
                res_id = res.get_id()[0]
                if not res_id.startswith('H_') and not res_id.startswith('W'):
                    try:
                        self.pdbl.append(res)
                        self.l.append(cls(res))
                    except KeyError as e:
                        self.assertTrue(str(e).strip() not in res, "Monomer %s doesn't lack %s, but programe failed to create it (struc: %s)" % (res.get_id(), str(e), self.pdb_structure.id))

        @testing(monomer.Monomer.indicators)
        @testing(monomer.Monomer.representation)
        def test_indicators(self):
            for n in self.l:
                for name in n.indicators:
                    self.assertIsInstance(getattr(n, name), geometry.Coord)

                for c in n.representation:
                    self.assertIsInstance(c, geometry.Coord)

        @testing(monomer.Monomer.seq)
        @testing(monomer.Monomer.seq_1to3)
        def test_seq(self):
            for n in self.l:
                c = n.seq
                s3 = n.seq_1to3(c)
                self.assertIsInstance(c, types.StringType)
                self.assertEqual(len(c), 1)
                self.assertEqual(len(s3), 3)


        @testing(monomer.Monomer.seq3)
        @testing(monomer.Monomer.seq_3to1)
        def test_seq3(self):
            for n in self.l:
                c = n.seq3
                s1 = n.seq_3to1(c)
                self.assertIsInstance(c, types.StringType)
                self.assertEqual(len(c), 3)
                self.assertEqual(len(s1), 1)

        @testing(monomer.MonomerChainable.backbone)
        def test_backbone(self):
            for n in self.l:
                for c in n.backbone:
                    self.assertIsInstance(c, geometry.Coord)

        @testing(monomer.Monomer.calculate_rc)
        #~ @testing(monomer.MonomerChainable.calculate_rc)
        #~ @testing(monomer.MonomerOther.calculate_rc)
        #TO since these methods no longer exist, i believe
        #above lines are not necessary
        def test_calculate_rc(self):
            for m in self.l:
                try:
                    m.calculate_rc()
                except Exception as e:
                    self.fail("Test for %s borks (%s)." % (str(m), str(e)))

        @testing(monomer.Monomer.__iter__)
        @testing(monomer.Monomer.iter_atoms)
        def test_iterators(self):
            for (pdbr, r) in zip(self.pdbl, self.l):
                self.assertEqual(len(pdbr), len(list(r.iter_atoms())))

                for a in r.iter_atoms():
                    self.assertIn(a, r)

                for a in r.iter_atoms():
                    self.assertIn(a, r)

                for a in r.pseudoatoms.values():
                    self.assertIn(a, r)

                ll = list(r.pseudoatoms.values()) + list(r.atoms.values())
                for a in r:
                    self.assertIn(a, ll)

        @testing(monomer.Monomer.__getattr__)
        @unittest.expectedFailure
        def test_getsetattr(self):
            for m in self.l:
                for aname in itertools.chain(iter(m.atoms), iter(m.pseudoatoms)):
                    self.assertEqual(aname, aname.strip())
                    #TO -- commented to avoid deprecation warning
                    #~ self.assertEqual(m[aname], getattr(m, aname.lower()))
                    #~ self.assertEqual(m[aname], getattr(m, aname.upper()))

        if issubclass(cls, monomer.Residue):
            @testing(monomer.Residue.calculate_cbx)
            @testing(monomer.Monomer.__getitem__)
            def test_calculate_cbx(self):
                for n in self.l:
                    n.calculate_cbx()

                    if n.name == 'GLY':
                        self.assertAlmostEqual((n.cbx - n.atoms['CA ']).calculate_length(), 0)
                    else:
                        self.assertAlmostEqual((n.cbx - n.atoms['CB ']).calculate_length(), 1)

            @testing(monomer.Residue.ca)
            def test_ca(self):
                for n in self.l:
                    self.assertEqual(n.ca, n.atoms['CA '])

        if issubclass(cls, monomer.Nucleotide):
            @testing(monomer.Nucleotide.calculate_ring_center)
            @testing(monomer.Nucleotide.calculate_ring_plane)
            def test_ring_geom(self):
                for n in self.l:
                    n.calculate_ring_plane()
                    n.calculate_ring_center()

                    pl = n.ring_plane
                    rc = n.ring_center

                    rcp = pl.ort_projection(rc)

                    self.assertLess((rcp - rc).calculate_length(), 0.01)

    return MonomerTest


def make_monomercreatetest(strname):
    """ Create and return a MonomerTestBasic test case for a given structure and monomer class. """

    @test_name_append(strname)
    class MonomerCreateTest(unittest.TestCase):

        def setUp(self):
            self.pdb_structure = Bio.PDB.PDBParser(QUIET=True).get_structure(strname, data_dir + '%s.pdb' % strname)

        @testing(monomer.Monomer.create_monomers)
        @testing(monomer.Monomer.__len__)
        @testing(monomer.MonomerOther)
        @testing(monomer.MonomerOther.__init__)
        @testing(monomer.Residue)
        @testing(monomer.Nucleotide)
        @testing(monomer.Ion)
        @testing(monomer.Ion.__init__)
        @testing(monomer.Ligand)
        @testing(monomer.Ligand.__init__)
        def test_init(self):
            for res in self.pdb_structure.get_residues():
                res_id = res.get_id()[0]
                m = monomer.Monomer.create_monomers(res)
                if res_id.startswith('W'):
                    self.assertIsNone(m, "%s is water. No monomer should be created." % str(res.get_id()))
                    continue
                elif res_id.startswith('H_'):
                    #~ self.assertIsInstance(m, monomer.MonomerOther, "%s is hetero. MonomerOther should be created." % str(res.get_id()))
                    # since create_monomers has been changed and returns dictionary, I need to change the test:
                    self.assertTrue(any(isinstance(i, monomer.MonomerOther) for i in m.values()), "%s is hetero. MonomerOther should be created (struc %s)." % (str(res.get_id()), self.pdb_structure.id))
                else:

                    def hasitem(obj, name):
                        try:
                            obj[name]
                            return True
                        except KeyError:
                            return False
                    mch = [i for i in m.values() if isinstance(i, monomer.MonomerChainable)]
                    if len(mch) == 0:
                        for cls, additionally in [[monomer.Residue, ('CB',)], [monomer.Nucleotide, ('',)]]:
                            needed_atoms = cls.get_config('backbone_atoms') + additionally
                            if not all(i.strip() in res for i in needed_atoms):
                                continue
                            #~ self.assertIsInstance(m, monomer.MonomerChainable, "%s is regular. MonomerChainable should be created." % str(res.get_id()))
                            #TO -- same here:
                            self.assertTrue(False, "%s is regular. MonomerChainable should be created (struc %s)." % (str(res.get_id()), self.pdb_structure.id))

                    #~ self.assertEqual(len(m.atoms.values()), len(res), "%s %s" % (str(list(m)), str(list(res))))
                    #TO -- while m is not one monomer...
                    self.assertTrue(any(len(i.atoms) == len(res) for i in m.values()))
                    self.assertEqual(len(m), len(list(m)))

                for i in m.values():
                    tests_performed["monomer.%s" % i.__class__.__name__] = True


        #~ @testing(monomer.Monomer.create_monomers)
        #~ def test_create_monomer_failures(self):

            #~ def get_full_id():
                #~ return ('stru', 0, 'A', (' ', 0, ' '))

            #~ for res in self.pdb_structure.get_residues():
                #~ res.get_full_id = get_full_id
                #~ chainable = []
                #~ for monomer_type in MonomerChainable.__subclasses__():
                    #~ try:
                        #~ mers[monomer_type] = monomer_type(pdb_residue, structure_obj, warnings_)
                        #~ chainable.append(1)
                    #~ except:
                        #~ pass
                #~ if len(chainable) != 0:
                    #~ self.assertRaises(IncompleteChainableParticle, lambda: monomer.Monomer.create_monomers(res))
                #~ else:
                    #~ self.assertTrue(monomer.Monomer.create_monomers(res)[monomer.MonomerOther].__class__ in (monomer.Ion, monomer.Lignad))


    return MonomerCreateTest


def load_tests(loader, standard_tests, pattern):
    """ Add tests created by make_* functions for all structures. Return a complete TestSuite. """

    structures_rna = ['3npn']
    structures_prot = ['3m6x', '1no5', '1pxq', '2lp2',
                       '3ftk', '3g88', '3lgb', '3tk0']

    if fast:
        structures_rna = structures_rna[:1]
        structures_prot = structures_prot[:1]

    structures_any = structures_prot + structures_rna + []

    protbasic = unittest.TestSuite()
    prot = unittest.TestSuite()
    rnabasic = unittest.TestSuite()
    rna = unittest.TestSuite()
    create = unittest.TestSuite()

    for name in structures_prot:
        protbasic.addTests(
            loader.loadTestsFromTestCase(make_monomertestbasic(name, monomer.Residue)))
        prot.addTests(loader.loadTestsFromTestCase(
            make_monomertest(name, monomer.Residue)))

    for name in structures_rna:
        rnabasic.addTests(loader.loadTestsFromTestCase(
            make_monomertestbasic(name, monomer.Nucleotide)))
        rna.addTests(loader.loadTestsFromTestCase(
            make_monomertest(name, monomer.Nucleotide)))

    for name in structures_any:
        create.addTests(loader.loadTestsFromTestCase(
            make_monomercreatetest(name)))

    standard_tests.addTests(protbasic)
    standard_tests.addTests(rnabasic)
    standard_tests.addTests(prot)
    standard_tests.addTests(rna)
    standard_tests.addTests(create)

    standard_tests.addTests(loader.loadTestsFromTestCase(syntax_check.variants_tested(tests_performed)))

    return standard_tests


if __name__ == '__main__':
    if syntax_check.rip_argv('--fast'):
        fast = True

    unittest.main()
