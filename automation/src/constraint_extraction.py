import numpy

from selenium.webdriver import Chrome
from typing import List

from html_analysis import HTMLConstraints, HTMLElementReference, HTMLInputSpecification
from utility import InputType, textual_input_types

"""
Constraint Extraction module

Provides classes to define constraint candidates, extract candidates from inputs and
build a specification for these inputs.
"""


class ConstraintCandidate:
    def __init__(self) -> None:
        pass


class ConstraintCandidateFinder:
    """ConstraintCandidateFinder class

    Provides methods to identify constraint candidates for a specific input of the form.
    """

    def __init__(self, web_driver: Chrome) -> None:
        self.__driver = web_driver

    def find_constraint_candidates_for_input(self, html_input_specification: HTMLInputSpecification) -> List[ConstraintCandidate]:
        """Try to extract as many constraint candidates as possible from the source code for a given input."""

        magic_values = self.get_magic_value_sequence_by_type(
            html_input_specification.contraints.type)

        print(magic_values)

        return []

    def get_magic_value_sequence_by_type(self, type: str) -> List[str]:
        """Get a sequence of 'magic values' for a given HTML input type.

        'Magic values' are used to find the important code parts for validation during dynamic analysis of the source code.
        """
        match type:
            case t if t in textual_input_types:
                return 'magic_value_why_would_someone_add_this_to_their_code'
            case InputType.CHECKBOX.value:
                return self.__get_random_checked_states(10)
            case InputType.RADIO.value:
                pass
            case _:
                raise ValueError(
                    'The provided type does not match any known html input type')

    def __get_random_checked_states(self, amount: int) -> List[int]:
        """Get a sequence of of 0s and 1s in random order, the length of which is specified by amount."""

        checked_states = numpy.ones(amount, dtype=numpy.int0)
        checked_states[:amount // 2] = 0
        numpy.random.shuffle(checked_states)
        return checked_states.tolist()


class SpecificationBuilder:
    def __init__(self) -> None:
        pass
