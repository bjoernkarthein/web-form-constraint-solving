import string
import uuid

from abc import ABC, abstractmethod
from typing import List, Dict, Self, Set

"""
pattern = disjunction
disjunction = term | term '|' disjunction
term = atom | atom quantifier | atom term

atom = patterncharacter | '.' | '\' printable | '(' group ')' | '[' options ']'

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
    def nodes(self) -> List[Self]:
        pass

    @abstractmethod
    def leaves(self) -> List[Self]:
        pass

class Pattern:
    def __init__(self, regex_tree: RegEx) -> None:
        self.__tree = regex_tree
        self.nodes: Set[RegEx] = self.__tree.nodes()
        self.leaves: Set[Primitive] = self.__tree.leaves()

class Alternative(RegEx):
    def __init__(self, this: RegEx, that: RegEx) -> None:
        self.__this = this
        self.__that = that

    def __str__(self) -> str:
        return f'{self.__this} or {self.__that}'

    def nodes(self) -> List[Self]:
        return self.__this.nodes() + self.__that.nodes() + [self]

    def leaves(self) -> List[Self]:
        return self.__this.leaves() + self.__that.leaves()

class Sequence(RegEx):
    def __init__(self, first: RegEx, second: RegEx) -> None:
        self.__first = first
        self.__second = second

    def __str__(self) -> str:
        return f'{self.__first} -> {self.__second}'

    @property
    def first(self) -> int:
        return self.__first

    @property
    def second(self) -> int:
        return self.__second

    def nodes(self) -> List[Self]:
        return self.__first.nodes() + self.__second.nodes() + [self]

    def leaves(self) -> List[Self]:
        return self.__first.leaves() + self.__second.leaves()

class Quantifier:
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

class Repetition(RegEx):
    def __init__(self, term: RegEx, quantifier: Quantifier) -> None:
        self.__term = term
        self.__quantifier = quantifier

    def __str__(self) -> str:
        return f'{self.__term} {self.__quantifier}'

    def nodes(self) -> List[Self]:
        return self.__term.nodes() + [self]

    def leaves(self) -> List[Self]:
        return self.__term.leaves()

class Primitive(RegEx):
    def __init__(self, char: str) -> None:
        self.__char = char

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

    @property
    def char(self) -> str:
        return self.__char

    def nodes(self) -> List[Self]:
        return []

    def leaves(self) -> List[Self]:
        return [self]

class PatternTranslator:
    def __init__(self, javascript_pattern: str) -> None:
        self.__pattern: str = javascript_pattern
        self.__syntax_characters: List[str] = ['^', '$', '\\', '.', '*', '+', '?', '(', ')', '[', ']', '{', '}', '|']
        self.__printable_characters: List[str] = [*string.printable]
        self.__digits: List[str] = [*string.digits]

    def convert(self):
        tree = self.parse()
        print(tree)
        pattern = Pattern(tree)
        # grammar = self.build_grammar(pattern)
        # print(self.write_gammar(grammar))
        
    def build_grammar(self, pattern: Pattern) -> Grammar:
        next_free_label = 1
        grammar: Grammar = {'<start>': []}

        terminals = []
        [terminals.append(t) for t in pattern.leaves if t not in terminals] # remove duplicates
        for terminal in terminals:
            grammar[f'<{next_free_label}>'] = [f'"{terminal}"']
            next_free_label += 1
        
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

    def options(self) -> RegEx:
        if self.peek() == '^':
            self.eat('^')
            excluded = self.not_in()
            print(excluded)
            choices = list(set(self.__printable_characters) - set(excluded))
            return self.__create_choice_from_list(choices)

        options = self.atom()

        if self.more() and self.peek() == '-':
            self.eat('-')
            end = self.atom()
            options = self.__build_alternative_from_range(options.char, end.char)

        while self.more() and self.peek() != ']':
            next_option = self.options()
            options = Alternative(options, next_option)

        return options

    def not_in(self) -> List[str]:
        choice = self.atom()
        excluded = [str(c) for c in choice.leaves()]

        if self.more() and self.peek() == '-':
            self.eat('-')
            end = str(self.atom().leaves()[0])
            excluded = self.__get_characters_from_range(excluded[0], end)

        while self.more() and self.peek() != ']':
            next = self.not_in()
            excluded = excluded + next

        return excluded

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
                self.eat('\\')
                if self.peek() == 'd':
                    self.eat('d')
                    digits = self.__printable_characters[0:10]
                    return self.__create_choice_from_list(digits)
                elif self.peek() == 's':
                    self.eat('s')
                    return self.__create_choice_from_list(['\r', '\n', '\t', '\f', '\v'])
                elif self.peek() == 'w':
                    self.eat('w')
                    letters = self.__printable_characters[0:62]
                    return self.__create_choice_from_list(letters + ['_'])
                else:
                    char = self.next()
                    return Primitive(char)
            case '(':
                self.eat('(')
                disjunction = self.disjunction()
                self.eat(')')
                return disjunction
            case '[':
                self.eat('[')
                options = self.options()
                self.eat(']')
                return options
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

    def __get_characters_from_range(self, start: str, end: str) -> List[str]:
        try:
            start_index = self.__printable_characters.index(start)
            end_index = self.__printable_characters.index(end)
            return self.__printable_characters[start_index:end_index+1]
        except Exception as e:
            raise RuntimeError(f'Can not get sublist for values from {start} to {end}')

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


t = PatternTranslator('(a|bc)?')
tree = t.parse()
print(tree)