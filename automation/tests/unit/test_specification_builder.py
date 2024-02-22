import unittest

from src.analysis.constraint_extraction import ConstraintCandidateResult, ConstraintCandidateType, ConstraintOtherValueType, SpecificationBuilder
from src.analysis.html_analysis import HTMLInputSpecification, HTMLElementReference, HTMLConstraints, HTMLRadioGroupSpecification

class TestSpecificationBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = SpecificationBuilder()

        input_reference = HTMLElementReference("id", "input")
        input_constraints = HTMLConstraints(type="number", min=10, max=20, required="")

        radio_references = [(HTMLElementReference("id", "1"), "1"), (HTMLElementReference("id", "2"), "2")]

        self.input_spec = HTMLInputSpecification(input_reference, input_constraints)
        self.radio_spec = HTMLRadioGroupSpecification("radio", radio_references)
        self.builder.create_specification_for_html_input(self.input_spec)
        self.builder.create_specification_for_html_radio_group(self.radio_spec)

    def test_add_constraint_candidates_empty(self) -> None:
        old_grammar, old_formula = self.builder.refrence_to_spec_map.get(str(self.input_spec.reference))
        new_grammar, new_formula = self.builder.add_constraints_to_current_specification(self.input_spec.reference, "number", ConstraintCandidateResult({'candidates': []}))
        self.assertEqual(old_grammar, new_grammar)
        self.assertEqual(old_formula, new_formula)

    def test_add_constraint_candidate_literal_comp(self) -> None:
        new_grammar, new_formula = self.builder.add_constraints_to_current_specification(self.input_spec.reference, "number", 
        ConstraintCandidateResult({'candidates': [{
            "type": ConstraintCandidateType.LITERAL_COMPARISON.value,
            "operator": "==",
            "otherValue": "15"
        }]}))
        self.assertIn('= "15"', new_formula)

    def test_add_constraint_candidate_length_comp(self) -> None:
        new_grammar, new_formula = self.builder.add_constraints_to_current_specification(self.input_spec.reference, "number", 
        ConstraintCandidateResult({'candidates': [{
            "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
            "operator": ">=",
            "otherValue": "2"
        }]}))
        self.assertIn('>= "2"', new_formula)

    def test_add_constraint_candidates_multiple(self) -> None:
        new_grammar, new_formula = self.builder.add_constraints_to_current_specification(self.input_spec.reference, "number", 
        ConstraintCandidateResult(
            {
                'candidates': 
                    [{
                        "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
                        "operator": ">=",
                        "otherValue": "2"
                    },
                    {
                        "type": ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value,
                        "operator": "<=",
                        "otherValue": "30"
                    }]
            }
        ))
        self.assertIn('>= "2"', new_formula)
        self.assertIn('<= "30"', new_formula)

    def test_add_constraint_candidate_var_comp_unknown(self) -> None:
        new_grammar, new_formula = self.builder.add_constraints_to_current_specification(self.input_spec.reference, "number", 
        ConstraintCandidateResult({'candidates': [{
            "type": ConstraintCandidateType.VARIABLE_COMPARISON,
            "operator": ">=",
            "otherValue": {
                "type": ConstraintOtherValueType.UNKOWN.value,
                "value": "MAX_SIZE"
            }
        }]}))

    def test_add_constraint_candidate_var_comp_ref_eq(self) -> None:
        other_input_reference = HTMLElementReference("id", "other-input")
        other_input_constraints = HTMLConstraints(type="number", min=0, max=100)
        other_input_spec = HTMLInputSpecification(other_input_reference, other_input_constraints)
        self.builder.create_specification_for_html_input(other_input_spec)

        new_grammar, new_formula = self.builder.add_constraints_to_current_specification(self.input_spec.reference, "number", 
        ConstraintCandidateResult({'candidates': [{
            "type": ConstraintCandidateType.VARIABLE_COMPARISON.value,
            "operator": "==",
            "otherValue": {
                "type": ConstraintOtherValueType.REFERENCE.value,
                "value": str(other_input_reference)
            }
        }]}))

    def test_add_constraint_candidate_var_comp_ref_neq(self) -> None:
        other_input_reference = HTMLElementReference("id", "other-input")
        other_input_constraints = HTMLConstraints(type="number", min=0, max=100)
        other_input_spec = HTMLInputSpecification(other_input_reference, other_input_constraints)
        self.builder.create_specification_for_html_input(other_input_spec)

        new_grammar, new_formula = self.builder.add_constraints_to_current_specification(self.input_spec.reference, "number", 
        ConstraintCandidateResult({'candidates': [{
            "type": ConstraintCandidateType.VARIABLE_LENGTH_COMPARISON.value,
            "operator": "!==",
            "otherValue": {
                "type": ConstraintOtherValueType.REFERENCE.value,
                "value": str(other_input_reference)
            }
        }]}))

    def test_add_constraint_candidate_regex(self) -> None:
        new_grammar, new_formula = self.builder.add_constraints_to_current_specification(self.input_spec.reference, "number", 
        ConstraintCandidateResult({'candidates': [{
            "type": ConstraintCandidateType.REGEX_TEST.value,
            "pattern": "some string"
        }]}))

        self.assertIn(f'str.contains(<{self.input_spec.type}>, "some string")', new_formula)

    def test_add_constraint_candidate_match(self) -> None:
        new_grammar, new_formula = self.builder.add_constraints_to_current_specification(self.input_spec.reference, "number", 
        ConstraintCandidateResult({'candidates': [{
            "type": ConstraintCandidateType.REGEX_TEST.value,
            "pattern": "/a?/"
        }]}))

        self.assertEqual(new_grammar, ("\n").join([
            f'<start> ::= <{self.input_spec.type}-or-empty>',
            f'<{self.input_spec.type}-or-empty> ::= "" | <{self.input_spec.type}>',
            f'<{self.input_spec.type}> ::= <nt1>',
            '<nt1> ::= "" | "a"'
        ]))