import unittest

from src.generation.input_generation import InputGenerator, ValidityEnum


class TestPrebuiltSpecifications(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = InputGenerator()

    def test_email(self) -> None:
        with open("pre-built-specifications/email/email.bnf", "r") as file:
            grammar = file.read()

        with open("pre-built-specifications/email/email.isla", "r") as file:
            formula = file.read()

        print(grammar)
        print(formula)

        values = self.generator.generate_inputs(grammar, None, ValidityEnum.VALID, 5)
        values = list(map(lambda v: v.value, values))
        print(values)
