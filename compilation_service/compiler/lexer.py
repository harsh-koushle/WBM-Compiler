# lexer.py

import re
from collections import namedtuple

# ====================================================================================
# This file defines the Lexer. Its job is to take the raw source code string and
# break it down into a stream of "tokens". Each token is a small piece of the
# language, like a keyword, an operator, or a number.
# ====================================================================================

TokenType = namedtuple('TokenType', ['name', 'pattern'])
Token = namedtuple('Token', ['type', 'value', 'lineno', 'column'])

TOKEN_SPECS = [
    # -- Structural Tokens --
    TokenType('COMMENT',   r'//.*'),
    TokenType('WHITESPACE',r'\s+'),

    # -- Keywords for New Features --
    TokenType('IF',        r'\bif\b'),
    TokenType('ELSE',      r'\belse\b'),
    TokenType('WHILE',     r'\bwhile\b'),
    TokenType('FOR',       r'\bfor\b'),
    TokenType('STRING',    r'\bstring\b'),

    # -- Existing Keywords --
    TokenType('BOOL',      r'\bbool\b'),
    TokenType('CHAR',      r'\bchar\b'),
    TokenType('FLOAT',     r'\bfloat\b'),
    TokenType('INT',       r'\bint\b'),
    TokenType('DEF',       r'\bdef\b'),
    TokenType('RETURN',    r'\breturn\b'),
    TokenType('PRINT',     r'\bprint\b'),
    
    # -- Literals (Order is important!) --
    TokenType('STRING_LIT',r'"[^"]*"'),  # Match text in double quotes
    TokenType('FLOAT_LIT', r'\d+\.\d+'),    # Must come before NUMBER
    TokenType('BOOL_LIT',  r'\b(true|false)\b'),
    TokenType('CHAR_LIT',  r'\'[^\']\''), # Match a single character in single quotes
    TokenType('NUMBER',    r'\d+'),

    # -- Identifiers --
    TokenType('ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'),
    
    # -- Operators and Delimiters --
    # Comparison operators
    TokenType('EQ',        r'=='),
    TokenType('NEQ',       r'!='),
    TokenType('GTE',       r'>='),
    TokenType('LTE',       r'<='),
    TokenType('GT',        r'>'),
    TokenType('LT',        r'<'),
    
    # Logical NOT operator
    TokenType('NOT',       r'!'),

    # Standard operators and delimiters
    TokenType('ASSIGN',    r'='),
    TokenType('PLUS',      r'\+'),
    TokenType('MINUS',     r'-'),
    TokenType('MUL',       r'\*'),
    TokenType('DIV',       r'/'),
    
    # Brackets for arrays
    TokenType('LBRACKET',  r'\['),
    TokenType('RBRACKET',  r'\]'),

    TokenType('LPAREN',    r'\('),
    TokenType('RPAREN',    r'\)'),
    TokenType('LBRACE',    r'\{'),
    TokenType('RBRACE',    r'\}'),
    TokenType('SEMI',      r';'),
    TokenType('COMMA',     r','),
    
    # Any other character is a mismatch
    TokenType('MISMATCH',  r'.'),
]

class Lexer:
    """The lexer, responsible for turning a string into tokens."""
    def __init__(self, code):
        self.code = code
        # We build one big regular expression from all the small ones.
        # This is very efficient.
        tok_regex = '|'.join(f'(?P<{spec.name}>{spec.pattern})' for spec in TOKEN_SPECS)
        self.tok_regex = re.compile(tok_regex)
        self.lineno = 1
        self.line_start = 0

    def tokenize(self):
        """Yields tokens from the source code."""
        tokens = []
        # finditer() finds all non-overlapping matches for our big regex.
        for mo in self.tok_regex.finditer(self.code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - self.line_start

            # Skip whitespace and comments, but track line numbers.
            if kind == 'WHITESPACE' or kind == 'COMMENT':
                if '\n' in value:
                    self.lineno += value.count('\n')
                    self.line_start = mo.end()
                continue
            
            # If we find a character that doesn't match any rule, it's an error.
            if kind == 'MISMATCH':
                raise RuntimeError(f'Unexpected character: {value!r} at line {self.lineno}:{column}')

            tokens.append(Token(kind, value, self.lineno, column))
        
        # Add a special "End of File" token to make parsing easier.
        tokens.append(Token('EOF', '', self.lineno, 0))
        return tokens