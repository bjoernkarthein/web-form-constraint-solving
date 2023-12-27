import string
import sys

from typing import List, Dict

"""
pattern = disjunction
disjunction = term | term '|' disjunction
term = atom | atom quantifier | atom term

atom = patterncharacter | '.' | '\' printable | '(' disjunction ')' | '[' list ']'

quantifier = '*' | '+' | '?' | '{' number '}' | '{' number ',}' | '{' number ',' number '}'

syntaxcharacter = '^' | '$' | '\' | '.' | '*' | '+' | '?' | '(' | ')' | '[' | ']' | '{' | '}' | '|'
patterncharacter = printable without syntaxcharacter
"""

class RegEx:
    def __init__(self) -> None:
        pass

class Blank(RegEx):
    pass

class Alternative(RegEx):
    def __init__(self, this: RegEx, that: RegEx) -> None:
        self.__this = this
        self.__that = that

    def __str__(self) -> str:
        return f'({self.__this}) or ({self.__that})'

class Sequence(RegEx):
    def __init__(self, first: RegEx, second: RegEx) -> None:
        self.__first = first
        self.__second = second

    def __str__(self) -> str:
        return f'{self.__first} -> {self.__second}'

class Quantifier(RegEx):
    def __init__(self, min_repeat: int, max_repeat: int = None) -> None:
        self.__min_repeat = min_repeat
        self.__max_repeat = max_repeat

    def __str__(self) -> str:
        result = 'times '
        if self.__max_repeat is None:
            return f'times {self.__min_repeat}'
        elif self.__max_repeat == sys.maxsize:
            return f'times {self.__min_repeat} to unlimited'
        else:
            return f'times {self.__min_repeat} to {self.__max_repeat}'

class Repetition(RegEx):
    def __init__(self, atom: RegEx, quantifier: RegEx) -> None:
        self.__atom = atom
        self.__quantifier = quantifier

    def __str__(self) -> str:
        return f'{self.__atom} {self.__quantifier}'

class Primitive(RegEx):
    def __init__(self, char: str) -> None:
        self.__char = char

    def __str__(self) -> str:
        return self.__char

class PrimitiveChoice(RegEx):
    def __init__(self, choices) -> None:
        self.__choices = choices

    def __str__(self) -> str:
        return f'one from {self.__choices}'

class PatternTranslator:
    def __init__(self, javascript_pattern: str) -> None:
        self.__pattern: str = javascript_pattern
        self.__syntax_characters: List[str] = ['^', '$', '\\', '.', '*', '+', '?', '(', ')', '[', ']', '{', '}', '|']
        self.__printable_characters: List[str] = [*string.printable]
        self.__digits: List[str] = [*string.digits]

    def convert(self):
        tree = self.parse()
        print(tree)

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
                self.eat('.')
                no_line_terminators = self.__printable_characters.copy()
                no_line_terminators.remove('\n')
                no_line_terminators.remove('\r')
                return PrimitiveChoice(no_line_terminators)
            case '\\':
                # TODO: what about \s etc?
                self.eat('\\')
                char = self.next()
                return Primitive(char)
            case '(':
                # TODO: handle groups correctly
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
                return Quantifier(0, sys.maxsize)
            case '+':
                self.eat('+')
                return Quantifier(1, sys.maxsize)
            case '?':
                self.eat('?')
                return Quantifier(0, 1)
            case '{':
                self.eat('{')
                quantifier = self.__handle_quantification_with_numbers()
                self.eat('}')
                return quantifier
    
    def __handle_quantification_with_numbers(self) -> Quantifier:
        min = self.next()
        while (self.more() and self.peek() not in [',', '}']):
            min = min + self.next()
        
        if self.peek() == '}':
            return Quantifier(int(min), None)

        if self.peek() == ',':
            self.eat(',')
            max = self.next()
            while (self.more() and self.peek() not in ['}']):
                max = max + self.next()

            return Quantifier(min, max)


t = PatternTranslator('^x\+$|a.?(bc)*')
t.convert()