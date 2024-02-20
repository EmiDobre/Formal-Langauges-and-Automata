from collections.abc import Callable
from dataclasses import dataclass

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    #de sters:
    def __str__(self):
        result = f"Alphabet (S): {self.S}\n"
        result += f"States (K): {self.K}\n"
        result += f"Initial State (q0): {self.q0}\n"
        result += "Transitions (d):\n"
        for (state, symbol), next_state in self.d.items():
            result += f"  {state} --{symbol}--> {next_state}\n"
        result += f"Final States (F): {self.F}\n"
        return result


    def accept(self, word: str) -> bool:
        #etapa3: VIABLE ERROR
        #index din cuv ramas al simbolului ce da eroare + linia
        self.firstInSink = 0
        self.nrChar = 0             
        self.nrLine = 0
        
        #incep de la q0
        self.currentState = self.q0
        #fiecare simbol din cuvant:
        for symbol in word:
            currentConfig = (self.currentState, symbol)
            #etapa3: nrchar, line
            if self.firstInSink == 0:
                self.nrChar += 1
                if symbol == "\n":
                    self.nrLine += 1
            
            #daca am stare next din aceasta config:
            if currentConfig in self.d:
                #starea acum e urm configuratie
                self.currentState = self.d[currentConfig]
                #de cate ori trec prin sink
                if self.currentState == frozenset():
                    self.firstInSink += 1
            else:
                return False
        
        #cuv este consumat: daca e intr-o stare finala: accept
        if self.currentState in self.F:
            return True
        else:
            return False