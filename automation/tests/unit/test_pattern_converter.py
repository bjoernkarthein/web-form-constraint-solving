import unittest

from src.utility.pattern_translation import PatternConverter


class TestPatternConverter(unittest.TestCase):
    def test_simple_pattern_conversion(self) -> None:
        converter = PatternConverter("test")
        grammar = converter.convert_pattern_to_grammar()

        self.assertEqual(grammar, '<start> ::= "t" "e" "s" "t"')

    def test_simple_alt_pattern_conversion(self) -> None:
        converter = PatternConverter("a|b|c")
        grammar = converter.convert_pattern_to_grammar()

        self.assertEqual(
            grammar,
            ("\n").join(
                ["<start> ::= <nt2>", '<nt2> ::= "a" | <nt1>', '<nt1> ::= "b" | "c"']
            ),
        )

    def test_simple_rep_pattern_conversion(self) -> None:
        converter = PatternConverter("a+")
        grammar = converter.convert_pattern_to_grammar()

        self.assertEqual(
            grammar, ("\n").join(["<start> ::= <nt1>", '<nt1> ::= "a" | "a" <nt1>'])
        )

    def test_simple_rep2_pattern_conversion(self) -> None:
        converter = PatternConverter("a?")
        grammar = converter.convert_pattern_to_grammar()

        self.assertEqual(
            grammar, ("\n").join(["<start> ::= <nt1>", '<nt1> ::= "" | "a"'])
        )

    def test_simple_rep3_pattern_conversion(self) -> None:
        converter = PatternConverter("a*")
        grammar = converter.convert_pattern_to_grammar()

        self.assertEqual(
            grammar, ("\n").join(["<start> ::= <nt1>", '<nt1> ::= "" | "a" <nt1>'])
        )

    def test_simple_rep4_pattern_conversion(self) -> None:
        converter = PatternConverter("a{1,3}")
        grammar = converter.convert_pattern_to_grammar()

        self.assertEqual(
            grammar,
            ("\n").join(["<start> ::= <nt1>", '<nt1> ::= "a" | "a" "a" | "a" "a" "a"']),
        )

    def test_simple_rep5_pattern_conversion(self) -> None:
        converter = PatternConverter("a{6}")
        grammar = converter.convert_pattern_to_grammar()

        self.assertEqual(
            grammar,
            ("\n").join(["<start> ::= <nt1>", '<nt1> ::= "a" "a" "a" "a" "a" "a"']),
        )

    def test_simple_rep6_pattern_conversion(self) -> None:
        converter = PatternConverter("a{2,}")
        grammar = converter.convert_pattern_to_grammar()

        self.assertEqual(
            grammar, ("\n").join(["<start> ::= <nt1>", '<nt1> ::= "a" "a" | "a" <nt1>'])
        )

    def test_not_in_pattern_conversion(self) -> None:
        converter = PatternConverter("[^a-z]")
        grammar = converter.convert_pattern_to_grammar()
