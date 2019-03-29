import filecmp
import os
import unittest

import pandas as pd
import pyphant.Read_FMF.Read_fmf as rf
import pyphant.Write_FMF.Write_fmf as wf


class TestCreatingAndReadingFile(unittest.TestCase):
    # test reading in filenames with or without the fmf suffix

    def testSuffix(self):
        # should not be able to open "fffff" without .fmf
        def openfile():
            fh = wf.create_file("fffff")
            fh.close()
            f = open('fffff', 'r')
            f.close()

        self.assertRaises(FileNotFoundError, openfile)
        os.remove("fffff.fmf")

    def testSuffix2(self):
        # should not be able to open file "fmf" without .fmf
        def openfile():
            fh = wf.create_file("fmf")
            fh.close()
            f = open('fmf', 'r')
            f.close()

        self.assertRaises(FileNotFoundError, openfile)
        os.remove("fmf.fmf")

    def testSuffix3(self):
        # should be able to open file "fffmf.fmf"
        fh = wf.create_file("fffmf")
        fh.close()
        f = open('fffmf.fmf', 'r')
        f.close()
        os.remove("fffmf.fmf")

    def testSuffix4(self):
        # should be able to open file "f.fmf"
        fh = wf.create_file("f.fmf")
        fh.close()
        f = open('f.fmf', 'r')
        f.close()
        os.remove("f.fmf")

    def testpath(self):
        # should be able to open file at a different place "f.fmf"
        fh = wf.create_file("./f.fmf")
        fh.close()
        f = open("./f.fmf", 'r')
        f.close()
        os.remove("./f.fmf")


class TestWriteHeader(unittest.TestCase):
    # test if given various header arguments, correctly writes the appropriate header
    def testHeader1(self):
        f = open("testheader.fmf", "w+")
        wf.append_header(f, 1.0, ";", None, None)
        f.close()

        f = open("testheader.fmf", "r")
        header = f.readline()
        f.close()
        os.remove("testheader.fmf")
        self.assertEqual("; -*- fmf-version: 1.0 -*- \n", header)

    def testHeader2(self):
        f = open("testheader.fmf", "w+")
        wf.append_header(f, 1.0, ";", encoding="uft-8", delimiter=None)
        f.close()

        f = open("testheader.fmf", "r")
        header = f.readline()
        f.close()
        os.remove("testheader.fmf")
        self.assertEqual("; -*- fmf-version: 1.0; encoding: uft-8 -*- \n", header)

    def testHeader3(self):
        f = open("testheader.fmf", "w+")
        wf.append_header(f, 1.0, ";", encoding="uft-8", delimiter="\t")
        f.close()

        f = open("testheader.fmf", "r")
        header = f.readline()
        f.close()
        os.remove("testheader.fmf")
        self.assertEqual("; -*- fmf-version: 1.0; encoding: uft-8; delimiter: \\t -*- \n", header)

    def testHeader4(self):
        f = open("testheader.fmf", "w+")
        wf.append_header(f, 1.0, ";", None, delimiter="\t")
        f.close()

        f = open("testheader.fmf", "r")
        header = f.readline()
        f.close()
        os.remove("testheader.fmf")
        self.assertEqual("; -*- fmf-version: 1.0; delimiter: \\t -*- \n", header)

    def testHeader5(self):
        f = open("testheader.fmf", "w+")
        wf.append_header(f, 1.0, ";", encoding=None, delimiter="whitespace")
        f.close()

        f = open("testheader.fmf", "r")
        header = f.readline()
        f.close()
        os.remove("testheader.fmf")
        self.assertEqual("; -*- fmf-version: 1.0; delimiter: whitespace -*- \n", header)

    def testHeader6(self):
        # test the comment character argument
        f = open("testheader.fmf", "w+")
        wf.append_header(f, 1.0, encoding="uft-8", delimiter="\t", comment="%")
        f.close()

        f = open("testheader.fmf", "r")
        header = f.readline()
        f.close()
        os.remove("testheader.fmf")
        self.assertEqual("% -*- fmf-version: 1.0; encoding: uft-8; delimiter: \\t -*- \n", header)


class TestSection(unittest.TestCase):
    # metadata = {'*reference': {"key1": "value1", "key2": "value2"}}

    def testSection1(self):
        # test single section
        metadata = {'*reference': {"key1": "value1", "key2": "value2"}}

        fh = open("testsection.fmf", "w+")
        wf.append_section(fh, metadata)
        fh.close()

        self.assertTrue(filecmp.cmp("testsection.fmf", "section1.fmf"))

        os.remove("testsection.fmf")

    def testSection2(self):
        # test multiple sections
        metadata = {'*reference': {"key1": "value1", "key2": "value2"},
                    '*data definitions': {"key1": "value1", "key2": "value2"}}

        fh = open("testsection.fmf", "w+")
        wf.append_section(fh, metadata)
        fh.close()

        self.assertTrue(filecmp.cmp("testsection.fmf", "section2.fmf"))

        os.remove("testsection.fmf")


class TestTables(unittest.TestCase):
    data = {"key1": [1, 2, 3], "key2": [4, 5, 6], "key3": [7, 8, 9]}
    data = pd.DataFrame(data)
    dict_data = {"A": data, "B": data}
    data_def = {"key1": "value1 [m]", "key2": "value2 [kg]", "key3": "value3 [s]"}
    data_pint = rf.pintify(data, data_def)
    dict_data_pint = {"A": data_pint, "B": data_pint}

    def testTable1(self):
        # test single df input
        fh = open("testtables.fmf", "w+")
        wf.append_tables(fh, self.data, ":G", "\t")
        fh.close()

        self.assertTrue(filecmp.cmp("testtables.fmf", "tables1.fmf"))

        os.remove("testtables.fmf")

    def testTable2(self):
        # test single pintarray input
        fh = open("testtables.fmf", "w+")
        wf.append_tables(fh, self.data_pint, ":G", "\t")
        fh.close()

        self.assertTrue(filecmp.cmp("testtables.fmf", "tables1.fmf"))

        os.remove("testtables.fmf")

    def testTable3(self):
        # test multiple df input
        fh = open("testtables.fmf", "w+")
        wf.append_tables(fh, self.dict_data, ":G", "\t")
        fh.close()

        self.assertTrue(filecmp.cmp("testtables.fmf", "tables2.fmf"))

        os.remove("testtables.fmf")

    def testTable4(self):
        # test multiple pintarray input
        fh = open("testtables.fmf", "w+")
        wf.append_tables(fh, self.dict_data_pint, ":G", "\t")
        fh.close()

        self.assertTrue(filecmp.cmp("testtables.fmf", "tables2.fmf"))

        os.remove("testtables.fmf")

    def testTable5a(self):
        # test different delimitter - dataframe
        fh = open("testtables.fmf", "w+")
        wf.append_tables(fh, self.data, ":G", ",")
        fh.close()

        self.assertTrue(filecmp.cmp("testtables.fmf", "tables3a.fmf"))

        os.remove("testtables.fmf")

    def testTable5b(self):
        # test different delimitter - pint array
        fh = open("testtables.fmf", "w+")
        wf.append_tables(fh, self.data_pint, ":G", "whitespace")
        fh.close()

        self.assertTrue(filecmp.cmp("testtables.fmf", "tables3b.fmf"))

        os.remove("testtables.fmf")

    def testTable6a(self):
        # test different number formatting - dataframe
        fh = open("testtables.fmf", "w+")
        wf.append_tables(fh, self.data, ":f", ",")
        fh.close()

        self.assertTrue(filecmp.cmp("testtables.fmf", "tables4.fmf"))

        os.remove("testtables.fmf")

    def testTable6b(self):
        # test different number formatting - pint array
        fh = open("testtables.fmf", "w+")
        wf.append_tables(fh, self.data_pint, ":f", ",")
        fh.close()

        self.assertTrue(filecmp.cmp("testtables.fmf", "tables4.fmf"))

        os.remove("testtables.fmf")


class TestWriteFMF(unittest.TestCase):
    def testWriteFMF_Solar_a(self):
        # Trys to recreate solar.fmf
        # assumes readfmf is perfect

        dataframe, metadata = rf.readFMF("../Read_FMF/Solar.fmf", 1)

        filename = "solar_test_a"
        wf.write_fmf(filename, 1.0, dataframe, metadata, formatting=":.4E")

        # self.assertTrue(filecmp.cmp("solar_test.fmf", "../Read_FMF/Solar.fmf"))
        # inspection cause it doesn't automatically format it with exponents of multiple 3.

        os.remove("solar_test_a.fmf")

    def testWriteFMF_Solar_b(self):
        # Trys to recreate solar.fmf
        # assumes readfmf is perfect

        dataframe, metadata = rf.readFMF("../Read_FMF/Solar.fmf", 1,
                                         isPinting=False)

        filename = "solar_test_b"
        wf.write_fmf(filename, 1.0, dataframe, metadata, formatting=":.4E")

        # self.assertTrue(filecmp.cmp("solar_test.fmf", "../Read_FMF/Solar.fmf"))
        # inspection cause it doesn't automatically format it with exponents of multiple 3.

        os.remove("solar_test_b.fmf")

    def testWriteFMF_Faraday_a(self):
        # Trys to recreate faraday.fmf
        # assumes readfmf is perfect

        dataframe, metadata = rf.readFMF("../Read_FMF/Faraday.fmf", 1)
        dict_data = {"A": dataframe[0], "P": dataframe[1]}

        filename = "faraday_test_a"
        wf.write_fmf(filename, 1.0, dict_data, metadata, formatting=":.4E")

        # self.assertTrue(filecmp.cmp("solar_test.fmf", "../Read_FMF/Faraday.fmf"))
        # inspection cause it doesn't format the best, numbers are -> floats, then hard to go back to ints.

        os.remove("faraday_test_a.fmf")

    def testWriteFMF_Faraday_b(self):
        # Trys to recreate faraday.fmf
        # assumes readfmf is perfect

        dataframe, metadata = rf.readFMF("../Read_FMF/Faraday.fmf", 1,
                                         isPinting=False)
        print(dataframe[0])
        dict_data = {"A": dataframe[0], "P": dataframe[1]}

        filename = "faraday_test_b"
        wf.write_fmf(filename, 1.0, dict_data, metadata, formatting=":.4E")

        # self.assertTrue(filecmp.cmp("solar_test.fmf", "../Read_FMF/Faraday.fmf"))
        # inspection cause it doesn't format the best, numbers are -> floats, then hard to go back to ints.

        os.remove("faraday_test_b.fmf")

    def testWriteFMF_dep_a(self):
        # Trys to recreate dep.fmf
        # assumes readfmf is perfect

        dataframe, metadata = rf.readFMF("../tests/resources/fmf/dep.fmf", 1)

        filename = "dep_a"
        wf.write_fmf(filename, 1.0, dataframe, metadata, formatting=":g", delimiter="whitespace")

        # self.assertTrue(filecmp.cmp("dep_a.fmf", "../tests/resources/fmf/dep.fmf"))
        # inspection cause it the whitespace of the original has different sizes.

        os.remove("dep_a.fmf")

    def testWriteFMF_multitable_a(self):
        # Trys to recreate multitable.fmf
        # assumes readfmf is perfect

        dataframe, metadata = rf.readFMF("../tests/resources/fmf/multitable.fmf", 1)

        filename = "multitable_a"
        dict_data = {"I": dataframe[0], "A": dataframe[1], "R": dataframe[2], "MM": dataframe[3], "D": dataframe[4],
                     "E": dataframe[5]}
        wf.write_fmf(filename, 1.0, dict_data, metadata, formatting=":.18g", delimiter="\t", encoding="utf-8")

        # self.assertTrue(filecmp.cmp("multitable_a.fmf", "../tests/resources/fmf/multitable.fmf"))
        # pretty close, some number - precision issues that are the main differences.

        os.remove("multitable_a.fmf")


class TestReadWriteRead(unittest.TestCase):
    def test_hash_test(self):
        # Trys to recreate hash.fmf then read again - for comparison
        # assumes readfmf is perfect

        dataframe, metadata = rf.readFMF("../tests/resources/fmf/hash_test.fmf", 1)

        filename = "hash_test_test"
        data_dict = {"DE": dataframe[0]}
        wf.write_fmf(filename, 1.0, data_dict, metadata, formatting=":g", delimiter="\t")

        dataframe2, metadata2 = rf.readFMF("hash_test_test.fmf", 1)

        self.assertTrue(dataframe[0].equals(dataframe2[0]))
        self.assertTrue(metadata == metadata2)
        os.remove("hash_test_test.fmf")

    def test_multitable(self):
        # Trys to recreate multitable.fmf then read again - for comparison
        # assumes readfmf is perfect

        dataframe, metadata = rf.readFMF(
            "../tests/resources/fmf/multitable.fmf", 1)

        filename = "multitable_test"
        dict_data = {"I": dataframe[0], "A": dataframe[1], "R": dataframe[2], "MM": dataframe[3], "D": dataframe[4],
                     "E": dataframe[5]}
        wf.write_fmf(filename, 1.0, dict_data, metadata, formatting=":.18g", delimiter="\t", encoding="uft-8")

        dataframe2, metadata2 = rf.readFMF("multitable_test.fmf", 1)

        self.assertTrue(dataframe[0].equals(dataframe2[0]))
        self.assertTrue(dataframe[1].equals(dataframe2[1]))
        self.assertTrue(dataframe[2].equals(dataframe2[2]))
        self.assertTrue(dataframe[3].equals(dataframe2[3]))
        self.assertTrue(dataframe[4].equals(dataframe2[4]))

        # dataframe[5] is only slightly different because of precision
        # i = 0
        # for index, row in dataframe[5].iterrows():
        #     print((dataframe[5]).iloc[[i]], (dataframe2[5]).iloc[[i]])
        #     i +=1
        # self.assertTrue(dataframe[5].equals(dataframe2[5]))

        self.assertTrue(metadata == metadata2)

        os.remove("multitable_test.fmf")


class TestNessesaryInfo(unittest.TestCase):
    data = {"key1": [1, 2, 3], "key2": [4, 5, 6], "key3": [7, 8, 9]}
    data = pd.DataFrame(data)
    dict_data = {"A": data, "B": data}

    def test_nessesary_info_1(self):
        # whether all the nessesary section headers are here - *referenece
        metadata = {"*data definitions": {}, "*data": {}}
        with self.assertWarnsRegex(UserWarning, r"\*reference"):
            wf.check_sections(metadata)

    def test_nessesary_info_2(self):
        # whether all the nessesary section headers are here - *data definitions
        metadata = {"reference": {}, "*data": {}}
        with self.assertWarnsRegex(UserWarning, r"\*data definitions"):
            wf.check_sections(metadata)

    def test_nessesary_info_3(self):
        # whether all the nessesary section headers are here - single dataframe
        metadata = {"*data definitions": {}, "*reference": {}, "*data": {}}
        wf.check_sections(metadata)

    def test_nessesary_info_4(self):
        # whether all the nessesary section headers are here - multiple dataframe
        metadata = {"*data definitions: A": {}, "*data definitions: B": {}, "*table definitions": {"a": "A", "b": "B"},
                    "*reference": {}, "*data": {}}
        wf.check_sections(metadata)

    def test_table_definitions1(self):
        # whether the table definitions are the same as those presented as keys in the data_dict input
        metadata = {"*table definitions": {"aaaa": "A", "bbbb": "B"}}
        wf.check_table_symbols(self.dict_data, metadata)

    def test_table_definitions2(self):
        # test if raises warning when cannot find * table definitions even though input is a dictionary of dataframes
        metadata2 = {"*table": {"aaaa": "A", "bbbb": "B"}}
        with self.assertWarnsRegex(UserWarning,
                                   r"Cannot find key/section \*table definitions, thus cannot check consistency of table symbols", ):
            wf.check_table_symbols(self.dict_data, metadata2)

    def test_table_definitions3(self):
        # test if raises warning when symbols are different
        metadata3 = {"*table definitions": {"aaaa": "A", "bbbb": "C"}}
        with self.assertWarnsRegex(UserWarning, r"Table definitions symbols not equal to the dataframe symbols"):
            wf.check_table_symbols(self.dict_data, metadata3)

    def test_table_definitions4(self):
        # should work when order is different
        metadata4 = {"*table definitions": {"bbbb": "B", "aaaa": "A", }}
        wf.check_table_symbols(self.dict_data, metadata4)


if __name__ == "__main__":
    unittest.main()
