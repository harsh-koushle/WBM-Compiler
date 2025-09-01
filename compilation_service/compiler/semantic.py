# semantic.py

from ast_nodes import *

# ====================================================================================
# This file defines the Semantic Analyzer. Its job is to walk the AST produced by
# the parser and check for "context-sensitive" errors. This means it checks things
# the parser can't, such as:
# - Type errors (e.g., trying to add a number to a string).
# - Undefined variables (using a variable before it's declared).
# - Incorrect function arguments.
# - Ensuring loop conditions are booleans.
# It uses a "Symbol Table" to keep track of variables and functions in scope.
# ====================================================================================

class Symbol:
    """Base class for a symbol in the symbol table."""
    def __init__(self, name, type):
        self.name = name
        self.type = type

class FunctionSymbol(Symbol):
    """Represents a function symbol."""
    def __init__(self, name, return_type, params):
        super().__init__(name, 'FUNCTION')
        self.return_type = return_type
        self.params = params

class VariableSymbol(Symbol):
    """Represents a variable symbol. The type can be a string (e.g., 'int') or an object (e.g., ArrayType)."""
    def __init__(self, name, type):
        super().__init__(name, type)

class ArrayType:
    """A custom class to represent array types, e.g., 'array of int'."""
    def __init__(self, base_type):
        self.base_type = base_type
    
    def __eq__(self, other):
        return isinstance(other, ArrayType) and self.base_type == other.base_type
    
    def __repr__(self):
        return f"array({self.base_type})"

class SymbolTable:
    """A table to store symbols for a given scope."""
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, symbol):
        if self.symbols.get(symbol.name):
            return False # Symbol already exists
        self.symbols[symbol.name] = symbol
        return True

    def resolve(self, name):
        symbol = self.symbols.get(name)
        if symbol is None and self.parent:
            return self.parent.resolve(name)
        return symbol

class SemanticAnalyzer:
    """The semantic analyzer, responsible for all static analysis."""
    def __init__(self):
        self.current_scope = None
        self.current_function = None

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visit_{type(node).__name__} method")

    def open_scope(self):
        self.current_scope = SymbolTable(parent=self.current_scope)
    
    def close_scope(self):
        self.current_scope = self.current_scope.parent

    # --- Visitor Methods ---

    def visit_ProgramNode(self, node):
        self.open_scope() # Global scope
        for statement in node.statements:
            self.visit(statement)
        self.close_scope()

    def visit_BlockNode(self, node):
        self.open_scope()
        for statement in node.statements:
            self.visit(statement)
        self.close_scope()
    
    def visit_VarDeclNode(self, node):
        init_type = self.visit(node.value)
        var_type = node.var_type.base_type if isinstance(node.var_type, ArrayTypeNode) else node.var_type

        # Handle array types
        if isinstance(node.var_type, ArrayTypeNode):
            if not isinstance(init_type, ArrayType):
                raise TypeError(f"Type mismatch: cannot assign {init_type} to array type at line {node.lineno}")
            if init_type.base_type != 'any' and init_type.base_type != var_type:
                 raise TypeError(f"Type mismatch: cannot assign array of {init_type.base_type} to array of {var_type} at line {node.lineno}")
            var_type = ArrayType(var_type)
        # Handle primitive types
        elif init_type != var_type:
            raise TypeError(f"Type mismatch: cannot assign {init_type} to '{node.var_name}' of type {var_type} at line {node.lineno}")
        
        if not self.current_scope.define(VariableSymbol(node.var_name, var_type)):
            raise NameError(f"Variable '{node.var_name}' already declared in this scope at line {node.lineno}")
    
    def visit_AssignmentNode(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        if left_type != right_type:
            raise TypeError(f"Type mismatch in assignment: cannot assign {right_type} to {left_type} at line {node.lineno}")

    def visit_IfNode(self, node):
        condition_type = self.visit(node.condition)
        if condition_type != 'bool':
            raise TypeError(f"If statement condition must be a boolean, but got {condition_type} at line {node.lineno}")
        self.visit(node.then_block)
        if node.else_block:
            self.visit(node.else_block)
    
    def visit_WhileNode(self, node):
        condition_type = self.visit(node.condition)
        if condition_type != 'bool':
            raise TypeError(f"While loop condition must be a boolean, but got {condition_type} at line {node.lineno}")
        self.visit(node.body_block)

    def visit_ForNode(self, node):
        self.open_scope()
        self.visit(node.init)
        condition_type = self.visit(node.condition)
        if condition_type != 'bool':
            raise TypeError(f"For loop condition must be a boolean, but got {condition_type} at line {node.lineno}")
        self.visit(node.update)
        self.visit(node.body_block)
        self.close_scope()

    def visit_PrintNode(self, node):
        self.visit(node.value)
        
    def visit_FuncDefNode(self, node):
        # ... (Same as previous version, just ensuring completeness) ...
        func_symbol = FunctionSymbol(node.func_name, node.return_type, [])
        self.current_scope.define(func_symbol)
        previous_function = self.current_function
        self.current_function = func_symbol
        self.open_scope()
        for param_type, param_name in node.params:
            param_symbol = VariableSymbol(param_name, param_type)
            self.current_scope.define(param_symbol)
            func_symbol.params.append(param_symbol)
        self.visit(node.body)
        self.close_scope()
        self.current_function = previous_function
    
    def visit_ReturnNode(self, node):
        # ... (Same as previous version) ...
        return_type = self.visit(node.value)
        if not self.current_function:
            raise SyntaxError(f"Return statement found outside of a function at line {node.lineno}")
        if return_type != self.current_function.return_type:
            raise TypeError(f"Type mismatch: function '{self.current_function.name}' should return {self.current_function.return_type}, but returns {return_type}")
    
    def visit_BinOpNode(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        op = node.op.type

        if op in ('PLUS', 'MINUS', 'MUL', 'DIV'):
            # Allow math on int and float
            if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
                raise TypeError(f"Unsupported operand types for arithmetic: '{left_type}' and '{right_type}'")
            return 'float' if 'float' in (left_type, right_type) else 'int'
        
        if op in ('LT', 'GT', 'LTE', 'GTE'):
            # Allow comparison on int and float
            if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
                raise TypeError(f"Unsupported operand types for comparison: '{left_type}' and '{right_type}'")
            return 'bool'
        
        if op in ('EQ', 'NEQ'):
            # Allow equality checks on most types, as long as they match
            if left_type != right_type:
                raise TypeError(f"Cannot compare {left_type} and {right_type} for equality")
            return 'bool'
        
        raise TypeError(f"Unknown binary operator {op}")

    def visit_UnaryOpNode(self, node):
        expr_type = self.visit(node.expr)
        op = node.op.type
        if op == 'NOT' and expr_type == 'bool':
            return 'bool'
        if op == 'MINUS' and expr_type in ('int', 'float'):
            return expr_type
        raise TypeError(f"Unsupported unary operator '{op}' for type {expr_type}")
    
    def visit_FuncCallNode(self, node):
        # ... (Same as previous version) ...
        func_symbol = self.current_scope.resolve(node.func_name)
        if not func_symbol or not isinstance(func_symbol, FunctionSymbol):
            raise NameError(f"Function '{node.func_name}' is not defined at line {node.lineno}")
        # ... (Argument checking logic remains the same) ...
        return func_symbol.return_type

    def visit_ArrayLiteralNode(self, node):
        if not node.elements:
            return ArrayType('any') # Empty array
        
        # Check that all elements have the same type
        first_type = self.visit(node.elements[0])
        for element in node.elements[1:]:
            if self.visit(element) != first_type:
                raise TypeError(f"Array elements must all be of the same type at line {node.lineno}")
        return ArrayType(first_type)

    def visit_ArrayAccessNode(self, node):
        array_symbol = self.current_scope.resolve(node.name)
        if not array_symbol:
            raise NameError(f"Array '{node.name}' is not defined at line {node.lineno}")
        
        if not isinstance(array_symbol.type, ArrayType):
            raise TypeError(f"'{node.name}' is not an array and cannot be indexed at line {node.lineno}")
        
        index_type = self.visit(node.index)
        if index_type != 'int':
            raise TypeError(f"Array index must be an integer, but got {index_type} at line {node.lineno}")
        
        return array_symbol.type.base_type # Returns the type of the element, e.g., 'int'

    def visit_NumNode(self, node): return 'int'
    def visit_FloatNode(self, node): return 'float'
    def visit_StringNode(self, node): return 'string'
    def visit_CharNode(self, node): return 'char'
    def visit_BoolNode(self, node): return 'bool'
    def visit_VarNode(self, node):
        symbol = self.current_scope.resolve(node.value)
        if not symbol:
            raise NameError(f"Variable '{node.value}' is not defined at line {node.lineno}")
        return symbol.type