import unittest
from abpytools import ChainCollection, Chain
import operator
import os
from glob import glob
from . import read_sequence, check_connection, ABNUM_URL, IGBLAST_URL


class ChainCollectionCore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.antibody_collection_1_name = 'test'
        cls.chain_test_sequence = read_sequence('./tests/Data/chain_collection_fasta_test.fasta')

    def test_ChainCollection_length_0(self):
        antibody_collection = ChainCollection()
        self.assertEqual(len(antibody_collection), 0)

    def test_ChainCollection_input_exception_1(self):
        # when ChainCollection.object_list is instantiated with
        # something other than a list it throws an error
        self.assertRaises(ValueError, ChainCollection, 0)

    def test_ChainCollection_input_exception_2(self):
        # when ChainCollection.object_list is instantiated with
        #  a list with non Chain objects it throws an error
        self.assertRaises(ValueError, ChainCollection, [Chain(sequence=""), 0])

    def test_ChainCollection_input_exception_3(self):
        # when ChainCollection is instantiated with static method
        # .load_from_fasta with an invalid file path it throws an error
        self.assertRaises(ValueError, ChainCollection.load_from_fasta, './tests/Data/NonExistentFile.fasta')

    def test_ChainCollection_input_exception_4(self):
        # when ChainCollection is instantiated with .load_from_file with
        # path to a file that does not have a .fasta or .json extension
        # it throws an error
        self.assertRaises(ValueError, ChainCollection.load_from_file, './tests/Data/__init__.py')

    def test_ChainCollection_input_1(self):
        # instantiate ChainCollection with a Chain (empty) object
        # this doesn't make any sense and raises an error
        self.assertRaises(ValueError, ChainCollection, [Chain(sequence="")])

    def test_ChainCollection_input_2(self):
        # instantiate ChainCollection with a loaded Chain object
        test_chain = Chain(sequence=self.chain_test_sequence)
        test_collection = ChainCollection(antibody_objects=[test_chain])
        self.assertIsInstance(test_collection, ChainCollection)

    def test_ChainCollection_load_fasta_exception(self):
        # throws error when reading a file with fasta extention,
        # but with the wrong format
        self.assertRaises(ValueError, ChainCollection.load_from_file, './tests/Data/NotAFASTAFile.fasta')

    def test_ChainCollection_chain(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json')
        self.assertEqual(antibody_collection_1.chain, 'heavy')

    @unittest.skipUnless(check_connection(URL=IGBLAST_URL), 'No internet connection, skipping test.')
    def test_ChainCollection_chain_2(self):
        # checks if the chain type is read properly from a Chain object
        test_chain = Chain(sequence=self.chain_test_sequence)
        test_chain.load()
        test_collection = ChainCollection(antibody_objects=[test_chain])
        self.assertEqual(test_collection.chain, 'heavy')

    def test_ChainCollection_proto_io_1(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.save(file_format='pb2', path='./tests/chain_collection_1_heavy')
        self.assertTrue(os.path.isfile('./tests/chain_collection_1_heavy.pb2'))

    def test_ChainCollection_proto_io_2(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/chain_collection_1_heavy.pb2',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.names[0], 'test')

    def test_ChainCollection_n_ab(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.n_ab, 1)

    def test_ChainCollection_numbering_scheme(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.numbering_scheme, 'chothia')

    def test_ChainCollection_numbering_scheme_kabat(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.set_numbering_scheme('kabat', realign=False)
        self.assertEqual(antibody_collection_1.numbering_scheme, 'kabat')

    def test_ChainCollection_Hmatrix_shape(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        # if this fails it means that abysis has been updated
        self.assertEqual(antibody_collection_1.hydrophobicity_matrix().shape, (1, 158))

    @unittest.skipUnless(check_connection(URL=ABNUM_URL), 'No internet connection, skipping test.')
    def test_ChainCollection_Hmatrix_calculation(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_fasta_test.fasta',
                                                               numbering_scheme='chothia')
        self.assertEqual(antibody_collection_1.hydrophobicity_matrix().shape, (1, 158))

    def test_ChainCollection_sequence_length(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(len(antibody_collection_1.sequences), 1)

    def test_ChainCollection_obj_length(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(len(antibody_collection_1), 1)

    def test_ChainCollection_slicing_1_obj(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        # if returning a single chain abpytools automatically creates a new Chain object
        self.assertIsInstance(antibody_collection_1[0], Chain)

    def test_ChainCollection_slicing_2_obj(self):
        antibody_collection_1 = ChainCollection.load_from_file(
            path='./tests/Data/chain_collection_heavy_2_sequences.json', show_progressbar=False, verbose=False)
        # slicing multiple sequences returns a ChainCollection object
        self.assertIsInstance(antibody_collection_1[[0, 1]], ChainCollection)

    def test_ChainCollection_cdr_regions_part1(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertCountEqual(antibody_collection_1.ab_region_index().keys(),
                              [self.antibody_collection_1_name])

    def test_ChainCollection_cdr_regions_part2(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertCountEqual(antibody_collection_1.ab_region_index()[self.antibody_collection_1_name],
                              ['CDR', 'FR'])

    def test_ChainCollection_cdr_regions_part3_cdr(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertCountEqual(antibody_collection_1.ab_region_index()[self.antibody_collection_1_name]['CDR'],
                              ['CDR1', 'CDR2', 'CDR3'])

    def test_ChainCollection_cdr_regions_part3_fr(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertCountEqual(antibody_collection_1.ab_region_index()[self.antibody_collection_1_name]['FR'],
                              ['FR1', 'FR2', 'FR3', 'FR4'])

    def test_ChainCollection_total_charge(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertAlmostEqual(antibody_collection_1.total_charge[self.antibody_collection_1_name], 1.3278508)

    def test_ChainCollection_igblast_parser_germline(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.igblast_local_query('tests/Data/chain_collection_1_igblast.html')
        self.assertEqual(antibody_collection_1.germline[self.antibody_collection_1_name][0], 'IGHV4-34*01')

    def test_ChainCollection_igblast_parser_germline_score(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.igblast_local_query('tests/Data/chain_collection_1_igblast.html')
        self.assertAlmostEqual(antibody_collection_1.germline[self.antibody_collection_1_name][1], 9.11e-69,
                               delta=10e-9)

    @unittest.skipUnless(check_connection(URL=IGBLAST_URL), 'No internet connection, skipping test.')
    def test_ChainCollection_igblast_server_query_germline(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.igblast_server_query(show_progressbar=False)
        self.assertEqual(antibody_collection_1.germline[self.antibody_collection_1_name][0], 'IGHV4-34*01')

    @unittest.skipUnless(check_connection(URL=IGBLAST_URL), 'No internet connection, skipping test.')
    def test_ChainCollection_igblast_server_query_score(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.igblast_server_query(show_progressbar=False)
        self.assertAlmostEqual(antibody_collection_1.germline[self.antibody_collection_1_name][1], 9.11e-69,
                               delta=10e-9)

    @unittest.skipUnless(check_connection(URL=IGBLAST_URL), 'No internet connection, skipping test.')
    def test_ChainCollection_igblast_server_query_identity(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.igblast_server_query(show_progressbar=False)
        self.assertEqual(antibody_collection_1.germline_identity[self.antibody_collection_1_name]['Total'], 96.9)

    def test_ChainCollection_slicing(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertIsInstance(antibody_collection_1.get_object('test'), Chain)

    @unittest.skipUnless(check_connection(URL=ABNUM_URL), 'No internet connection, skipping test.')
    def test_Chain_abysis_parser(self):
        antibody = ChainCollection.load_from_file(path='./tests/Data/chain_collection_fasta_test.fasta',
                                                  numbering_scheme='chothia', verbose=False, show_progressbar=False)
        self.assertEqual(antibody.chain, 'heavy')

    @unittest.skipUnless(check_connection(URL=ABNUM_URL), 'No internet connection, skipping test.')
    def test_Chain_abysis_parser_chothia(self):
        antibody = ChainCollection.load_from_file(path='./tests/Data/chain_collection_fasta_test.fasta',
                                                  numbering_scheme='chothia', verbose=False, show_progressbar=False)
        self.assertEqual(antibody.numbering_table(as_array=True)[0][-1], '-')

    @unittest.skipUnless(check_connection(URL=ABNUM_URL), 'No internet connection, skipping test.')
    def test_Chain_abysis_parser_kabat(self):
        antibody = ChainCollection.load_from_file(path='./tests/Data/chain_collection_fasta_test.fasta',
                                                  numbering_scheme='kabat', verbose=False, show_progressbar=False)
        self.assertEqual(antibody.numbering_table(as_array=True)[0][-1], '-')

    def test_ChainCollection_numbering_tableDataFrame(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.numbering_table(as_array=False)['CDR1']['H32'].values[0], 'Y')

    def test_ChainCollection_numbering_table_shape_np(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.numbering_table(as_array=True).shape, (1, 158))

    def test_ChainCollection_numbering_table_shape_pd(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.numbering_table(as_array=False).shape, (1, 158))

    def test_ChainCollection_numbering_table_region_pd(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(
            antibody_collection_1.numbering_table(region='CDR1').loc[self.antibody_collection_1_name].values[-1], 'Y')

    def test_ChainCollection_numbering_table_region_np(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.numbering_table(as_array=True, region='CDR1')[0][-1], 'Y')

    def test_ChainCollection_numbering_table_fr_region(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.numbering_table(region='FR1').loc['test'].values[0], 'Q')

    def test_ChainCollection_molecular_weight(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertAlmostEqual(antibody_collection_1.molecular_weights(monoisotopic=False)[0], 20029.85217699999)

    def test_ChainCollection_molecular_weight_monoisotopic(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertAlmostEqual(antibody_collection_1.molecular_weights(monoisotopic=True)[0], 20042.1121)

    def test_ChainCollection_ec(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertAlmostEqual(antibody_collection_1.extinction_coefficients(reduced=False)[0], 52410.0)

    def test_ChainCollection_ec_reduced(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertAlmostEqual(antibody_collection_1.extinction_coefficients(reduced=True)[0], 52160.0)

    def test_ChainCollection_charge(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertAlmostEqual(antibody_collection_1.charge.sum(), 1.7497642167513607)

    def test_ChainCollection_get_object_exception(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertRaises(ValueError, antibody_collection_1.get_object, 'foo')

    def test_ChainCollection_get_object_1(self):
        # check if get_object returns a Chain object
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertIsInstance(antibody_collection_1.get_object('test'), Chain)

    def test_ChainCollection_get_object_2(self):
        # check if get_object returns a Chain object and keeps the information (i.e. name)
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.get_object('test').name, 'test')

    def test_ChainCollection_add(self):
        # check if adding two ChainCollection objects with one sequence each
        # results in a ChainCollection object with two sequences
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_2 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_2_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_3 = antibody_collection_1 + antibody_collection_2
        self.assertEqual(antibody_collection_3.n_ab, 2)

    @unittest.skipUnless(check_connection(URL=ABNUM_URL), 'No internet connection, skipping test.')
    def test_ChainCollection_add_exception_1(self):
        # check if adding two ChainCollection objects with one sequence each
        # results in a ChainCollection object with two sequences
        antibody_chothia = ChainCollection.load_from_file(path='./tests/Data/chain_collection_fasta_test.fasta',
                                                          numbering_scheme='chothia',
                                                          show_progressbar=False, verbose=False)
        antibody_kabat = ChainCollection.load_from_file(path='./tests/Data/chain_collection_fasta_test.fasta',
                                                        numbering_scheme='kabat',
                                                        show_progressbar=False, verbose=False)
        self.assertRaises(ValueError, operator.add, antibody_chothia, antibody_kabat)

    @unittest.skipUnless(check_connection(URL=ABNUM_URL), 'No internet connection, skipping test.')
    def test_ChainCollection_add_exception_2(self):
        antibody_chothia = ChainCollection.load_from_file(path='./tests/Data/chain_collection_fasta_test.fasta',
                                                          numbering_scheme='chothia', show_progressbar=False,
                                                          verbose=False)
        antibody_kabat = Chain(sequence=read_sequence('./tests/Data/chain_collection_fasta_test.fasta'),
                               numbering_scheme='kabat')
        antibody_kabat.load()
        self.assertRaises(ValueError, operator.add, antibody_chothia, antibody_kabat)

    def test_ChainCollection_add_exception_3(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        self.assertRaises(ValueError, operator.add, antibody_collection_1, 0)

    @unittest.skipUnless(check_connection(URL=ABNUM_URL), 'No internet connection, skipping test.')
    def test_ChainCollection_fasta(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.save(file_format='fasta', path='./tests/SaveTest')
        antibody_collection_2 = ChainCollection.load_from_file(path='./tests/SaveTest.fasta',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.sequences[0], antibody_collection_2.sequences[0])

    def test_ChainCollection_json(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.save(file_format='json', path='./tests/SaveTest')
        antibody_collection_2 = ChainCollection.load_from_file(path='./tests/SaveTest.json',
                                                               show_progressbar=False, verbose=False)
        self.assertEqual(antibody_collection_1.sequences[0], antibody_collection_2.sequences[0])

    def test_ChainCollection_append_1(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_2 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_2_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.append(antibody_collection_2)
        self.assertEqual(antibody_collection_1.n_ab, 2)

    def test_ChainCollection_append_2(self):
        antibody_collection_1 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_1_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_2 = ChainCollection.load_from_file(path='./tests/Data/chain_collection_2_heavy.json',
                                                               show_progressbar=False, verbose=False)
        antibody_collection_1.append(antibody_collection_2)
        self.assertEqual(antibody_collection_1.hydrophobicity_matrix().shape, (2, 158))

    @classmethod
    def tearDownClass(cls):
        for name in glob('./tests/*'):
            if name.split('.')[-1] != 'py' and os.path.isfile(name):
                os.remove(name)
