import copy
from .NFA import NFA
from collections.abc import Callable
EPSILON = '' 


class Regex:
    def __init__(self, operation=None, left=None, right=None):
        self.operation = operation
        self.left = left
        self.right = right
        
    def is_empty(self):
        return all(value is None for value in (self.operation, self.left, self.right))
    
    #egalitate intre regexuri
    def __eq__(self, other):
        if isinstance(other, Regex):
            return (
                self.operation == other.operation and
                self.left == other.left and
                self.right == other.right
            )
        return False
    
    #vf daca nodul e frunza:
    def is_leaf(self):
        return self.left is None and self.right is None
    
  
    #inlocuiesc un subtree cu alt tree 
    def update_TreeNextNode(self, subtree, new_tree):
        if self == subtree:
            return self.copy_tree(new_tree)
        elif self.right is not None:
            self.right = self.right.update_TreeNextNode(subtree, new_tree)
        return self
    
    def copy_tree(self, other):
        if other is None:
            return None
        return Regex(
            operation=other.operation,
            left=self.copy_tree(other.left),
            right=self.copy_tree(other.right)
        )

    def __str__(self):
        return self._str_recursive()

    def _str_recursive(self, node=None):
        if node is None:
            node = self

        if node.left is None and node.right is None:
            return str(node.operation)

        left_str = self._str_recursive(node.left) if node.left else ""
        right_str = self._str_recursive(node.right) if node.right else ""

        if node.operation == 'CONCAT':
            return f"CONCAT({left_str}, {right_str})"
        elif node.operation == 'UNION':
            return f"UNION({left_str}, {right_str})"
        elif node.operation == 'STAR':
            return f"STAR({left_str},{right_str})"
        elif node.operation == 'PLUS':
            return f"PLUS({left_str},{right_str})"
        elif node.operation == 'QUESTION':
            return f"QUESTION({left_str},{right_str})"
        else:
            return str(node.operation)
 
    #aplic thmpson in ordinea data de arbore
    def thompson(self) -> NFA[int]:
        nfa = NFA[int]
        nfa, _ = self.thompsonRecursive(0) 
        #print(nfa)   
        return nfa

    #python retine referinteee deci grijaa la recurente!!
    def thompsonRecursive(self, nrStates):
        if self.is_leaf():
            return self.leaf_to_nfa(nrStates), nrStates + 2
        
        elif self.operation == 'CONCAT':
            left_nfa, nrStates = self.left.thompsonRecursive(nrStates)
            right_nfa, nrStates = self.right.thompsonRecursive(nrStates)
            return self.concat_to_nfa(left_nfa, right_nfa), nrStates
        
        elif self.operation == 'UNION':
            left_nfa, nrStates = self.left.thompsonRecursive(nrStates)
            right_nfa, nrStates = self.right.thompsonRecursive(nrStates)
            return self.union_to_nfa(left_nfa, right_nfa, nrStates), nrStates + 2
        
        elif self.operation == 'STAR':
            content_nfa, nrStates = self.right.thompsonRecursive(nrStates)
            return self.star_to_nfa(content_nfa, nrStates), nrStates + 2  

        elif self.operation == 'PLUS':
            content_nfa, nrStates = self.right.thompsonRecursive(nrStates)
            copyContent, nrStates = self.copy_nfa1_to_nfa2(content_nfa, nrStates)
            starContent = self.star_to_nfa(content_nfa, nrStates)
            nrStates += 2     
            return self.concat_to_nfa(copyContent, starContent), nrStates
        
        elif self.operation == 'QUESTION':
            content_nfa, nrStates = self.right.thompsonRecursive(nrStates)
            eps_nfa = self.nfa_EPSILON(nrStates)
            nrStates += 1
            return self.union_to_nfa(content_nfa, eps_nfa, nrStates), nrStates + 2
        

    def nfa_EPSILON(self, nrStates):
        initial_state = nrStates + 1
        alphabet = set()
        states = set()
        states.add(initial_state)
        transitions = {}
        final_state = initial_state
        nfa = NFA(S=alphabet, K=states, q0=initial_state, d=transitions, F={final_state})
        return nfa
        

    def leaf_to_nfa(self, nrStates):
        symbol = str(self)
        firstNr = nrStates + 1
        lastNr = firstNr + 1
    
        first = int(firstNr)
        last = int(lastNr)
    
        alphabet = {symbol}
        k = {first, last}
        q0 = first
        d = {(first, symbol): {last}}
        f = {last}
    
        nfa = NFA(S=alphabet, K=k, q0=q0, d=d, F=f)        
        return nfa 

   
    def concat_to_nfa(self, left_nfa, right_nfa):      
        #alfabet = reuniune stari reuniune
        alphabet = left_nfa.S.union(right_nfa.S)
        states = left_nfa.K.union(right_nfa.K)
        
        #stare init si finala:
        initial_state = left_nfa.q0
        final_state = right_nfa.F.pop()  
        
        #tranzitii: ambele + inca o eps tranz
        transitions = dict(left_nfa.d)
        transitions.update(right_nfa.d)
        epsilon_transition = (left_nfa.F.pop(), EPSILON)
        transitions[epsilon_transition] = {right_nfa.q0}

        nfa = NFA(S=alphabet, K=states, q0=initial_state, d=transitions, F={final_state})
        return nfa 
    
    def union_to_nfa(self, left_nfa, right_nfa, nrStates):      
        #alfabet = reuniune stari reuniune
        alphabet = left_nfa.S.union(right_nfa.S)
        states = left_nfa.K.union(right_nfa.K)
        
        #stare init si finala: + adaugate la states
        initial_state = nrStates + 1
        final_state = nrStates + 2
        states.add(initial_state)
        states.add(final_state)
        
        #tranzitii: toate de pana acum
        transitions = dict(left_nfa.d)
        transitions.update(right_nfa.d)
        
        #tranzitii: inca 4 eps tranz
        eps_transInit = (initial_state, EPSILON)       
        transitions[eps_transInit] = {left_nfa.q0, right_nfa.q0}
        eps_transFinalLeft = (left_nfa.F.pop(), EPSILON)
        transitions[eps_transFinalLeft] = {final_state}
        eps_transFinalRight = (right_nfa.F.pop(), EPSILON)
        transitions[eps_transFinalRight] = {final_state}

        nfa = NFA(S=alphabet, K=states, q0=initial_state, d=transitions, F={final_state})
        return nfa 
        
    def star_to_nfa(self, content_nfa, nrStates):
        #alfabet, stari de pana acum:
        alphabet = content_nfa.S
        states = content_nfa.K

        #stare init si finala noi:
        initial_state = nrStates + 1
        final_state = nrStates + 2
        states.add(initial_state)
        states.add(final_state)
        
        #tranzitii pastrate:
        transitions = dict(content_nfa.d)
        
        #traanzitii noi: inca 4 
        eps_transInit = (initial_state, EPSILON) 
        transitions[eps_transInit] = {content_nfa.q0, final_state}
        eps_transBack = (content_nfa.F.pop(), EPSILON)
        transitions[eps_transBack] = {content_nfa.q0, final_state}
        
        nfa = NFA(S=alphabet, K=states, q0=initial_state, d=transitions, F={final_state})
        return nfa 
    

    def copy_nfa1_to_nfa2(self, nfa, nrStates):
        
        # fiecare stare: nume nou = nr Stari + 1 ... 
        #copiere alfabet/stari cu nume nou
        alphabet = nfa.S 
        nfaFinal_state = next(iter(nfa.F))
        initial_state = len(nfa.K) + nfa.q0
        final_state = len(nfa.K) + nfaFinal_state
        states = set()
        transitions = {}
        
        #nume nou stari:
        #echivalari tranzitii:
        for (src, symbol), destinations in nfa.d.items():
            new_src =  src + len(nfa.K)
            new_destinations = {dest + len(nfa.K) for dest in destinations}
            transitions[(new_src, symbol)] = new_destinations
            
            states.add(new_src)
            
        new_nfa = NFA(S=alphabet, K=states, q0=initial_state, d=transitions, F={final_state})
        return new_nfa, nrStates + len(nfa.K)
        

def parse_regex(regex: str) -> Regex:
    #Pas1: transofmrare in tokeni
    tokens = build_regexTokens(regex)
    #Pas2: transformare in arbore
    regexTree = Regex()
    regex, _ , _ , _ = parse_expression(regexTree, tokens, 0, "NONE")
    
    
    return regex



#Pas1: parsare regex in tokens: ('tip simbol', caracter) 
#pentru a trasnforma [] in tupluri nu regex simplu
#dictionar de tupluri 
def isSymbol(symbol, readAsSymbol):
    #] nu se pune pt ca daca am [ care nu e parte din regex
    #] nu se mai citeste deloc 
    invalid_characters = set("()[|+?*")
    if readAsSymbol == True:
        return True
    else:
        return symbol not in invalid_characters

#index = simbolul anterior
def readSymbol(index, regex, readAsSymbol):
    index = index + 1
    symbol = regex[index]
    readAsSymbol = False
    
    #\simbol => simbolul e parte din limbaj
    if symbol == '\\':
        index = index + 1
        symbol = regex[index]
        readAsSymbol = True
        
        return symbol, index, readAsSymbol
    #altfel escape white space daca e cazul
    if symbol == ' ':
        index = index + 1
        symbol = regex[index]   
    
    return symbol, index, readAsSymbol
  

#Constructie tokeni:
def build_regexTokens(regex: str):
    tokens = {}      
    index = -1
    readAsSymbol = False
    tokenIndex = 0

    while index < len(regex) - 1:
        symbol, index, readAsSymbol = readSymbol(index, regex, readAsSymbol)
        #simbolul valid = operatie sau doar simbol:
        if isSymbol(symbol, readAsSymbol):
            token = ('SYMBOL', symbol)
            tokens[tokenIndex] = token
            tokenIndex += 1   
        else:
            if symbol == '[':
                tokenIndex, tokens = syntactic_sugar(index, tokenIndex, tokens, regex)
                index = index + 4 
            else:       
                typeSymbol = ""
                if symbol == '|':
                    typeSymbol = 'UNION'
                if symbol == '*':
                    typeSymbol = 'STAR'
                if symbol == '+':
                    typeSymbol = 'PLUS'
                if symbol == '?':
                    typeSymbol = 'QUESTION'
                if symbol == '(':                
                    typeSymbol = 'PARANTEZA('
                if symbol == ')':
                    typeSymbol = 'PARANTEZA)'
                token = (typeSymbol, symbol)
                tokens[tokenIndex] = token
                tokenIndex += 1
    return tokens

def syntactic_sugar(index, tokenIndex, tokens, regex ):
    
    start = regex[index + 1]
    end = regex[index + 3]
    token = ('PARANTEZA(', '(')
    tokens[tokenIndex] = token
    tokenIndex += 1
    #cifre
    if start.isdigit() and end.isdigit():
        nr = int(start)
        while nr <= int(end):
            token = ('SYMBOL', str(nr))
            tokens[tokenIndex] = token
            tokenIndex += 1
            if nr != int(end):
                token = ('UNION', '|')
                tokens[tokenIndex] = token
                tokenIndex += 1  
            nr += 1     
    #litere:
    if start.isalpha() and end.isalpha():
        current_char = start
        while current_char <= end:
            token = ('SYMBOL', current_char)
            tokens[tokenIndex] = token
            tokenIndex += 1
            if current_char != end:
                token = ('UNION', '|')
                tokens[tokenIndex] = token
                tokenIndex += 1
            current_char = chr(ord(current_char) + 1)   
    
    #end:
    token = ('PARANTEZA)', ')')
    tokens[tokenIndex] = token
    tokenIndex += 1
    
    return tokenIndex, tokens


#Pas2: din tokeni construiesc parsing tree:
def parse_expression(regexTree, tokens, index, last_operation):
  
    typeSymbol = ""
    symbol = ""
    lastSubTree = Regex()
        
    while index < len(tokens):
        (typeSymbol, symbol) = tokens[index]

        #1)Citesc SIMBOL => fac CONCAT sau UNION
        if typeSymbol == 'SYMBOL':
            #INCEPUT:
            if last_operation == 'NONE':
                if regexTree.is_empty():
                    regexTree = Regex(symbol)
                    last_operation = 'CONCAT'
                    lastSubTree = regexTree
            #AM DEJA o operatie:
            else:    
                if last_operation != 'UNION_TO_DO':
                    regexTree, index, last_operation, lastSubTree = parse_concat(regexTree, tokens, index, last_operation, lastSubTree)
                else:
                    regexTree, index, last_operation, lastSubTree  = parse_union(regexTree, tokens, index, last_operation, lastSubTree)
                
        #1)Citesc STAR/PLUS/QUESTION:  - aplicat pe () sau simbol
        if typeSymbol == 'STAR' or typeSymbol == 'PLUS' or typeSymbol == 'QUESTION':
            last_operation = typeSymbol
            #a* sau ()* <=> subtree*
            if lastSubTree.is_empty() == False:
                startree = Regex( typeSymbol, right = lastSubTree)
                regexTree = regexTree.update_TreeNextNode(lastSubTree, startree)
                lastSubTree = startree
          
        #2)Citesc UNIUNE: setez ca urm caracter va face uniunea
        if typeSymbol == 'UNION':
            last_operation = 'UNION_TO_DO'
    
        #3)Citesc PARANTEZE ( sau ):
        if typeSymbol == 'PARANTEZA(':
            #Inceput:
            if last_operation == 'NONE':
                regexTree, index, last_operation, lastSubTree = parse_expression(regexTree, tokens, index + 1, "NONE")
                lastSubTree = regexTree
            #Am deja op: UNIUNE SAU CONCAT cu ce e in paranteza
            else:
                if last_operation != 'UNION_TO_DO':
                    regexTree, index, last_operation, lastSubTree = parse_concat(regexTree, tokens, index, last_operation, lastSubTree)
                else:
                    regexTree, index, last_operation, lastSubTree = parse_union(regexTree, tokens, index, last_operation, lastSubTree)
    
        #4)Reintoarcere din call recursiv: ...) - back cu regeTree ul din parateza:
        if typeSymbol == 'PARANTEZA)':
            #lastSubTree este paranteza insasi (...)
            return regexTree, index, last_operation, regexTree
        
        index += 1         
            
    return regexTree, index, last_operation, lastSubTree


#CONCATENARI : citesc simbol sau ( 
def parse_concat(regexTree, tokens, index, last_operation, lastSubTree):
    (typeSymbol, symbol) = tokens[index]
    
    if typeSymbol == 'SYMBOL':
        #PRIOR mai mare: ...subtree A: => ....CONCAT subtree, A
        # | subtree A, UNION ...-> newright; subTree(deja stelat sau nu) A -> Concat..., newright
            last_operation = 'CONCAT'
            newRight = Regex('CONCAT', left = lastSubTree, right = Regex(symbol))
            regexTree = regexTree.update_TreeNextNode(lastSubTree, newRight)
            #actualizare subtree
            lastSubTree = Regex(symbol)
            
    #TODO (
    if typeSymbol == 'PARANTEZA(':
        #PRIOR mai mare: *(.. : aplic pe subtree 
            last_operation = 'CONCAT'
            newRight = Regex()
            newRight, index, _, lastSubTree = parse_expression(newRight, tokens, index + 1, 'NONE')
            regexTree = Regex('CONCAT', left = regexTree, right = newRight)       
        

    return regexTree, index, last_operation, lastSubTree


#UNIUN la simbol sau paranteza
#cea mai mica prior: devine parinte 
def parse_union(regexTree, tokens, index, last_operation, lastSubTree):
    (typeSymbol, symbol) = tokens[index]
    
    #....| a => subTree e acum a (in caz ca aplic concat sau star pe el)
    #=> UNION left = ...; right = Regex(a)
    if typeSymbol == 'SYMBOL':
        last_operation = 'UNION'
        regexTree = Regex('UNION', left = regexTree, right = Regex(symbol))
        lastSubTree = Regex(symbol)
    #..| (..
    if typeSymbol == 'PARANTEZA(':
        last_operation = 'UNION'
        newRight = Regex()
        newRight, index, _, lastSubTree = parse_expression(newRight, tokens, index + 1, 'NONE')
        regexTree = Regex('UNION', left = regexTree, right = newRight) 
    
    return regexTree, index, last_operation, lastSubTree