import re
import string

from abc import ABC, abstractmethod, abstractproperty
from typing import List, Dict
from typing_extensions import Self

"""
Simplified CFG for a JavaScript pattern (https://tc39.es/ecma262/#prod-Pattern)

pattern = disjunction
disjunction = term | term '|' disjunction
term = atom | atom quantifier | atom term

atom = patterncharacter | '.' | '\' printable | '(' group ')' | '[' list ']'
list = options | '^' options

quantifier = '*' | '+' | '?' | '{' number '}' | '{' number ',}' | '{' number ',' number '}'

syntaxcharacter = '^' | '$' | '\' | '.' | '*' | '+' | '?' | '(' | ')' | '[' | ']' | '{' | '}' | '|'
patterncharacter = printable without syntaxcharacter
"""

Grammar = Dict[str, List[str]]


class PatternConverter:
    def __init__(self, javascript_pattern: str) -> None:
        self.__javascript_pattern = javascript_pattern
        self.__parser = PatternParser(self.__javascript_pattern)
        self.__grammar_builder = GrammarBuilder()

    def convert_pattern_to_grammar(self) -> str | None:
        try:
            pattern_ast = self.__parser.parse()
        except ValueError as e:
            print(f"Could not convert given pattern {self.__javascript_pattern}")
            print(e)
            return None

        return self.__grammar_builder.convert_pattern_to_cfg(pattern_ast)


class RegEx(ABC):
    @abstractproperty
    def leaves(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> List[Self]:
        pass


class Alternative(RegEx):
    def __init__(self, this: RegEx, that: RegEx) -> None:
        self.__this = this
        self.__that = that

    @property
    def this(self) -> RegEx:
        return self.__this

    @property
    def that(self) -> RegEx:
        return self.__that

    @property
    def leaves(self) -> List[RegEx]:
        return self.__this.leaves + self.__that.leaves

    def __str__(self) -> str:
        return f"{self.__this} or {self.__that}"


class Sequence(RegEx):
    def __init__(self, first: RegEx, second: RegEx) -> None:
        self.__first = first
        self.__second = second

    @property
    def first(self) -> RegEx:
        return self.__first

    @property
    def second(self) -> RegEx:
        return self.__second

    @property
    def leaves(self) -> List[RegEx]:
        return self.__first.leaves + self.__second.leaves

    def __str__(self) -> str:
        return f"{self.__first} -> {self.__second}"


class Quantifier:
    def __init__(self, min_repeat: int, max_repeat: int = None) -> None:
        self.__min_repeat = int(min_repeat)
        self.__max_repeat = int(max_repeat) if max_repeat is not None else None

    @property
    def min_repeat(self) -> int:
        return self.__min_repeat

    @property
    def max_repeat(self) -> int:
        return self.__max_repeat

    def __str__(self) -> str:
        if self.__min_repeat == self.__max_repeat:
            return f"times {self.__min_repeat}"
        elif self.__max_repeat == None:
            return f"times {self.__min_repeat} to unlimited"
        else:
            return f"times {self.__min_repeat} to {self.__max_repeat}"


class Repetition(RegEx):
    def __init__(self, term: RegEx, quantifier: Quantifier) -> None:
        self.__term = term
        self.__quantifier = quantifier

    @property
    def term(self) -> RegEx:
        return self.__term

    @property
    def quantifier(self) -> Quantifier:
        return self.__quantifier

    @property
    def leaves(self) -> List[RegEx]:
        return self.__term.leaves

    def __str__(self) -> str:
        return f"{self.__term} {self.__quantifier}"


class Primitive(RegEx):
    def __init__(self, char: str) -> None:
        self.__char = char

    @property
    def char(self) -> str:
        return self.__char

    @property
    def leaves(self) -> List[RegEx]:
        return [self]

    def __str__(self) -> str:
        return self.__char

    def __eq__(self, other) -> bool:
        """Checks for equality of two Primitives"""
        if isinstance(other, Primitive):
            return self.__char == other.char
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> bool:
        return hash(self.__char)


class PatternParser:
    def __init__(self, javascript_pattern: str) -> None:
        self.__pattern: str = javascript_pattern
        self.__printable_characters: List[str] = [*string.printable]

    def parse(self):
        return self.disjunction()

    # recursive descent methods
    def peek(self) -> str:
        return self.__pattern[0]

    def eat(self, c: str) -> None:
        if self.peek() == c:
            self.__pattern = self.__pattern[1:]
        else:
            raise ValueError(
                f'eat expected next character to be "{c}" but was "{self.peek()}"'
            )

    def next(self) -> str:
        c = self.peek()
        self.eat(c)
        return c

    def more(self) -> bool:
        return len(self.__pattern) > 0

    # pattern element types

    def disjunction(self) -> RegEx:
        term = self.term()

        if self.more() and self.peek() == "|":
            self.eat("|")
            disjunction = self.disjunction()
            return Alternative(term, disjunction)
        else:
            return term

    def term(self) -> RegEx:
        term = self.atom()

        if self.more() and self.peek() in ["*", "+", "?", "{"]:
            quantifier = self.quantifier()
            term = Repetition(term, quantifier)

        while self.more() and self.peek() != ")" and self.peek() != "|":
            next_term = self.term()
            term = Sequence(term, next_term)

        return term

    def options(self) -> RegEx:
        if self.peek() == "^":
            self.eat("^")
            excluded = self.not_in()
            choices = list(set(self.__printable_characters) - set(excluded))
            return self.__create_choice_from_list(choices)

        options = self.atom()

        if self.more() and self.peek() == "-":
            self.eat("-")
            end = self.atom()
            options = self.__build_alternative_from_range(options.char, end.char)

        while self.more() and self.peek() != "]":
            next_option = self.options()
            options = Alternative(options, next_option)

        return options

    def not_in(self) -> List[str]:
        choice = self.atom()
        excluded = [str(c) for c in choice.leaves]

        if self.more() and self.peek() == "-":
            self.eat("-")
            end = str(self.atom().leaves[0])
            excluded = self.__get_characters_from_range(excluded[0], end)

        while self.more() and self.peek() != "]":
            next = self.not_in()
            excluded = excluded + next

        return excluded

    def atom(self) -> RegEx:
        c = self.peek()
        match c:
            case ".":
                # TODO: handle . correctly with quantifiers
                self.eat(".")
                no_line_terminators = self.__printable_characters.copy()
                no_line_terminators.remove('"')
                return self.__create_choice_from_list(no_line_terminators[:-6])
            case "\\":
                self.eat("\\")
                if self.peek() == "d":
                    self.eat("d")
                    digits = self.__printable_characters[0:10]
                    return self.__create_choice_from_list(digits)
                elif self.peek() == "s":
                    self.eat("s")
                    return self.__create_choice_from_list(
                        ["\r", "\n", "\t", "\f", "\v"]
                    )
                elif self.peek() == "w":
                    self.eat("w")
                    letters = self.__printable_characters[0:62]
                    return self.__create_choice_from_list(letters + ["_"])
                else:
                    char = self.next()
                    return Primitive(char)
            case "(":
                self.eat("(")
                disjunction = self.disjunction()
                self.eat(")")
                return disjunction
            case "[":
                self.eat("[")
                options = self.options()
                self.eat("]")
                return options
            case _:
                self.eat(c)
                return Primitive(c)

    def quantifier(self) -> RegEx:
        c = self.peek()
        match c:
            case "*":
                self.eat("*")
                return Quantifier(0, None)
            case "+":
                self.eat("+")
                return Quantifier(1, None)
            case "?":
                self.eat("?")
                return Quantifier(0, 1)
            case "{":
                self.eat("{")
                quantifier = self.__handle_quantification_with_numbers()
                self.eat("}")
                return quantifier

    def __get_characters_from_range(self, start: str, end: str) -> List[str]:
        try:
            start_index = self.__printable_characters.index(start)
            end_index = self.__printable_characters.index(end)
            return self.__printable_characters[start_index : end_index + 1]
        except Exception as e:
            raise RuntimeError(f"Can not get sublist for values from {start} to {end}")

    def __build_alternative_from_range(self, start: str, end: str) -> Alternative:
        options = self.__get_characters_from_range(start, end)
        return self.__create_choice_from_list(options)

    def __create_choice_from_list(self, characters: List[str]) -> Alternative:
        if len(characters) == 2:
            return Alternative(Primitive(characters[0]), Primitive(characters[1]))

        c = characters[0]
        return Alternative(Primitive(c), self.__create_choice_from_list(characters[1:]))

    def __handle_quantification_with_numbers(self) -> Quantifier:
        min = self.next()
        while self.more() and self.peek() not in [",", "}"]:
            min = min + self.next()

        if self.peek() == "}":
            return Quantifier(min, min)

        if self.peek() == ",":
            self.eat(",")
            max = None
            while self.more() and self.peek() not in ["}"]:
                max = self.next() if max is None else max + self.next()

            return Quantifier(min, max)


class GrammarBuilder:
    def __init__(self) -> None:
        self.__non_terminal_counter = 0

    def convert_pattern_to_cfg(self, pattern_ast: RegEx) -> str:
        start_symbol = self.__generate_non_terminal()
        pattern_cfg = self.__convert_ast_to_cfg(pattern_ast)
        prettified = self.__perttify_grammar(pattern_cfg)
        return f"{start_symbol} ::= {prettified}"

    def __generate_non_terminal(self):
        non_terminal = f"<nt{self.__non_terminal_counter}>"
        self.__non_terminal_counter += 1
        return non_terminal if self.__non_terminal_counter > 1 else "<start>"

    def __convert_ast_to_cfg(self, ast: RegEx) -> str:
        if isinstance(ast, Sequence):
            left = self.__convert_ast_to_cfg(ast.first)
            right = self.__convert_ast_to_cfg(ast.second)
            return f"{left} {right}"

        elif isinstance(ast, Alternative):
            this = self.__convert_ast_to_cfg(ast.this)
            that = self.__convert_ast_to_cfg(ast.that)
            non_terminal = self.__generate_non_terminal()
            return f"{non_terminal} ::= {this} | {that}"

        elif isinstance(ast, Repetition):
            expression = self.__convert_ast_to_cfg(ast.term)
            non_terminal = self.__generate_non_terminal()
            quantifier = ast.quantifier

            result = f"{non_terminal} ::= "
            if quantifier.min_repeat == 0:
                result += '""'
            else:
                result += f'{(" ").join([expression] * quantifier.min_repeat)}'

            if quantifier.max_repeat is None:
                result += " | "
                result += f"{expression} {non_terminal}"
            elif (
                quantifier.max_repeat is not None
                and quantifier.max_repeat > quantifier.min_repeat
            ):
                result += " | "
                result += (" | ").join(
                    [
                        (" ").join([expression] * i)
                        for i in range(
                            quantifier.min_repeat + 1, quantifier.max_repeat + 1
                        )
                    ]
                )

            return result

        elif isinstance(ast, Primitive):
            return f'"{ast.char}"'

    # TODO: is this the best approach? Revisit grammar string building maybe
    def __perttify_grammar(self, grammar: str) -> str:
        return re.sub(r"(<[^>]+>) ::=", r"\1\n\1 ::=", grammar)
