import os
import tempfile
import unittest

from coalib.output.ConfWriter import ConfWriter
from coalib.parsing.ConfParser import ConfParser
from coalib.settings.Section import Section


class ConfWriterTest(unittest.TestCase):
    example_file = ('to be ignored \n'
                    '    save=true\n'
                    '    a_default, another = val \n'
                    '    TEST = tobeignored  # thats a comment \n'
                    '    test = push \n'
                    '    t = \n'
                    '    [Section] \n'
                    '    [MakeFiles] \n'
                    '     j  , ANother = a \n'
                    '                   multiline \n'
                    '                   value \n'
                    '    ; just a omment \n'
                    '    ; just a omment \n'
                    '    key\\ space = value space\n'
                    '    key\\=equal = value=equal\n'
                    '    key\\\\backslash = value\\\\backslash\n'
                    '    key\\,comma = value,comma\n'
                    '    key\\#hash = value\\#hash\n'
                    '    key\\.dot = value.dot\n'
                    '    a_default = val, val2\n')

    append_example_file = ('[defaults]\n'
                           'a = 4\n'
                           'b = 4,5,6\n'
                           'c = 4,5\n'
                           'd = 4\n'
                           '[defaults.new]\n'
                           'a = 4,5,6,7\n'
                           'b = 4,5,6,7\n'
                           'c = 4,5,6,7\n'
                           'd = 4,5,6,7\n')

    def setUp(self):
        self.file = os.path.join(tempfile.gettempdir(), 'ConfParserTestFile')
        with open(self.file, 'w', encoding='utf-8') as file:
            file.write(self.example_file)

        self.conf_parser = ConfParser()
        self.write_file_name = os.path.join(tempfile.gettempdir(),
                                            'ConfWriterTestFile')
        self.uut = ConfWriter(self.write_file_name)

    def tearDown(self):
        self.uut.close()
        os.remove(self.file)
        os.remove(self.write_file_name)

    def test_exceptions(self):
        self.assertRaises(TypeError, self.uut.write_section, 5)

    def test_write(self):
        result_file = ['[Default]\n',
                       'save = true\n',
                       'a_default, another = val\n',
                       '# thats a comment\n',
                       'test = push\n',
                       't = \n',
                       '[Section]\n',
                       '[MakeFiles]\n',
                       'j, ANother = a\n',
                       'multiline\n',
                       'value\n',
                       '; just a omment\n',
                       '; just a omment\n',
                       'key\\ space = value space\n',
                       'key\\=equal = value=equal\n',
                       'key\\\\backslash = value\\\\backslash\n',
                       'key\\,comma = value,comma\n',
                       'key\\#hash = value\\#hash\n',
                       'key\\.dot = value.dot\n',
                       'a_default += val2\n']
        self.uut.write_sections(self.conf_parser.parse(self.file))
        self.uut.close()

        with open(self.write_file_name, 'r') as f:
            lines = f.readlines()

        self.assertEqual(result_file, lines)

    def test_append(self):
        with open(self.file, 'w', encoding='utf-8') as file:
            file.write(self.append_example_file)

        result_file = ['[Default]\n',
                       '[defaults]\n',
                       'a = 4\n',
                       'b = 4,5,6\n',
                       'c = 4,5\n',
                       'd = 4\n',
                       '[defaults.new]\n',
                       'b += 7\n',
                       'c += 6, 7\n',
                       'a, d += 5, 6, 7\n']

        sections = self.conf_parser.parse(self.file)
        for (_, section) in list(sections.items()):
            section.set_default_section(sections)
        self.uut.write_sections(self.conf_parser.parse(self.file))
        self.uut.close()

        with open(self.write_file_name, 'r') as f:
            lines = f.readlines()

        self.assertEqual(result_file, lines)

    def test_write_with_dir(self):
        self.uut_dir = ConfWriter(tempfile.gettempdir())
        self.uut_dir.write_sections({'name': Section('name')})
        self.uut_dir.close()

        with open(os.path.join(tempfile.gettempdir(), '.coafile'), 'r') as f:
            lines = f.readlines()

        self.assertEqual(['[name]\n'], lines)
        os.remove(os.path.join(tempfile.gettempdir(), '.coafile'))
