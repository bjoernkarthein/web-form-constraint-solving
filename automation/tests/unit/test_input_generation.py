import unittest

from src.generation.input_generation import InputGenerator, ValidityEnum


class TestValidInputGeneration(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = InputGenerator()

    def test_simple_grammar_only(self) -> None:
        grammar = """
        <start> ::= <string>
        <string> ::= <letter> | <letter><string>
        <letter> ::= "a" | "b" | "c" | "d"
        """

        value = self.generator.generate_inputs(grammar)[0]
        self.assertEqual(value.validity, ValidityEnum.VALID)
        self.assertTrue(len(value.value) > 0)

    def test_simple_grammar_and_formula(self) -> None:
        grammar = """
        <start> ::= <string>
        <string> ::= <letter> | <letter><string>
        <letter> ::= "a" | "b" | "c" | "d"
        """

        formula = "str.len(<start>) > 2"

        value = self.generator.generate_inputs(grammar, formula)[0]

        self.assertEqual(value.validity, ValidityEnum.VALID)
        self.assertTrue(len(value.value) > 2)

    def test_grammar_and_formula(self) -> None:
        grammar = """
        <start> ::= <string>
        <string> ::= <letter> | <letter><string>
        <letter> ::= "a" | "b" | "c" | "d"
        """

        formula = 'str.contains(<start>, "acdc")'

        value = self.generator.generate_inputs(grammar, formula)[0]

        self.assertEqual(value.validity, ValidityEnum.VALID)
        self.assertTrue("acdc" in value.value)


class TestInvalidInputGeneration(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = InputGenerator()

    def test_simple_invalid_generation_with_formula(self) -> None:
        grammar = """
        <start> ::= <string>
        <string> ::= "" | "a" <string>
        """

        formula = "str.len(<start>) > 2"

        value = self.generator.generate_inputs(
            grammar, formula, ValidityEnum.INVALID, timeout_seconds=5
        )[0].value
        self.assertTrue(len(value) <= 2)

    def test_simple_invalid_generation_without_formula(self) -> None:
        grammar = """
        <start> ::= <string>
        <string> ::= <letter> | <letter><string>
        <letter> ::= "a" | "b" | "c" | "d"
        """

        value = self.generator.generate_inputs(
            grammar, formula=None, validity=ValidityEnum.INVALID, timeout_seconds=5
        )[0].value
        print(value)
        self.assertTrue(any(c not in value for c in "abcd"))
