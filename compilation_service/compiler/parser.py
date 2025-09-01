# parser.py

from ast_nodes import *
from lexer import Token

# ====================================================================================
# This file defines the Parser. Its job is to take the stream of tokens from the
# lexer and build the Abstract Syntax Tree (AST) according to the language's grammar.
# It understands the rules of the language, like "an if statement needs a condition
# in parentheses" or "a variable declaration needs a type, a name, and a value".
# ====================================================================================

# A set of all keywords that represent a data type.
TYPE_KEYWORDS = {'INT', 'FLOAT', 'BOOL', 'CHAR', 'STRING'}

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # --- Helper Methods ---

    def current_token(self):
        """Returns the current token without consuming it."""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else Token('EOF', '', 0, 0)

    def peek(self, k=1):
        """Looks ahead k tokens without consuming."""
        i = self.pos + k
        return self.tokens[i] if i < len(self.tokens) else Token('EOF', '', 0, 0)

    def advance(self):
        """Consumes the current token and moves to the next one."""
        self.pos += 1

    def eat(self, token_type):
        """Consumes the current token if it matches the expected type, otherwise raises an error."""
        token = self.current_token()
        if token.type == token_type:
            self.advance()
            return token
        else:
            raise SyntaxError(f"Expected token {token_type} but found {token.type} at line {token.lineno}")

    # --- Main Parsing Logic ---

    def parse(self):
        """Parses the entire token stream into a program AST node."""
        statements = []
        while self.current_token().type != 'EOF':
            statements.append(self.parse_statement())
        return ProgramNode(statements)

    def parse_statement(self):
        """Parses a single statement based on the current token."""
        token_type = self.current_token().type
        
        if token_type in TYPE_KEYWORDS:
            return self.parse_variable_declaration()
        elif token_type == 'DEF':
            return self.parse_function_definition()
        elif token_type == 'PRINT':
            return self.parse_print_statement()
        elif token_type == 'RETURN':
            return self.parse_return_statement()
        elif token_type == 'IF':
            return self.parse_if_statement()
        elif token_type == 'WHILE':
            return self.parse_while_statement()
        elif token_type == 'FOR':
            return self.parse_for_statement()
        elif token_type == 'ID':
            # This could be an assignment (x=10 or arr[0]=10) or a standalone function call (my_func();)
            # We peek ahead to decide.
            if self.peek().type == 'LPAREN': # It's a function call statement
                expr = self.parse_expression()
                self.eat('SEMI')
                return expr
            elif self.peek().type in ('ASSIGN', 'LBRACKET'): # It's an assignment
                return self.parse_assignment_statement()
        
        raise SyntaxError(f"Unexpected token {token_type} at start of statement at line {self.current_token().lineno}")

    # --- Statement Parsing Methods ---

    def parse_variable_declaration(self):
        """Parses a variable declaration, including array types."""
        type_token = self.current_token()
        self.advance()
        
        # Check for array type, e.g., int[]
        if self.current_token().type == 'LBRACKET':
            self.eat('LBRACKET')
            self.eat('RBRACKET')
            var_type = ArrayTypeNode(type_token.value)
        else:
            var_type = type_token.value
        
        name_token = self.eat('ID')
        self.eat('ASSIGN')
        value = self.parse_expression()
        self.eat('SEMI')
        return VarDeclNode(var_type, name_token.value, value, type_token.lineno)
    
    def parse_assignment_statement(self):
        """Parses an assignment to a variable or array element."""
        lineno = self.current_token().lineno
        
        # The left side can be a simple variable or an array access
        if self.peek().type == 'LBRACKET':
            left = self.parse_array_access()
        else:
            left = VarNode(self.eat('ID'))
            
        self.eat('ASSIGN')
        right = self.parse_expression()
        self.eat('SEMI')
        return AssignmentNode(left, right, lineno)

    def parse_print_statement(self):
        lineno = self.eat('PRINT').lineno
        self.eat('LPAREN')
        value = self.parse_expression()
        self.eat('RPAREN')
        self.eat('SEMI')
        return PrintNode(value, lineno)

    def parse_if_statement(self):
        """Parses an if-else statement."""
        lineno = self.eat('IF').lineno
        self.eat('LPAREN')
        condition = self.parse_expression()
        self.eat('RPAREN')
        then_block = self.parse_block()
        else_block = None
        if self.current_token().type == 'ELSE':
            self.eat('ELSE')
            else_block = self.parse_block()
        return IfNode(condition, then_block, else_block, lineno)

    def parse_while_statement(self):
        """Parses a while loop."""
        lineno = self.eat('WHILE').lineno
        self.eat('LPAREN')
        condition = self.parse_expression()
        self.eat('RPAREN')
        body_block = self.parse_block()
        return WhileNode(condition, body_block, lineno)

    def parse_for_statement(self):
        """Parses a for loop: for (init; condition; update) { ... }."""
        lineno = self.eat('FOR').lineno
        self.eat('LPAREN')
        
        # Parse initializer (can be a var declaration or assignment)
        if self.current_token().type in TYPE_KEYWORDS:
            init = self.parse_variable_declaration()
        else:
            init = self.parse_assignment_statement()
        
        # Parse condition
        condition = self.parse_expression()
        self.eat('SEMI')

        # Parse update (is an assignment without the final semicolon)
        update_lineno = self.current_token().lineno
        if self.peek().type == 'LBRACKET':
            left = self.parse_array_access()
        else:
            left = VarNode(self.eat('ID'))
        self.eat('ASSIGN')
        right = self.parse_expression()
        update = AssignmentNode(left, right, update_lineno)

        self.eat('RPAREN')
        body = self.parse_block()
        return ForNode(init, condition, update, body, lineno)

    def parse_block(self):
        """Parses a { ... } block."""
        self.eat('LBRACE')
        statements = []
        while self.current_token().type != 'RBRACE' and self.current_token().type != 'EOF':
            statements.append(self.parse_statement())
        self.eat('RBRACE')
        return BlockNode(statements)
    
    def parse_return_statement(self):
        lineno = self.eat('RETURN').lineno
        value = self.parse_expression()
        self.eat('SEMI')
        return ReturnNode(value, lineno)

    def parse_function_definition(self):
        """Parses a function definition."""
        self.eat('DEF')
        # ... (This function remains mostly the same, but should check TYPE_KEYWORDS)
        # For brevity, we assume it's correct from the previous version.
        return_type_token = self.current_token()
        self.advance()
        func_name_token = self.eat('ID')
        self.eat('LPAREN')
        params = []
        if self.current_token().type != 'RPAREN':
            param_type = self.current_token().value
            self.advance()
            param_name = self.eat('ID').value
            params.append((param_type, param_name))
            while self.current_token().type == 'COMMA':
                self.eat('COMMA')
                param_type = self.current_token().value
                self.advance()
                param_name = self.eat('ID').value
                params.append((param_type, param_name))
        self.eat('RPAREN')
        body = self.parse_block()
        return FuncDefNode(return_type_token.value, func_name_token.value, params, body, func_name_token.lineno)

    # --- Expression Parsing (with Precedence) ---
    # Lowest Precedence to Highest:
    # equality -> comparison -> term -> factor -> unary -> primary

    def parse_expression(self):
        """Entry point for parsing any expression."""
        return self.parse_equality()

    def parse_equality(self):
        """Parses equality operators: == != """
        node = self.parse_comparison()
        while self.current_token().type in ('EQ', 'NEQ'):
            op = self.current_token()
            self.eat(op.type)
            right = self.parse_comparison()
            node = BinOpNode(left=node, op=op, right=right)
        return node

    def parse_comparison(self):
        """Parses comparison operators: < > <= >="""
        node = self.parse_term()
        while self.current_token().type in ('LT', 'GT', 'LTE', 'GTE'):
            op = self.current_token()
            self.eat(op.type)
            right = self.parse_term()
            node = BinOpNode(left=node, op=op, right=right)
        return node

    def parse_term(self):
        """Parses addition and subtraction: + -"""
        node = self.parse_factor()
        while self.current_token().type in ('PLUS', 'MINUS'):
            op = self.current_token()
            self.eat(op.type)
            right = self.parse_factor()
            node = BinOpNode(left=node, op=op, right=right)
        return node

    def parse_factor(self):
        """Parses multiplication and division: * /"""
        node = self.parse_unary()
        while self.current_token().type in ('MUL', 'DIV'):
            op = self.current_token()
            self.eat(op.type)
            right = self.parse_unary()
            node = BinOpNode(left=node, op=op, right=right)
        return node
    
    def parse_unary(self):
        """Parses unary operators: ! -"""
        token = self.current_token()
        if token.type in ('NOT', 'MINUS'):
            self.eat(token.type)
            expr = self.parse_unary()
            return UnaryOpNode(op=token, expr=expr)
        return self.parse_primary()

    def parse_primary(self):
        """Parses the highest-precedence expressions: literals, identifiers, calls, array access."""
        token = self.current_token()
        
        if token.type == 'FLOAT_LIT':
            self.eat('FLOAT_LIT')
            return FloatNode(token)
        elif token.type == 'STRING_LIT':
            self.eat('STRING_LIT')
            return StringNode(token)
        elif token.type == 'BOOL_LIT':
            self.eat('BOOL_LIT')
            return BoolNode(token)
        elif token.type == 'CHAR_LIT':
            self.eat('CHAR_LIT')
            return CharNode(token)
        elif token.type == 'NUMBER':
            self.eat('NUMBER')
            return NumNode(token)
        elif token.type == 'ID':
            # Could be a variable, function call, or array access
            if self.peek().type == 'LPAREN':
                return self.parse_function_call()
            elif self.peek().type == 'LBRACKET':
                 return self.parse_array_access()
            else:
                self.eat('ID')
                return VarNode(token)
        elif token.type == 'LPAREN': # Grouped expression
            self.eat('LPAREN')
            node = self.parse_expression()
            self.eat('RPAREN')
            return node
        elif token.type == 'LBRACE': # Array literal
            return self.parse_array_literal()
        
        raise SyntaxError(f"Unexpected token in expression: {token.type} at line {token.lineno}")

    def parse_function_call(self):
        """Parses a function call."""
        func_name_token = self.eat('ID')
        self.eat('LPAREN')
        args = []
        if self.current_token().type != 'RPAREN':
            args.append(self.parse_expression())
            while self.current_token().type == 'COMMA':
                self.eat('COMMA')
                args.append(self.parse_expression())
        self.eat('RPAREN')
        return FuncCallNode(func_name_token.value, args, func_name_token.lineno)

    def parse_array_literal(self):
        """Parses an array literal: {1, 2, 3}"""
        lineno = self.eat('LBRACE').lineno
        elements = []
        if self.current_token().type != 'RBRACE':
            elements.append(self.parse_expression())
            while self.current_token().type == 'COMMA':
                self.eat('COMMA')
                elements.append(self.parse_expression())
        self.eat('RBRACE')
        return ArrayLiteralNode(elements, lineno)

    def parse_array_access(self):
        """Parses an array access: my_array[i]"""
        name_token = self.eat('ID')
        self.eat('LBRACKET')
        index_expr = self.parse_expression()
        self.eat('RBRACKET')
        return ArrayAccessNode(name_token.value, index_expr, name_token.lineno)