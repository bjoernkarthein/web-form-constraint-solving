from selenium.webdriver import Chrome
from typing import List

from html_analysis import HTMLConstraints, HTMLElementReference, HTMLInputSpecification


class ConstraintCandidate:
    def __init__(self) -> None:
        pass


class ConstraintCandidateFinder:
    def __init__(self, web_driver: Chrome) -> None:
        self.__driver = web_driver

    def find_constraint_candidates_for_input(self, html_input_specification: HTMLInputSpecification) -> List[ConstraintCandidate]:
        self.__driver


class SpecificationBuilder:
    def __init__(self) -> None:
        pass
