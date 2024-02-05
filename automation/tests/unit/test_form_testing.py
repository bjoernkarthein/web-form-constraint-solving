import json
import os
import unittest

from src.interaction.form_testing import SpecificationParser
from src.utility.helpers import load_file_content

test_data_path = "tests/unit/test_data/"


class TestSpecificationParser(unittest.TestCase):
    def test_parse_valid_spec(self):
        """
        Test that a valid specification is parsed correctly
        """
        json_str = load_file_content(
            os.path.abspath(f"{test_data_path}/valid_spec.json")
        )
        parser = SpecificationParser("")
        valid_spec = json.loads(json_str)
        result = parser._SpecificationParser__check_specification_format(valid_spec)
        self.assertTrue(result)

    def test_parse_invalid_spec(self):
        """
        Test that an invalid specification is handled with the correct errors during parsing
        """
        json_str = load_file_content(
            os.path.abspath(f"{test_data_path}/invalid_spec.json")
        )
        parser = SpecificationParser("")
        valid_spec = json.loads(json_str)
        result = parser._SpecificationParser__check_specification_format(valid_spec)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
