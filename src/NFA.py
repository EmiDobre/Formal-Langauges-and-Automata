from .DFA import DFA
from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''

@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        #closure ul fiecarei stari = set de stari:
        closure = set()
        closure.add(state)
        #folosesc stiva
        #seturile stari next al oricarei stari
        stack = [state]
        while stack:
            currentState = stack.pop()
            currentConfig = (currentState, EPSILON)
            #daca am tranzitie pe epsilon:
            if currentConfig in self.d:
                epsilon_nextStates = self.d[currentConfig]
                for next_state in epsilon_nextStates:
                    if next_state not in closure:
                        stack.append(next_state)
                        closure.add(next_state)
        return closure

    def subset_construction(self) -> DFA[frozenset[STATE]]:
            
        #Pas1: atribute dfa:
        dfa_d = {}
        dfa_K = set()
        dfa_F = set()
        dfa_q0 = frozenset(self.epsilon_closure(self.q0))
        
        #Pas2: elementele din stiva = reuniune de eps closure 
        stack = [dfa_q0]
        dfa_K.add(dfa_q0)
        stack.append(dfa_q0)
        
        while stack:
            closure = stack.pop()

            #tranzitii: pt fiecare simbol 
            for symbol in self.S:
                nextClosure_states = set()

                #aflare stari urmatoare pt fiecare stare din closure:
                for current_state in closure:
                    currentConfig = (current_state, symbol)
                    if currentConfig in self.d:
                        nextClosure_states.update(self.d[currentConfig])

                #setul de closure urmator: reuniune eps closure pt starile de next aflate
                closureReunion = set()
                for state in nextClosure_states:
                    closureReunion.update(self.epsilon_closure(state))

                #stare noua in dfa (din closure uri)
                dfaState = frozenset(closure)
                dfaStateNext = frozenset(closureReunion)
                if dfaStateNext not in dfa_K:    #daca nu am analizat deja starea
                    dfa_K.add(dfaStateNext)
                    stack.append(closureReunion)

                #tranzitia in dfa:
                dfaConfiguration = (dfaState, symbol)
                dfa_d[dfaConfiguration] = dfaStateNext

        #Pas3: starile finale: intersectie starile din "seturile frozen" (fiecare stare in dfa)
        #cu starile finale nfa
        for state in dfa_K:
            if state.intersection(self.F):
                dfa_F.add(state)

        dfa = DFA ( S = self.S,
                    K = dfa_K, 
                    q0 = dfa_q0,
                    d = dfa_d, 
                    F = dfa_F)
        return dfa
