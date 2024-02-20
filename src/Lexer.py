from .DFA import DFA
from .NFA import NFA
from .Regex import parse_regex

class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        
        self.specList = []
        self.alphabets = set()
        
        for token, regex in spec:
            dfa = parse_regex(regex).thompson().subset_construction()
            self.alphabets.update(dfa.S)
            self.specList.append((token, dfa))
        pass

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        
        #1) lexeme:
        copyWord = word
        nrLine = 0
        cut = 0
        start = 0
        end = len(word) 
        outputList = []
        
        accepted = False
        while True :
            end = len(word) - cut
            currentWord = word[start:end]
            
            #oprire 
            if cut >= len(word):
                break
           
            #pt fiecare cuvant vf daca am un dfa sa il accepte
            for token, dfa in self.specList:
                if dfa.accept(currentWord):
                    outputList.append((token, currentWord))
                    accepted = True
                    if currentWord == "\n":
                        nrLine += 1
                    break
            #daca am acceptat nu mai tai din cuvant si il resetez
            #caut in cuvantul de la vechiul cut si dupa
            if accepted == True:
                start = start + len(currentWord)
                cut = 0
                end = len(word)
                word = word[start:end]
                accepted = False
                start = 0
            #altfel tot tai din cuvant spre stanga pana gasesc 
            else:
                cut += 1
        
        #2) erori:
        outputList = self.error_check(outputList, copyWord)
            
        return outputList
    
    
    #eroarea apare daca lexemele concatenate nu fac cuvantul => 
    #nu s-a mai gasit longest match - in diferenta de cuv ramas e o eroare
    def error_check(self, outputList, word):
        
        checkedList = []
        error = str()
        lexemConcat = str()
        
        nrChar = 0
        lenLine = 0
        nrLine = 0
        for token, lexem in outputList:
            lexemConcat += lexem
        
        #aflare char si nr linie:
        for i in range(len(lexemConcat)):
            if lexemConcat[i] == "\n":
                nrLine += 1
                lenLine = 0
            else:
                lenLine += 1
        
        #nr ch = numar caract de pe acea linie
        nrChar = lenLine - 1        
        indexNextCh = len(lexemConcat)
        
        #1)EROARE:
        if  lexemConcat != word :
            #1)caract de la care difera este cel la len(lenxemTotal) din word
            #1) no alternative: ...CH - ch nu e din niciun alfabet, daca e:
            #                   ...CH x => x != EOF 
            #2) EOF:            ...CH x => x = EOF 
            symbol = word[indexNextCh]
            nrChar += 1
            
            if self.unknownCH(symbol) == True:
                error = "No viable alternative at character " + str(nrChar) + ", line " + str(nrLine)
            else:
                indexNextCh += 1
                if indexNextCh >= len(word):
                    error = "No viable alternative at character EOF, line " + str(nrLine)
                else:
                    nrChar, nrLine = self.findCH(word, nrChar, nrLine, indexNextCh-1)     
                    error = "No viable alternative at character " + str(nrChar) + ", line " + str(nrLine)
            
            noToken = ""
            checkedList.append((noToken, error))
        #2) FARA EROARE:
        else:
            checkedList = outputList   
            
        return checkedList
    

    def unknownCH(self, symbol) :
        
        if symbol in self.alphabets:
            return False
        else:
            return True
    
    #ex: tokenul bun ar fi fost: ACG(A|C|T)*CT 
    # cuvant ramas: ACGAAGCTCT =>eroarea apare la G 
    # V.ERROR: starea finala = sink -> fst char care intra in sink da eroarea
    def findCH(self, word, nrChar, nrLine, indexNextCh):
        
        for _, dfa in self.specList:
            if dfa.accept(word[indexNextCh: len(word)]) == False:
                if dfa.currentState == frozenset():
                   return dfa.nrChar + nrChar, nrLine + dfa.nrLine
