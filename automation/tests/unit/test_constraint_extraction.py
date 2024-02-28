import unittest

from src.analysis.constraint_extraction import (
    ConstraintCandidateResult,
    ConstraintCandidate,
    ConstraintCandidateType,
    PatternMatchCandidate,
)
from src.utility.helpers import load_file_content

test_data_path = "tests/unit/test_data/"


class TestConstraintCandidate(unittest.TestCase):
    def test_simple_candidate_parsing(self):
        candidates = ConstraintCandidateResult(
            {
                "candidates": [
                    {
                        "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
                        "operator": "==",
                        "otherValue": "2",
                    },
                    {
                        "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
                        "operator": "===",
                        "otherValue": "2",
                    },
                    {
                        "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
                        "operator": "<",
                        "otherValue": "2",
                    },
                    {
                        "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
                        "operator": "<=",
                        "otherValue": "2",
                    },
                    {
                        "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
                        "operator": ">",
                        "otherValue": "2",
                    },
                    {
                        "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
                        "operator": ">=",
                        "otherValue": "2",
                    },
                    {
                        "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
                        "operator": "!=",
                        "otherValue": "2",
                    },
                    {
                        "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
                        "operator": "!==",
                        "otherValue": "2",
                    },
                ]
            }
        )

        self.assertEqual(len(candidates.candidates), 8)
        self.assertListEqual(
            list(map(lambda c: c.operator, candidates.candidates)),
            [
                "=",
                "=",
                "<",
                "<=",
                ">",
                ">=",
                "not (VALUE = OTHER)",
                "not (VALUE = OTHER)",
            ],
        )

    def test_pattern_candidate_parsing(self) -> None:
        candidates = ConstraintCandidateResult(
            {
                "candidates": [
                    {
                        "type": ConstraintCandidateType.REGEX_TEST.value,
                        "pattern": "some string",
                    },
                    {
                        "type": ConstraintCandidateType.STRING_MATCH.value,
                        "pattern": "/[A-Z]|\/x/g",
                    },
                ]
            }
        )

        self.assertTrue(type(candidates.candidates[0]) is PatternMatchCandidate)
        regex_candidate = candidates.candidates[0]

        self.assertTrue(type(candidates.candidates[1]) is PatternMatchCandidate)
        match_candidate = candidates.candidates[1]

        self.assertEqual(regex_candidate.pattern, "some string")
        self.assertFalse(regex_candidate.is_regex)

        self.assertEqual(match_candidate.pattern, "[A-Z]|\/x")
        self.assertTrue(match_candidate.is_regex)

    def test_candidate_equality(self) -> None:
        first = ConstraintCandidateResult(
            {
                "candidates": [
                    {
                        "type": ConstraintCandidateType.REGEX_TEST.value,
                        "pattern": "some string",
                    },
                    {
                        "type": ConstraintCandidateType.STRING_MATCH.value,
                        "pattern": "/[A-Z]|\/x/g",
                    },
                ]
            }
        )
        second = "test"
        third = ConstraintCandidateResult(
            {
                "candidates": [
                    {
                        "type": ConstraintCandidateType.REGEX_TEST.value,
                        "pattern": "some string",
                    }
                ]
            }
        )

        self.assertEqual(first, first)
        self.assertNotEqual(first, second)
        self.assertNotEqual(first, third)


if __name__ == "__main__":
    unittest.main()
