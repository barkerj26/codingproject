A python script that converts an inputted grammar into one in Chomsky Normal Form

There are 10 test files included to see how the script works

To use:
 - Download and install Python 3.13.0 or greater
 - Open your terminal and navigate to the folder where the scripts are
 - Run main.py with your input file (ie. `python main.py test.g` or `python3 main.py test.g`)
 - Optionally, you can include an output file (ie. `python main.py test.g out.g`)

File overview:
 - main.py: handles running the script
 - grammario.py: handles file access
 - grammar.py: defines the grammar class and some generic helper functions
 - cnf.py: handles the bulk of the CNF conversion process

Input/output file structure:
 - All nonterminals must be prefixed with an underscore (ie. `_s`)
 - Everything must either be separated by a space or newline
 - Rules must start with the nonterminal in question, then an 'arrow' (`->`)
 - Rules must end with a semicolon (`;`)
 - To have multiple options per rule, add a bar (`|`)
 - To have an epsilon character, add an option with nothing in it
 - Example rule: `_A -> a b c | ;`
 - For more example of what can/can't be done, see the test cases