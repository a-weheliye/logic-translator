"""

formula ::= ("∀" | "∃") var "." "(" formula ")" | complex
complex ::= term { "⇒" complex }
   term ::= factor { ("∧" | "∨") factor}
 factor ::= atom | '(' complex ')' | "¬" complex
   atom ::= P | Q | R | S | T
    var ::= a | b | ... | z
    
"""
import string

import regex as re
import scanner
from scanner import (LPAREN, RPAREN , COMMA, IMPLIES, LNOT, 
                LAND, LOR, FORALL, EXIST, VAR, DOT, getSym, error)


def Remove_Duplicates(input_string):
    pattern = r"\b(\w+)(?:\W\1\b)+"
    return re.sub(pattern, r"\1", input_string, flags=re.IGNORECASE)


def flatten_list(original_list): 
    return [item for sublist in original_list for item in sublist]


def format(s, op, length=None, left=None, right=None):
    
    if op == "and": 
        
        count = s.count("holds")
        s = re.sub(r"holds ", r"", s, count-1)
        s = re.sub(r" and (?![A-Z] hold)", r", ", s, count-1)
        s = re.sub(r"holds", r"hold", s)
        return s
    
    elif op == "or" : 
        count = s.count("holds")
        s = re.sub(r"holds ", r"", s, count-1)
        s = re.sub(r" or (?![A-Z] (hold|and))", r", ", s, count-1)
        s = re.sub(r"holds", r"hold", s)
        return s
    
    elif op == "implies":
        return s 
    
        pattern = r"(?<!holds|doesn't hold) implies (?![A-Z] holds)"
        replace = r", "
        
    elif op == "not":
        s = re.sub(r"\bholds doesn't hold\b", r"doesn't hold", s)
        s = re.sub(r"\bdoesn't hold doesn't hold\b", r"holds", s)
        return s

    elif op == "There exists" or op == "For all":
        s = re.sub(r"\bdoesn't hold holds\b", r"doesn't hold", s)
        s = proper_capitalization(s)
        return s       
        
        
    # return re.sub(pattern, replace, s)

 
def format_not(s, operand):
    s = re.sub(r"\bholds doesn't hold\b", r"doesn't hold", s)
    s = re.sub(r"\bdoesn't hold doesn't hold\b", r"holds", s)
    return s
 
 
def format_quantifier(s):
    s = re.sub(r"\bdoesn't hold holds\b", r"doesn't hold", s)
    s = proper_capitalization(s)
    return s       


def proper_capitalization(s): 
    words = s.split(" ")
    new = []
    for i in range(len(words)):
        if ((words[i] == "For" or words[i] == "There") and i != 0):
            new.append(words[i].lower())
        else:
            new.append(words[i])
    return " ".join(new)



# ------------------------------------------------------------------------------------------------

class Variable:
    def __init__(self, name, pos):
        self.name, self.pos = name, scanner.pos
        
    def __str__(self) : return str(self.name)    
    def __repr__(self): return str(self.name)
    def __iter__(self): return iter(self.name)
    

class AtomicProp:
    def __init__(self, prop, pos):
        self.prop = prop
        self.pos = scanner.pos
        self.list = [self.prop]
        
    def __str__(self) : return f"{self.prop} holds"
    def __repr__(self): return str(self.prop)
    def eq_form(self) : return f"{self.prop}"
    def __iter__(self): return iter(self.prop)
    def __len__(self) : return 1
    
    
class Implies:
    def __init__(self, op, left, right, pos):
        self.op, self.left, self.right, self.pos = op, left, right, pos
        self.list_left  = flatten_list([list(left)])
        self.list_right = flatten_list([list(right)])
        self.list = self.list_left + self.list_right
        
    def __str__(self):
        # return f"{self.left} {SC.OP_SYM[self.op]} {self.right}"
        s = Remove_Duplicates(f"{self.left} implies {self.right} holds")
        return format(s, str(scanner.OP_SYM[self.op]), len(self.list), self.left, self.right)

    def __repr__(self): return f"Implies({repr(self.left)}, {repr(self.right)})"        
    def eq_form(self) : return f"({self.left.eq_form()} ⇒ {self.right.eq_form()})"    
    def __iter__(self): return iter([self.list_left] + [self.list_right])    
    def __len__(self) : return len(self.list)    
    
    
class Conjunction:
    def __init__(self, op, left, right, pos):
        self.op, self.left, self.right, self.pos = op, left, right, pos
        self.list_left  = flatten_list([list(left)])
        self.list_right = flatten_list([list(right)])
        self.list = self.list_left + self.list_right
        
    def __str__(self):
        # return f"{self.left} {SC.OP_SYM[self.op]} {self.right}"
        s = format(Remove_Duplicates(f"{self.left} and {self.right}"), "and", len(self.list), self.left, self.right)
        return Remove_Duplicates(f"{s} hold")

    def __repr__(self): return f"Conjunction({repr(self.left)}, {repr(self.right)})"
    def eq_form(self) : return f"({self.left.eq_form()} ∧ {self.right.eq_form()})"
    def __iter__(self): return iter(self.list)
    def __len__(self) : return len(self.list)
    
    
class Disjunction:
    def __init__(self, op, left, right, pos):
        self.op, self.left, self.right, self.pos = op, left, right, pos
        self.list_left  = flatten_list([list(left)])
        self.list_right = flatten_list([list(right)])
        self.list = flatten_list([list(left)]) + flatten_list([list(right)])
        
    def __str__(self):
        # return f"{self.left} {SC.OP_SYM[self.op]} {self.right}"
        s = format(Remove_Duplicates(f"{self.left} or {self.right}"), "or", len(self.list), self.left, self.right)
        return Remove_Duplicates(f"{s} hold")
    
    def __repr__(self): return f"Disjunction({repr(self.left)}, {repr(self.right)})"
    def eq_form(self) : return f"({self.left.eq_form()} ∨ {self.right.eq_form()})"
    def __iter__(self): return iter(self.list)
    def __len__(self) : return len(self.list)
    
class Negation:
    def __init__(self,operand, pos):
        self.operand, self.pos = operand, pos
        
    def __str__(self):  return format_not(f"{self.operand} doesn't hold", self.operand)
    def __repr__(self): return (f"Negation({repr(self.operand)})")
    def eq_form(self):  return f"¬ ({self.operand.eq_form()})"
    def __iter__(self): return iter(self.operand)
    
    
class Existential:
    def __init__(self, op, variable, operand, pos):
        self.op, self.variable, self.operand, self.pos = op, variable, operand, pos

    def __str__(self) : return format_quantifier(Remove_Duplicates(f"There exists {self.variable}, such that {self.operand}"))  
    def __repr__(self): return f"Existential({repr(self.variable)}, {repr(self.operand)})"
    def __len__(self) : return len(self.operand)

    
class Universal:
    def __init__(self, op, variable, operand, pos):
        self.op, self.variable, self.operand, self.pos = op, variable, operand, pos

    def __str__(self) : return format_quantifier(Remove_Duplicates(f"For all {self.variable}, {self.operand} holds"))
    def __repr__(self): return f"Universal({repr(self.variable)}, {repr(self.operand)})"
    
# ------------------------------------------------------------------------------------------------

# formula(f) ::= ("∀" | "∃") var "." "(" formula() ")" | complex(c)
def formula():
    if scanner.sym in (FORALL, EXIST):
        op=scanner.sym; oldPos=scanner.pos; getSym(); 
        if scanner.sym == VAR and scanner.val in string.ascii_lowercase:
            variable=scanner.val; oldPos=scanner.pos; getSym()
            if scanner.sym == DOT:
                getSym()
                if scanner.sym == LPAREN: 
                    getSym()
                    if   op == FORALL: f = Universal(op, variable, formula(), oldPos)
                    elif op == EXIST : f = Existential(op, variable, formula(), oldPos)
                    if scanner.sym == RPAREN: getSym()
                    else            : error(') missing', scanner.pos)
    else:  f = complex()
    return f


# complex(c) ::= term_or(t) { "⇒" complex(c) « t := Implies(IMPLIES, t, c) » }
def complex():
    t = term_or()
    while scanner.sym == IMPLIES:
        op = scanner.sym
        oldPos = scanner.pos
        getSym()
        t = Implies(op, t, complex(), oldPos)
    return t
    
    
       
# term_or(o) ::= term_and(t) { "∨" term_or(a) « t := Disjunction(LOR, t, o) » }
def term_or():
    t = term_and()
    # while SC.sym in (LAND, LOR):
    while scanner.sym == LOR:
        op = scanner.sym
        oldPos = scanner.pos
        getSym()
        t = Disjunction(op, t, term_or(), oldPos)
    return t    
    
       
# term_and(a) ::= factor(t) { "∧" term_and(a) « t := Conjunction(LAND, t, a) » }
def term_and():
    t = factor()
    while scanner.sym == LAND:
        op = scanner.sym
        oldPos = scanner.pos
        getSym()
        t = Conjunction(op, t, term_and(), oldPos)
    return t


# factor(f) ::= atom(f) 
#             | '(' complex(c) ')' «  »
#             | "¬" complex(c)     « Negation(NOT, c) »
def factor():
    if scanner.sym == VAR and scanner.val in string.ascii_uppercase:
        name = scanner.val
        oldPos = scanner.pos
        getSym()
        f = AtomicProp(name, oldPos)
        
        
    elif scanner.sym == LNOT:
        oldPos = scanner.pos
        getSym()
        if scanner.sym == VAR and scanner.val in string.ascii_uppercase:
            name = scanner.val
            oldPos = scanner.pos
            getSym()
            f = Negation(AtomicProp(name, oldPos), oldPos)
            
            
        elif scanner.sym == LPAREN:
            oldPos = scanner.pos
            getSym()
            f = Negation(complex(), oldPos)
            if scanner.sym == RPAREN: getSym()
            else            : error(') missing', scanner.pos)
        
        
    elif scanner.sym == LPAREN:    
        oldPos = scanner.pos
        getSym()
        f = complex()
        if scanner.sym == RPAREN: getSym()
        else            : error(') missing', scanner.pos)
        


    else: error("term expected", scanner.pos)
    return f



def ast(s):
    # global SC.src, SC.pos
    # global depth = 0
    scanner.src, scanner.pos = s, 0
    scanner.getChar()
    getSym()
    x = formula()
    return x


def translate(s):
    translation = str(ast(s))
    
    atomic_pattern = r"(?<=hold and [A-Z]) hold"
    imp_pattern    = r"hold holds"
    neg_pattern    = r"hold doesn't hold"
    dual_disjunct  = r"(?<=[A-Z] or [A-Z]) hold"
    
    substitutions = [
                        (atomic_pattern, r" holds"),
                        (imp_pattern,    r"hold"),
                        (neg_pattern,    r"doesn't hold"),
                        (dual_disjunct,  r" holds")
                    ]

    
    for pattern in substitutions:
        translation = re.sub(pattern[0], pattern[1], translation)
    
    print(translation)
    
    return translation


if __name__ == "__main__":
    
    x = input("Enter a logical expression: ")
    while x != 'q':
        
        print(f"{ast(x)}\n")
        x = input("Enter a logical expression: ")

    print("EXITED")
    
    
    
    
    

