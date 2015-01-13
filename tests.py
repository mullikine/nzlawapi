import random
import unittest
from xml import etree
from server import *
from definitions import *
from util import xml_compare
import os


class TestQueries(unittest.TestCase):

    def setUp(self):      
        self.parser = etree.XMLParser(remove_blank_text=True)      
        self.xml = etree.parse('tests/companiesact.xml', parser=self.parser)

    def tearDown(self):
        pass
        #self.conn.close()

    def test_path_query_counts(self):
        # test path queries return correct number of leaf nodes
        self.assertEqual(len(find_sub_node(self.xml, ['2'])), 1)
        self.assertEqual(len(find_sub_node(self.xml, ['223'])), 1)
        self.assertEqual(len(find_sub_node(self.xml, ['223', 'b'])), 1)
        self.assertEqual(len(find_sub_node(self.xml, ['223', 'a+c'])), 2)
        self.assertEqual(len(find_schedule_node(self.xml, '2')), 1)

    def test_path_query_failures(self):
        self.assertRaises(CustomException, find_sub_node, self.xml, ['666'])      

    def test_definition_query_counts(self):
        self.assertEqual(len(find_definitions(self.xml, 'company')), 20)
        self.assertRaises(CustomException, find_definitions, self.xml, 'balderdash')

    @unittest.skip("need db")
    def test_id_search(self):
        conn = connect_db()
        self.assertEqual(len(find_node_by_id('DLM320106', db=conn)[0]), 1)
        self.conn.close()

    def test_search(self):
        self.assertEqual(len(find_node_by_query(self.xml, 'constitution')), 910)
        self.assertEqual(len(find_node_by_query(self.xml, 'fistycuffs')), 0)


class TestDefinitions(unittest.TestCase):

    def setUp(self):      
        self.parser = etree.XMLParser(remove_blank_text=True)      

    def test_definition_extraction(self):
        tree = etree.parse('tests/3_definitions.xml', parser=self.parser)
        definitions = find_all_definitions(tree)
        self.assertEqual(len(definitions), 3)
        self.assertTrue('accounting period' in definitions)
        self.assertTrue('address for service' in definitions)
        self.assertTrue('annual meeting' in definitions)

    def test_definition_transience_simple(self):
        parser = etree.XMLParser(remove_blank_text=True)        
        tree = etree.parse('tests/transient_defs.xml', parser=self.parser)
        tree, definitions = process_definitions(tree, Definitions())
        self.assertEqual(len(definitions), 1)
        self.assertEqual(len(definitions.all()), 4)

def transform_eqn(filename, parser):
    transform = etree.XSLT(etree.parse('xslt/equations_root.xslt'))
    tree = etree.parse(filename, parser=parser)
    # using method="html" leaves col tags unclosed, and therefore creates malformed documents which can't be read by fromstring
    # TODO: is there a fix for this, or do we even need fromstring(tosting())?
    return etree.fromstring(etree.tostring(transform(tree), encoding='UTF-8', method="xml"), parser=parser)

def print_error(msg):
    print msg

class TestEquations(unittest.TestCase):

    def setUp(self):      
        self.parser = etree.XMLParser(remove_blank_text=True)      

    def test_equations(self):
        for f in [f for f in os.listdir('tests/equations') if f.endswith('.xml')]:
            print f
            result= transform_eqn(os.path.join('tests/equations', f), self.parser)
            expected = etree.parse(os.path.join('tests/equations', f.replace('.xml', '.html')), parser=self.parser)
            self.assertTrue(xml_compare(result, expected.getroot(), print_error))






if __name__ == '__main__':
    unittest.main()