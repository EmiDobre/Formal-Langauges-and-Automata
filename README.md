# Formal-Langauges-and-Automata

The project for this course is implementing a Lexer in Python. A Lexer receives a specification formed as:
>TOKEN1 : REGEX1;
>
>TOKEN2 : REGEX2;
>
>TOKEN3 : REGEX3;
>....

where each TOKENi is a name given to a token, and REGEXi is a regex that describes lexemes that can classify that token.

The Lexer has the following output: [(lexema1, TOKEN_LEXEMA_1), (lexema2, TOKEN_LEXEMA_2), …], where TOKEN_LEXEMA_N is the name of the token for the n-th lexem based on the specification.

 Lexer class
-
- it is a constructor that receives a specification described earlier
- it has the *lex* function that does the lexer's job basically => from a given word based on the specification of the Lexer it gives a list of tuples  (token, lexem_word)
  
*example*:   Lexer with spec = [("TOKEN1", "abbc*"), ("TOKEN2", "ab+"), ("TOKEN3", "a*d")]

             lex("abbd") => abb satisfies TOKEN1 being the longest match and also TOKEN2 but it will choose the first in the spec => TOKEN1
             
                         =>   d will be identified as TOKEN3
             
*result*: [(TOKEN1, "abb"), (TOKEN3, "d")]

The idea behind the Lexer:
-
For identifying the longest match in a word to a certain token in the specification of the Lexer it is enough to "cut" from the initial word starting from the initial word, cutting one letter until we find the longest match or the word is used. A part of the word is considered the longest match if the DFA of the regex form spec accepts that part of the word.

For this, I introduce another concept: DFA, NFA, and Regex to help with finding the longest match and tokenizing the word. Finding the DFA automata for a regex is done in multiple steps: 

regex----THOMPSON---->nfa----SUBSET CONSTRUCTION---->dfa.

Regex---->THOMPSON---->Nfa:
-
- For this part, Thompson's algorithm transforms a regex into its nondeterministic finite automata representation.
  
- Regex: describes a sequence of characters

- Operations: | - union; * - star; . - concatenation
  
- The order of the characters matters and for this, it is important to use a parsing tree that helps with the order. I used binary trees that respect the order when being traversed Root Left Right, the root is the operation between left and right regexes, and so on until the leaves are just symbols.
  
- Example:
  
              a | b = UNION( a, b)

              a* = STAR(_, a)
 
              ab = CONCAT(a,b)
 
              (....) = anything in parenthesis is like a "symbol", it will be a subtree in the parsing tree
 
              a|b*(de)* = UNION(a, CONCAT( STAR(_, b), STAR( CONCAT(d, e)) ) )
 
- After transforming each regex into its parsing tree the nfa just follows the Root Left Right subtree and transforms each subtree into its specific nfa.

Nfa---->SUBSET CONSTRUCTION---->Dfa:
-

- DFA/NFA:
  
               S - alphabet of the language            
               K - states of the automata, set of __STATE__
               q0 - initial state
               d - transition function, a dictionary (state, character), and another state as the value (or states for NFA)
               F - final states of the DFA
- Differences:
  
              NFA: has epsilon transitions, d the transition function will be a set of successor states

  *Algorithm*:

- Start with the initial state of the NFA.
  
- Determine the set of states that can be reached from this initial state by following epsilon transitions (transitions that don't consume any input).

- For each input symbol, determine the set of states that can be reached from the states obtained in the previous step by following transitions labeled with that input symbol.

- Each set of states represents a single state in the DFA.
  
- The resulting DFA will have states corresponding to sets of states from the original NFA, and transitions between states will correspond to transitions between sets of states in the NFA.


Testing
-
For testing the code it is needed version python3.12 ( install here: https://aruljohn.com/blog/install-python/)
For running the tests:  python3.12 -m unittest which detects automatically the tests defined in the test folder.
                            
