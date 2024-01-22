import random
import string


class ValueMutator:
    def __init__(self, input: str, mutations: int = 1) -> None:
        self.__input = input
        self.__mutations = mutations
        self.__mutators = [
            self.__delete_random_character,
            self.__insert_random_character,
            self.__flip_random_character,
        ]

    def mutate(self, seed: str | None = None) -> str:
        if seed is not None:
            self.__input = seed

        for _ in range(self.__mutations):
            mutator = random.choice(self.__mutators)
            mutator()

        return self.__input

    def __delete_random_character(self) -> None:
        if len(self.__input) == 0:
            return

        pos = random.randint(0, len(self.__input) - 1)
        self.__input = self.__input[:pos] + self.__input[pos + 1 :]

    def __insert_random_character(self) -> None:
        pos = random.randint(0, len(self.__input))
        random_character = random.choice(string.printable)
        self.__input = self.__input[:pos] + random_character + self.__input[pos:]

    def __flip_random_character(self) -> None:
        if len(self.__input) == 0:
            return

        pos = random.randint(0, len(self.__input) - 1)
        char = self.__input[pos]
        bit = 1 << random.randint(0, 6)
        new_char = chr(ord(char) ^ bit)
        self.__input = self.__input[:pos] + new_char + self.__input[pos + 1 :]
