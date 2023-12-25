from typing import List, Dict

class PatternTranslator:
    def __init__(self) -> None:
        self.__special_characters = ['^', '$', '\\', '.', '*', '+', '?', '(', ')', '[', ']', '{', '}', '|']

    def convert_pattern_to_specification(self, javascript_pattern: str) -> (str, str | None):
        formula = None

        # According to html standard the user agent checks the input against ^(?:javascript_pattern)$
        if javascript_pattern[0] == '^':
            javascript_pattern = javascript_pattern[1:]
        
        if javascript_pattern[-1] == '$':
            javascript_pattern = javascript_pattern[:-1]

        quantifiers = self.__find_between(javascript_pattern, '{', '}')
        lists = self.__find_between(javascript_pattern, '[', ']')

        print(quantifiers)
        print(lists)

        grammar = self.__find_terminals(javascript_pattern)
        print(grammar)

        groups = self.__find_groups(javascript_pattern)
        print(groups)

        return grammar, formula

    def __find_between(self, string: str, start_character: str, end_character: str) -> List[str]:
        elements = []
        start_index = None
        end_index = None

        for i in range(len(string)):
            c = string[i]

            # TODO: nested quantifiers?
            if c == start_character:
                start_index = i
            if c == end_character:
                end_index = i
                print(start_index, end_index)
                elements.append(string[start_index:end_index+1])
                start_index = None
                end_index = None
        
        return elements

    def __find_terminals(self, javascript_pattern: str) -> Dict[int, List[str]]:
        grammar = {}
        for i in range(len(javascript_pattern)):
            c = javascript_pattern[i]
            if not c in self.__special_characters or i > 0 and javascript_pattern[i-1] == '\\':
                self.__add_rule_to_grammar(grammar, [c])
        
        return grammar

    def __find_groups(self, javascript_pattern: str) -> List[str]:
        groups = []
        unmatched_parentheses = 0
        start_index = None
        end_index = None

        for i in range(len(javascript_pattern)):
            c = javascript_pattern[i]

            if c == '(':
                if unmatched_parentheses == 0:
                    start_index = i
                unmatched_parentheses += 1
            if c == ')':
                unmatched_parentheses -= 1
                if unmatched_parentheses == 0:
                    end_index = i
                    javascript_pattern[start_index:end_index]
                    group = javascript_pattern[start_index:end_index+1]
                    
                    # recursively add subgroups from inner most to outermost
                    groups.extend(self.__find_groups(group[1:-1]))
                    groups.append(group)
            
                    start_index = None
                    end_index = None
    
        return groups

    def __add_group_to_grammar(self, group: str, grammar: Dict[int, List[str]]) -> Dict[int, List[str]]:
        
        return grammar

    def __add_rule_to_grammar(self, grammar: Dict[int, List[str]], rules: List[str]) -> Dict[int, List[str]]:
        next_free_index = len(grammar) + 1
        grammar[next_free_index] = rules
        return grammar


t = PatternTranslator()
t.convert_pattern_to_specification("""((a(b))\.c)[a-z]{1,5}(d)""")