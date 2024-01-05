import json

from typing import Dict

from utility import load_file_content


class SpecificationParser:
    def __init__(self, specification_file_path: str) -> None:
        self.__specification_file_path = specification_file_path

    def parse(self) -> Dict | None:
        specification_str = load_file_content(
            'specification/specification.json' if self.__specification_file_path is None else self.__specification_file_path)
        if specification_str == '':
            print(
                'No existing specification file found. Either pass a path to a valid specification file via the -s flag or run the analyse.py to extract a specification automatically.')
            return None

        try:
            specification = json.loads(specification_str)
        except json.JSONDecodeError as e:
            print('Error parsing specification file')
            print(e)
            return None

        if self.__specification_file_path is not None and not self.__check_specification_format(specification):
            print('The given specification file does not have the correct format')
            return None

        return specification

    def __check_specification_format(self, specification: Dict) -> bool:
        return True
