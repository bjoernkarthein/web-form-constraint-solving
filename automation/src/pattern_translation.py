import string
import uuid

from abc import ABC, abstractmethod
from typing import List, Dict, Self

"""
pattern = disjunction
disjunction = term | term '|' disjunction
term = atom | atom quantifier | atom term

atom = patterncharacter | '.' | '\' printable | '(' disjunction ')' | '[' list ']'

quantifier = '*' | '+' | '?' | '{' number '}' | '{' number ',}' | '{' number ',' number '}'

syntaxcharacter = '^' | '$' | '\' | '.' | '*' | '+' | '?' | '(' | ')' | '[' | ']' | '{' | '}' | '|'
patterncharacter = printable without syntaxcharacter
"""

Grammar = Dict[str, List[str]]

class RegEx(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def build_grammar(self, grammar: Grammar, next_free_label: int):
        pass

class Alternative(RegEx):
    def __init__(self, this: RegEx, that: RegEx) -> None:
        self.__this = this
        self.__that = that

    def __str__(self) -> str:
        return f'{self.__this} or {self.__that}'

    def build_grammar(self, grammar: Grammar, next_free_label: int):
        current = list(grammar.keys())[-1]
        if is_primitive(self.__this):
            grammar[current].append(f'"{str(self.__this)}"')
        else:
            label = f'<{next_free_label}>'
            next_free_label += 1
            grammar[current].append(label)
            grammar[label] = []
            self.__this.build_grammar(grammar, next_free_label)
        if is_primitive(self.__that):
            grammar[current].append(f'"{str(self.__that)}"')
        else:
            label = f'<{next_free_label}>'
            next_free_label += 1
            grammar[current].append(label)
            grammar[label] = []
            self.__that.build_grammar(grammar, next_free_label)


class Sequence(RegEx):
    def __init__(self, first: RegEx, second: RegEx) -> None:
        self.__first = first
        self.__second = second

    def __str__(self) -> str:
        return f'{self.__first} -> {self.__second}'

    def build_grammar(self, grammar: Grammar, next_free_label: int):
        print(self.__first)
        print(self.__second)

class Quantifier(RegEx):
    def __init__(self, min_repeat: int, max_repeat: int = None) -> None:
        self.__min_repeat = min_repeat
        self.__max_repeat = max_repeat

    def __str__(self) -> str:
        result = 'times '
        if self.__min_repeat == self.__max_repeat:
            return f'times {self.__min_repeat}'
        elif self.__max_repeat == None:
            return f'times {self.__min_repeat} to unlimited'
        else:
            return f'times {self.__min_repeat} to {self.__max_repeat}'

    @property
    def min_repeat(self) -> int:
        return self.__min_repeat

    @property
    def max_repeat(self) -> int:
        return self.__max_repeat

    def build_grammar(self, grammar: Grammar):
        pass

class Repetition(RegEx):
    def __init__(self, atom: RegEx, quantifier: Quantifier) -> None:
        self.__atom = atom
        self.__quantifier = quantifier

    def __str__(self) -> str:
        return f'{self.__atom} {self.__quantifier}'

    def build_grammar(self, grammar: Grammar, next_free_label: int):
        current = list(grammar.keys())[-1]
        min = self.__quantifier.min_repeat
        max = self.__quantifier.max_repeat

        label = f'<{next_free_label}>'
        next_free_label += 1
        if min == max:
            grammar[current].append(label * min)
        elif min == 0 and max == None:
            grammar[current].extend(['""', f'{label}{current}'])
        elif min == 1 and max == None:
            grammar[current].extend([label, f'{label}{current}'])
        else:
            for i in range(min, max+1):
                if i == 0:
                    grammar[current].append('""')
                else:
                    grammar[current].append(label*i)

        grammar[label] = []
        self.__atom.build_grammar(grammar, next_free_label)

class Primitive(RegEx):
    def __init__(self, char: str) -> None:
        self.__char = char

    def __str__(self) -> str:
        return self.__char

    def build_grammar(self, grammar: Grammar, next_free_label: int):
        current = list(grammar.keys())[-1]
        grammar[current].append(f'"{self.__char}"')

def is_primitive(elem: RegEx) -> bool:
    return isinstance(elem, Primitive)

class PatternTranslator:
    def __init__(self, javascript_pattern: str) -> None:
        self.__pattern: str = javascript_pattern
        self.__syntax_characters: List[str] = ['^', '$', '\\', '.', '*', '+', '?', '(', ')', '[', ']', '{', '}', '|']
        self.__printable_characters: List[str] = [*string.printable]
        self.__digits: List[str] = [*string.digits]

    def convert(self):
        tree = self.parse()
        grammar = self.build_grammar(tree)
        print(self.write_gammar(grammar))
        
    def build_grammar(self, regex: RegEx) -> Grammar:
        grammar: Grammar = {'<start>': []}
        print(regex)
        regex.build_grammar(grammar, 1)
        return grammar

    def write_gammar(self, grammar: Grammar) -> str:
        lines = []
        for label, values in grammar.items():
            options = " | ".join(values)
            lines.append(f'{label} ::= {options}')
        
        return '\n'.join(lines)

    def parse(self) -> RegEx:
        return self.disjunction()

    # recursive descent methods
    def peek(self) -> str:
        return self.__pattern[0]
        
    def eat(self, c: str) -> None:
        if self.peek() == c:
            self.__pattern = self.__pattern[1:]
        else:
            raise ValueError(f'eat expected next character to be "{c}" but was "{self.peek()}"')

    def next(self) -> str:
        c = self.peek()
        self.eat(c)
        return c

    def more(self) -> bool:
        return len(self.__pattern) > 0


    # pattern element types
    def disjunction(self) -> RegEx:
        term = self.term()

        if self.more() and self.peek() == '|':
            self.eat('|')
            disjunction = self.disjunction()
            return Alternative(term, disjunction)
        else:
            return term  

    def term(self) -> RegEx:
        term = self.atom()
        
        if self.more() and self.peek() in ['*', '+', '?', '{']:
            quantifier = self.quantifier()
            term = Repetition(term, quantifier)
        
        while self.more() and self.peek() != ')' and self.peek() != '|':
            next_term = self.term()
            term = Sequence(term, next_term)
            
        return term

    def atom(self) -> RegEx:
        c = self.peek()
        match c:
            case '.':
                # TODO: handle . correctly with quantifiers
                self.eat('.')
                no_line_terminators = self.__printable_characters.copy()
                no_line_terminators.remove('"')
                return self.__create_choice_from_list(no_line_terminators[:-6])
            case '\\':
                # TODO: what about \s etc?
                self.eat('\\')
                char = self.next()
                return Primitive(char)
            case '(':
                # TODO: handle groups correctly with quantifiers
                self.eat('(')
                disjunction = self.disjunction()
                self.eat(')')
                return disjunction
            case '[':
                # TODO: list
                pass
            case _:
                self.eat(c)
                return Primitive(c)

    def quantifier(self) -> RegEx:
        c = self.peek()
        match c:
            case '*':
                self.eat('*')
                return Quantifier(0, None)
            case '+':
                self.eat('+')
                return Quantifier(1, None)
            case '?':
                self.eat('?')
                return Quantifier(0, 1)
            case '{':
                self.eat('{')
                quantifier = self.__handle_quantification_with_numbers()
                self.eat('}')
                return quantifier

    def __create_choice_from_list(self, characters: List[str]) -> Alternative:
        if len(characters) == 2:
            return Alternative(Primitive(characters[0]), Primitive(characters[1]))

        c = characters[0]
        return Alternative(Primitive(c), self.__create_choice_from_list(characters[1:]))
    
    def __handle_quantification_with_numbers(self) -> Quantifier:
        min = self.next()
        while (self.more() and self.peek() not in [',', '}']):
            min = min + self.next()
        
        if self.peek() == '}':
            return Quantifier(int(min), int(min))

        if self.peek() == ',':
            self.eat(',')
            max = self.next()
            while (self.more() and self.peek() not in ['}']):
                max = max + self.next()

            return Quantifier(min, max)


t = PatternTranslator('abcd')
t.convert()