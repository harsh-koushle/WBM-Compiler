import sys
import traceback
import time  # <--- NEW: Import the time module

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from interpreter import Interpreter

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <filename>")
        sys.exit(1)

    source_filename = sys.argv[1]

    try:
        with open(source_filename, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{source_filename}'")
        sys.exit(1)


    
    try:
        # 1. Lexer
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        # 2. Parser
        parser = Parser(tokens)
        ast = parser.parse()

        # 3. Semantic Analyzer
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.visit(ast)

        # --- NEW: Start the timer ---
        start_time = time.time()

        # 4. Interpreter
        interpreter = Interpreter()
        interpreter.interpret(ast)

        # --- NEW: Stop the timer and calculate duration ---
        end_time = time.time()
        duration = end_time - start_time

        # --- UPDATED: Print the final message with the time ---
        print(f"\n--- Execution finished in {duration:.4f} seconds ---")

    except Exception as e:
        print("--- An error occurred ---")
        traceback.print_exc()

if __name__ == '__main__':
    main()
