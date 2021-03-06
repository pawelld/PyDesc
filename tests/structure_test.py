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
Unit tests for structure.py.

Usage:
    python structure_test.py [-v] [--skip-slow] [--fast]

    or

    python -m unittest [-v] structure_test
"""

import unittest
import random
import operator

import syntax_check
from syntax_check import notest, testing, test_name_append

import Bio.PDB

import warnings
import sys

import pydesc.structure as structure
import pydesc.selection as selection
import pydesc.monomer as monomer
import pydesc.numberconverter as numberconverter
import pydesc.warnexcept as warnexcept
import pydesc.config as config
import tests

config.ConfigManager.warnings_and_exceptions.class_filters.set("NoConfiguration", "ignore")
config.ConfigManager.warnings_and_exceptions.class_filters.set("LocalCopyAccess", "ignore")
config.ConfigManager.warnings_and_exceptions.class_filters.set("Info", "ignore")
config.ConfigManager.warnings_and_exceptions.class_filters.set("UnknownParticleName", "ignore")
config.ConfigManager.warnings_and_exceptions.class_filters.set("IncompleteChainableParticle", "ignore")

warnexcept.set_filters()

syntax_check.module = structure

notest(structure.AbstractStructure.rotate)
notest(structure.AbstractStructure.translate)
notest(structure.AbstractStructure.monomers)

notest(structure.Chain)

notest(structure.Contact.get_other_element)

notest(structure.AbstractDescriptor.create_coord_vector)
notest(structure.AbstractDescriptor.create_descriptors)

data_dir = tests.__path__[0] + '/data/test_structures/'
dcd_data_dir = tests.__path__[0] + '/data/dcd/'

skip_slow = False
fast = False

tests_performed = dict((x, False) for x in [
    'ElementChainable',
    'ElementOther',
    'ProteinDescriptor',
    'NucleotideDescriptor'
])

TestSyntax = syntax_check.module_syntax()


@testing(structure.StructureLoader)
class StructureLoaderTest(unittest.TestCase):

    """ Testcase for StructureLoader class. """

    structures = ['1asz', '1gax', '1no5', '1pxq', '2dlc', '2lp2',
                  '3ftk', '3g88', '3lgb', '3m6x', '3npn', '3tk0', '3umy']

    @testing(structure.StructureLoader.__init__)
    @testing(structure.StructureLoader.load_structure)
    def test_loader(self):
        """ Test StructureLoader.load_structure. """
        loader = structure.StructureLoader()
        for name in self.structures:
            with warnings.catch_warnings(record=True):
                struct = loader.load_structure(name)
            f = loader.handler.get_file(name)
            pdb_models = Bio.PDB.PDBParser(QUIET=True).get_structure(name, f)

            for s in struct:
                self.assertIsInstance(s, structure.Structure)

            self.assertEqual(len(struct), len(pdb_models))



def make_trajectorytest(strname):
    """Create and return a StructureTest testcase for a structures linked with dcd trajectories."""

    sl = structure.StructureLoader()

    class TrajectoryTest(unittest.TestCase):
        name = strname
        @classmethod
        def setUpClass(cls):
            cls.pdb_structure = sl.load_structure("mdm2", path=dcd_data_dir + cls.name + ".pdb")[0]

        @testing(structure.Structure.link_dcd_file)
        @testing(structure.Structure.disconnect_trajectory)
        @testing(structure.Structure.next_frame)
        @testing(structure.Structure.frame)
        def test_linking_trajectory(self):
            self.assertIsNone(self.pdb_structure.frame)
            self.pdb_structure.link_dcd_file(dcd_data_dir + self.name + ".dcd")
            fr = self.pdb_structure.frame
            self.pdb_structure.next_frame()
            self.assertEqual(fr + 1, self.pdb_structure.frame)
            self.assertIsNotNone(self.pdb_structure.frame)
            self.pdb_structure.disconnect_trajectory()
            self.assertIsNone(self.pdb_structure.frame)

    return TrajectoryTest


def make_structurebasictest(strname):
    """Create and return a StructureBasicTest testcase for a given structure."""
    @test_name_append(strname)
    class StructureBasicTest(unittest.TestCase):
        name = strname

        @testing(structure.AbstractStructure.__init__)
        @testing(structure.Structure.__init__)
        @testing(structure.Chain.__init__)
        def test_init(self):
            pdb_structure = Bio.PDB.PDBParser(
                QUIET=True).get_structure(self.name, data_dir + '%s.pdb' % self.name)
            converter = numberconverter.NumberConverter(pdb_structure)
            for model in pdb_structure:
                with warnings.catch_warnings(record=True) as wlist:
                    warnings.simplefilter("always")
                    structure.Structure(model, converter)
                    syntax_check.warning_message(self, wlist)

    return StructureBasicTest


def make_structuretest(strname):
    """Create and return a StructureTest testcase for a given structure."""
    @testing(structure.AbstractStructure)
    @testing(structure.Structure)
    @testing(structure.UserStructure)
    @testing(structure.Segment)
    @test_name_append(strname)
    class StructureTest(unittest.TestCase):
        name = strname

        @classmethod
        def setUpClass(cls):
            cls.pdb_structure = Bio.PDB.PDBParser(QUIET=True).get_structure(cls.name, data_dir + '%s.pdb' % cls.name)
            cls.converter = numberconverter.NumberConverter(cls.pdb_structure)
            cls.model = random.choice(cls.pdb_structure)
            with warnings.catch_warnings(record=True):
                cls.struct = structure.Structure(cls.model, cls.converter)

        @classmethod
        def tearDownClass(cls):
            del cls.struct
            del cls.model
            del cls.converter
            del cls.pdb_structure

        @testing(structure.AbstractStructure.__len__)
        def test_len(self):
            #~ self.assertEqual(len(self.struct), sum(map(len, self.model)))
            #TO water particles were taken under consideration in last version
            self.assertEqual(len(self.struct), sum(map(len, [filter(lambda x: True if x.get_id()[0] != 'W' else False, chain) for chain in self.model])))

        @testing(structure.Structure.get_secondary_structure)
        @testing(structure.Structure.get_simple_secondary_structure)
        @testing(structure.Structure.set_secondary_structure)
        def test_ss(self):
            self.struct.set_secondary_structure()
            ss = self.struct.get_secondary_structure()
            sss = self.struct.get_simple_secondary_structure()
            self.assertEqual(len(self.struct), len(ss))
            self.assertEqual(len(self.struct), len(sss))
            self.assertLessEqual(len(ss), 6)
            self.assertLessEqual(len(sss), 3)
            self.assertTrue(all(i in ('E', 'G', 'H', '-', 'S', 'T') for i in set(ss)))
            self.assertTrue(all(i in ('E', 'C', 'H') for i in set(sss)))

        @testing(structure.AbstractStructure.__iter__)
        def test_iter(self):
            l = list(iter(self.struct))

            self.assertEqual(len(l), len(self.struct))
            self.assertEqual(len(l), len(set(l)))

        def test_monomer_ind(self):
            for m in self.struct:
                pdb_id = numberconverter.PDB_id.from_pdb_residue(m.pdb_residue)
                self.assertEqual(m.ind, self.converter.get_ind(tuple(pdb_id)))

        @testing(structure.AbstractStructure.__getitem__)
        def test_getitem(self):
            for m in self.struct:
                self.assertEqual(self.struct[m.ind], m)

        def test_continuity(self):
            for mer in self.struct:
                if isinstance(mer, monomer.MonomerChainable):
                    if mer.next_monomer:
                        self.assertEqual(mer, mer.next_monomer.previous_monomer)
                    if mer.previous_monomer:
                        self.assertEqual(mer, mer.previous_monomer.next_monomer)

        @testing(structure.AbstractStructure.__getitem__)
        def test_getsliceunbound(self):
            whole = list(self.struct)
            pref = []
            for m in self.struct:
                slc = self.struct[m.ind:]
                slc1 = self.struct[:m.ind]
                self.assertItemsEqual(whole, pref + list(slc))
                self.assertEqual(len(whole), len(pref) + len(slc))
                self.assertItemsEqual(pref + [m], list(slc1))
                # TO structure slices take slice.stop mer!
                self.assertEqual(len(pref) + 1, len(slc1))
                pref.append(m)

        @testing(structure.AbstractStructure.next_monomer)
        @testing(structure.UserStructure.__init__)
        @testing(structure.Segment.__init__)
        @unittest.skipIf(skip_slow, "Takes too long")
        def test_getslicebound(self):
            step = 20
            step1 = 10
            whole = list(self.struct)
            for sg in range(0, len(whole), step):
                s = sg + random.randint(0, min(step - 1, len(whole) - sg - 1))
                for eg in range(s, len(whole), step1):
                    e = eg + random.randint(0, min(step1 - 1, len(whole) - eg - 1))
                    slc = self.struct[whole[s].ind:whole[e].ind]
                    self.assertItemsEqual(whole[s:e + 1], list(slc))

                    seg = True
                    for m1, m2 in zip(list(slc)[:-1], list(slc)[1:]):
                        with warnings.catch_warnings(record=True):
                            #~ if not m1.is_next(m2):
                                #~ seg = False
                                #~ self.assertIsNone(slc.next_monomer(m1))
                            #~ else:
                                #~ self.assertEqual(slc.next_monomer(m1), m2)
                            # TO is_next is deprecated, so:
                            if len(slc) == 1:
                                seg = True if isinstance(slc[0], monomer.MonomerChainable) else False
                                break
                            if m1.next_monomer == m2:
                                self.assertEqual(slc.next_monomer(m1), m2)
                            else:
                                seg = False
                                self.assertIsNone(slc.next_monomer(m1))
                    if seg:
                        self.assertIsInstance(slc, structure.Segment, "Slice is Userstructure, should be Segment: structure %s, slice: from %s to %s" % (str(self.struct), str(slc[0]), str(slc[-1])))

        @testing(structure.AbstractStructure.__add__)
        @testing(structure.AbstractStructure.__contains__)
        @testing(structure.UserStructure.__init__)
        @testing(structure.Segment.__init__)
        def test_add_in(self):
            whole = list(self.struct)

            slices = []
            for dummy_i in range(10):
                s = random.randint(0, len(whole) - 1)
                e = random.randint(s, len(whole) - 1)
                slices.append(self.struct[whole[s].ind:whole[e].ind])

            for dummy_i in range(20):
                k = random.randint(2, 10)
                sample = random.sample(slices, k)
                res = reduce(operator.add, sample)
                resset = reduce(operator.or_, map(set, sample))

                self.assertEqual(len(set(res)), len(list(res)), "Duplicate monomers after add.")
                self.assertSetEqual(set(res), resset)

                seg = True
                for m1, m2 in zip(list(res)[:-1], list(res)[1:]):
                    with warnings.catch_warnings(record=True):
                        #~ if not m1.is_next(m2):
                            #~ seg = False
                            #~ break
                        # TO is_next is deprecated
                        if not m1.next_monomer == m2:
                            seg = False
                            break
                if seg:
                    self.assertIsInstance(res, structure.Segment)

        @testing(structure.AbstractStructure.get_contact_map)
        @testing(structure.AbstractStructure.set_contact_map)
        @testing(structure.Contact.value)
        @unittest.skipIf(skip_slow, "Takes too long")
        def test_contactmap_and_contact_values(self):
            self.assertRaises(AttributeError, self.struct.get_contact_map)
            with warnings.catch_warnings(record=True) as wlist:
                warnings.simplefilter("always")
                self.struct.set_contact_map()

                syntax_check.warning_message(self, wlist)

            self.struct.get_contact_map()

            inds = map(operator.attrgetter('ind'), self.struct._monomers)

            config.ConfigManager.element.set("element_chainable_length", 3)

            for ind1 in inds:
                for ind2 in inds:
                    if ind1 == ind2 or self.struct[ind1].next_monomer == None or self.struct[ind2].next_monomer == None or self.struct[ind1].previous_monomer == None or self.struct[ind2].previous_monomer == None:
                        continue
                    c = structure.Contact(*[structure.ElementChainable(self.struct[i]) for i in (ind1, ind2)])
                    if ind2 in self.struct.contact_map.contacts[ind1]:
                        self.assertEqual(c.value, self.struct.contact_map.contacts[ind1][ind2])
                    else:
                        self.assertEqual(c.value, 0)

        @testing(structure.AbstractStructure.get_sequence)
        @testing(structure.Structure.get_sequence)
        def test_getsequence(self):
            for ch in self.struct.chains:
                seq = ch.get_sequence()
                chainable = filter(lambda x: isinstance(x, monomer.MonomerChainable), ch)
                self.assertEqual(len(seq), len(chainable), "Wrong len of sequence of %s chain" % ch.chain_char)

        @testing(structure.AbstractStructure.select)
        @testing(structure.Structure.select)
        def test_select(self):
            self.struct.select()

        @testing(structure.Segment)
        @testing(structure.Segment.select)
        @testing(structure.Segment.start)
        @testing(structure.Segment.end)
        def test_segment(self):
            whole = list(self.struct)

            nseg = 0
            cnt = 0

            while cnt < 1000 and nseg < 100:
                s = random.randint(0, len(whole) - 2)
                e = random.randint(s + 1, len(whole) - 1)
                slc = self.struct[whole[s].ind:whole[e].ind]

                cnt += 1
                if isinstance(slc, structure.Segment):
                    nseg += 1

                    slc.select()
                    self.assertEqual(whole[s], slc.start)
                    self.assertEqual(whole[e], slc.end)

            self.assertTrue(nseg, "Random segment generation failed to generate any segments.")

        @testing(structure.Element)
        @testing(structure.Element.__init__)
        @testing(structure.Element.build)
        @testing(structure.ElementChainable)
        @testing(structure.ElementChainable.__init__)
        @testing(structure.ElementOther)
        @testing(structure.ElementOther.__init__)
        def test_element(self):
            chs = [list(ch) for ch in self.struct.chains]
            whole = reduce(operator.add, chs)
            valerr = False
            msg = []

            config.ConfigManager.element.set("element_chainable_length", 5)

            for (i, m) in enumerate(whole):
                if isinstance(m, monomer.MonomerChainable):
                    willfail = False
                    mer_ch = max([ch for ch in chs if m in ch])
                    index = mer_ch.index(m)
                    if index < 2 or index >= len(mer_ch) - 2:
                        willfail = True
                    else:
                        try:
                            s = mer_ch[index - 2]
                            e = mer_ch[index + 2]
                        except IndexError:
                            willfail = True
                        else:
                            for m1, m2 in zip(mer_ch[(index - 2):(index + 2)], mer_ch[(index - 1):(index + 3)]):
                                with warnings.catch_warnings(record=True):
                                    if m1.next_monomer == m2:
                                        continue
                                    willfail = True
                                    break

                    tests_performed['ElementChainable'] = True
                    if willfail:
                        try:
                            self.assertRaises(ValueError, lambda: structure.ElementChainable(m))
                        except:
                            msg.append((sys.exc_info(), m))
                            valerr = True
                    else:
                        el = structure.ElementChainable(m)
                        elb = structure.Element.build(m)
                        self.assertEqual(type(el), type(elb))
                        self.assertEqual(len(el), config.ConfigManager.element.element_chainable_length)
                        self.assertEqual(el.start, s)
                        self.assertEqual(el.end, e)

                elif isinstance(m, monomer.MonomerOther):
                    tests_performed['ElementOther'] = True
                    el = structure.ElementOther(m)

            if valerr:
                self.fail("Unexpected exceptions caught for mer %i:\n %s" % (msg[0][1].ind, str(msg[0][0])))

        @testing(structure.Contact)
        @testing(structure.Contact.__init__)
        @testing(structure.Contact.__sub__)
        @unittest.expectedFailure
        def test_contact_future(self):
            # test fails because of lack of pydesc.contacts imported
            # their are not imported in order to avoid false-positive result
            # of set_contact_map test in presence of import errors
            whole = list(self.struct)

            for i in range(100):
                r1 = random.choice(whole)
                r2 = random.choice(whole)

                if r1 == r2:
                    continue

                try:
                    el1 = structure.ElementChainable(r1)
                    el2 = structure.ElementChainable(r2)
                except:
                    continue

                def check(c, v, crit):
                    self.assertEqual((tuple(map(lambda x: x.central_monomer, c.elements)), c.value, c.criterion), ((r1, r2), v, crit))

                c = structure.Contact(r1, r2)
                check(c, None, None)

                val = syntax_check.expando()
                c = structure.Contact(r1, r2, value=val)
                check(c, val, None)

                cc = contacts.ContactCriterion()
                c = structure.Contact(r1, r2, contact_criterion=cc)
                check(c, None, cc)

                self.assertEqual(c - el1, el2)
                self.assertEqual(c - el2, el1)

                self.assertTrue(isinstance(c.select(), selection.SelectionsUnion) or isinstance(c.select(), selection.Range))

        @testing(structure.Contact)
        @testing(structure.Contact.__init__)
        @testing(structure.Contact.get_other_element)
        @testing(structure.Contact.select)
        def test_contact(self):
            whole = list(self.struct)

            for i in range(100):
                r1, r2 = random.sample(whole, 2)

                try:
                    el1 = structure.ElementChainable(r1)
                    el2 = structure.ElementChainable(r2)
                except:  # pylint: disable=W0702
                    continue

                def check(c, v, crit):
                    #~ self.assertEqual((tuple(map(lambda x: x.central_monomer, c.elements)), c.value, c.criterion), ((r1, r2), v, crit))
                    # TO contact no longer have criterion attr, and value property doesn't work in this test due to lack of monomers' derived_from attr named contact_map
                    # which is coused by test design
                    self.assertEqual(sorted(map(operator.attrgetter('central_monomer'), c.elements)), sorted([r1, r2]))

                c = structure.Contact(el1, el2)
                check(c, None, None)

                self.assertEqual(c.get_other_element(el1).central_monomer.ind, el2.central_monomer.ind)
                self.assertEqual(c.get_other_element(el2).central_monomer.ind, el1.central_monomer.ind)

                sc = c.select()
                self.assertEqual(len(sc.specify(c).ids), len(c))

        @testing(structure.AbstractStructure.adjusted_number)
        @testing(structure.Segment.adjusted_number)
        @testing(structure.UserStructure.adjusted_number)
        def test_adjusted_number(self):
            whole = list(self.struct)

            cnt = 0

            while cnt < 100:
                s = random.randint(0, len(whole) - 2)
                e = random.randint(s + 1, len(whole) - 1)
                slc = self.struct[whole[s].ind:whole[e].ind]

                cnt += 1
                if isinstance(slc, structure.Segment):
                    adj = slc.adjusted_number()
                    inds = map(operator.attrgetter('ind'), slc)
                    for i in inds[1:]:
                        self.assertTrue(slc[inds[0]:i].adjusted_number() <= adj)
                    for i in inds[:-1]:
                        self.assertTrue(slc[i:inds[-1]].adjusted_number() <= adj)
                else:
                    conts = 0
                    for i, j in zip(slc[:-2], slc[-len(slc) + 1:]):
                        if i.next_monomer == j:
                            continue
                        if isinstance(i, monomer.MonomerChainable):
                            conts += 1
                    self.assertTrue(conts <= slc.adjusted_number())

        @testing(structure.AbstractStructure.create_pdbstring)
        @testing(structure.AbstractStructure.save_pdb)
        def test_pdbstring(self):
            stg = self.struct.create_pdbstring()
            self.struct.save_pdb('stc_test.pdb')
            nstc = structure.StructureLoader().load_structure('test', path='stc_test.pdb')[0]
            stg2 = nstc.create_pdbstring()
            self.assertEqual(stg.read(), stg2.read())

    return StructureTest


def make_descriptortest(strname):
    """Create and return a StructureTest testcase for a given structure."""

    @unittest.skipIf(skip_slow, "Takes too long")
    @test_name_append(strname)
    class DescriptorTest(unittest.TestCase):
        name = strname

        @classmethod
        def setUpClass(cls):
            cls.pdb_structure = Bio.PDB.PDBParser(QUIET=True).get_structure(cls.name, data_dir + '%s.pdb' % cls.name)
            cls.converter = numberconverter.NumberConverter(cls.pdb_structure)
            cls.model = random.choice(cls.pdb_structure)
            with warnings.catch_warnings(record=True):
                cls.struct = structure.Structure(cls.model, cls.converter)
                #~ crit = contacts.ContactsAlternative(contacts.CaContact(), contacts.CbxContact(), contacts.RaContact())
                #~ cls.struct.set_contact_map(crit)
                cls.struct.set_contact_map()

        @classmethod
        def tearDownClass(cls):
            del cls.struct
            del cls.model
            del cls.converter
            del cls.pdb_structure

        @unittest.expectedFailure
        def test_descriptor_future(self):
            whole = list(self.struct)
            valerr = False
            msg = []

            for (i, m) in enumerate(whole):
                if isinstance(m, monomer.Nucleotide):
                    desc_class = structure.NucleotideDescriptor
                    name = 'NucleotideDescriptor'
                elif isinstance(m, monomer.Residue):
                    desc_class = structure.ProteinDescriptor
                    name = 'ProteinDescriptor'
                else:
                    continue

                willfail = False

                try:
                    structure.ElementChainable(m)
                except:
                    willfail = True

                tests_performed[name] = True
                if willfail:
                    try:
                        self.assertRaises(warnexcept.DiscontinuityError, lambda: desc_class.build(m))
                    except:
                        msg.append(sys.exc_info())
                        valerr = True
                    continue

                desc_class.build(m)

            if valerr:
                self.fail("Unexpected exceptions caught:\n %s" % str(msg))

        @testing(structure.AbstractDescriptor)
        @testing(structure.AbstractDescriptor.__init__)
        @testing(structure.AbstractDescriptor.select)
        @testing(structure.AbstractDescriptor.build)
        @testing(structure.NucleotideDescriptor)
        @testing(structure.NucleotideDescriptor.build)
        @testing(structure.NucleotideDescriptor.__init__)
        @testing(structure.ProteinDescriptor)
        @testing(structure.ProteinDescriptor.build)
        @testing(structure.ProteinDescriptor.__init__)
        def test_descriptor(self):
            whole = list(self.struct)

            for (i, m) in enumerate(whole):
                if isinstance(m, monomer.Nucleotide):
                    desc_class = structure.NucleotideDescriptor
                    name = 'NucleotideDescriptor'
                elif isinstance(m, monomer.Residue):
                    desc_class = structure.ProteinDescriptor
                    name = 'ProteinDescriptor'
                else:
                    continue

                try:
                    el = structure.ElementChainable(m)
                except:
                    continue

                tests_performed[name] = True

                if self.struct.contact_map.get_monomer_contacts(m) == []:
                    self.assertRaises(ValueError, lambda: desc_class.build(el))
                    continue
                staph = False
                for i in self.struct.contact_map.get_monomer_contacts(m):
                    try:
                        structure.Contact(i[0], i[1], self.struct)
                    except:
                        staph = True
                        break
                    # TO sometimes there are contcts in contact map, but mers contacted with central monomer are to close to edge to create elements
                if staph:
                    continue
                desc = desc_class.build(el, self.struct.contact_map)
                absdesc = structure.AbstractDescriptor.build(el)
                self.assertEqual(type(desc), type(absdesc))
                self.assertEqual(len(desc), len(absdesc))

                def el_in_desc(el, desc):
                    for m in el:
                        self.assertIn(m, desc)

                el_in_desc(el, desc)

                self.assertEquals(list(desc.central_element), list(el))

                secondary_contacts = filter(lambda x: False if el.central_monomer.ind in [i.central_monomer.ind for i in x.elements] else True, desc.contacts)
                primary_inds = [i.central_monomer.ind for i in reduce(operator.add, [i.elements for i in desc.contacts if i not in secondary_contacts])]
                for c in desc.contacts:
                    try:
                        el_in_desc(c.get_other_element(el), desc)
                    except ValueError:
                        self.assertTrue(c in secondary_contacts, '%s contains elements settled by mers that are not in contact with central monomer' % str(desc))
                        self.assertTrue(any(el_.central_monomer.ind in primary_inds for el_ in c.elements), '%s elements are not on a list of primary elements of %s' % (str(c), str(desc)))

                for s in desc.segments:
                    self.assertIsInstance(s, structure.Segment)
                    el_in_desc(s, desc)

                for c in desc.contacts:
                    for el in c.elements:
                        if isinstance(el, structure.ElementChainable):
                            ok = False
                            for s in desc.segments:
                                if set(el).issubset(s):
                                    ok = True
                                    break
                            self.assertTrue(ok, "Element %s is not contained in any segment" % str(el))

                if len(desc.contacts):
                    self.assertSetEqual(set(desc._monomers), set(reduce(operator.add, desc.contacts)))
                else:
                    self.assertSetEqual(set(desc._monomers), set(el))
                if isinstance(desc, structure.ProteinDescriptor):
                    self.assertSetEqual(set(desc._monomers), set(reduce(operator.add, desc.segments)))
                else:
                    self.assertSetEqual(set(filter(lambda i: isinstance(i, monomer.MonomerChainable), desc._monomers)), set(reduce(operator.add, desc.segments)))

                self.assertEqual(len(list(desc)), len(set(desc)))


                desc.select()

    return DescriptorTest


def load_tests(loader, standard_tests, pattern):
    """ Add tests created by make_* functions for all structures. Return a complete TestSuite. """
    structures = ['1asz', '1gax', '1no5', '1pxq', '2dlc', '2lp2',
                  '3ftk', '3g88', '3lgb', '3m6x', '3npn', '3tk0', '3umy']
    dcd_structures = ['mdm2']

    if fast:
        structures = ['4jgn']

    basic = unittest.TestSuite()

    for name in structures:
        basic.addTests(loader.loadTestsFromTestCase(make_structurebasictest(name)))
        basic.addTests(loader.loadTestsFromTestCase(make_structuretest(name)))
        basic.addTests(loader.loadTestsFromTestCase(make_descriptortest(name)))

    for name in dcd_structures:
        basic.addTests(loader.loadTestsFromTestCase(make_trajectorytest(name)))

    standard_tests.addTests(basic)

    standard_tests.addTests(loader.loadTestsFromTestCase(syntax_check.variants_tested(tests_performed)))

    return standard_tests

if __name__ == '__main__':
    if syntax_check.rip_argv('--skip-slow'):
        skip_slow = True

    if syntax_check.rip_argv('--fast'):
        fast = True

    unittest.main()
