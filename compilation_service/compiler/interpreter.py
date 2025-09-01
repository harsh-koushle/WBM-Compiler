# interpreter.py

from ast_nodes import *

# ====================================================================================
# This file defines the Interpreter. Its job is to "walk" the validated AST and
# execute the code. It keeps track of the program's state (like the values of
# variables) in an "Environment". For each node in the tree, it performs an action:
# - For a BinOpNode, it does the math.
# - For a VarDeclNode, it stores the variable in the environment.
# - For an IfNode, it makes a decision and executes the correct block.
# - For a WhileNode, it repeats a block of code.
# ====================================================================================

class ReturnValue(Exception):
    """An exception used to jump out of function calls with a return value."""
    def __init__(self, value):
        self.value = value

class Environment:
    """Manages variable and function storage with scopes."""
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}
        self.functions = {}

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Variable '{name}' not found.")

    def set(self, name, value):
        # We allow re-assignment to variables in the current or parent scopes
        if name in self.values or self.parent is None:
             self.values[name] = value
        elif self.parent:
             self.parent.set(name, value)
        else:
            raise NameError(f"Cannot assign to undefined variable '{name}'.")

    def declare(self, name, value):
        # Used for new variable declarations (var decl)
        self.values[name] = value
        
    def declare_function(self, name, node):
        self.functions[name] = node

    def get_function(self, name):
        func = self.functions.get(name)
        if func is None and self.parent:
            return self.parent.get_function(name)
        if func is None:
            raise NameError(f"Function '{name}' not found.")
        return func

class Interpreter:
    """The interpreter, responsible for executing the AST."""
    def __init__(self):
        self.environment = Environment()

    def visit(self, node, env):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, env)

    def generic_visit(self, node, env):
        raise NotImplementedError(f"No visit_{type(node).__name__} method")

    def interpret(self, ast):
        return self.visit(ast, self.environment)

    # --- Visitor Methods ---

    def visit_ProgramNode(self, node, env):
        for statement in node.statements:
            self.visit(statement, env)

    def visit_BlockNode(self, node, env):
        # Create a new scope for the block
        block_env = Environment(parent=env)
        for statement in node.statements:
            self.visit(statement, block_env)
    
    def visit_VarDeclNode(self, node, env):
        value = self.visit(node.value, env)
        env.declare(node.var_name, value)
    
    def visit_AssignmentNode(self, node, env):
        value = self.visit(node.right, env)
        
        if isinstance(node.left, VarNode):
            env.set(node.left.value, value)
        elif isinstance(node.left, ArrayAccessNode):
            array = env.get(node.left.name)
            index = self.visit(node.left.index, env)
            if not 0 <= index < len(array):
                raise IndexError(f"Array index out of bounds at line {node.lineno}")
            array[index] = value
        else:
            raise TypeError("The left-hand side of an assignment must be a variable or an array element.")

    def visit_IfNode(self, node, env):
        condition = self.visit(node.condition, env)
        if condition:
            self.visit(node.then_block, env)
        elif node.else_block:
            self.visit(node.else_block, env)
            
    def visit_WhileNode(self, node, env):
        while self.visit(node.condition, env):
            self.visit(node.body_block, env)

    def visit_ForNode(self, node, env):
        for_env = Environment(parent=env) # New scope for the loop variable
        self.visit(node.init, for_env)
        while self.visit(node.condition, for_env):
            self.visit(node.body_block, for_env)
            self.visit(node.update, for_env)
            
    def visit_PrintNode(self, node, env):
        value = self.visit(node.value, env)
        print(value)
        return value

    def visit_FuncDefNode(self, node, env):
        env.declare_function(node.func_name, node)

    def visit_FuncCallNode(self, node, env):
        func_node = env.get_function(node.func_name)
        args = [self.visit(arg, env) for arg in node.args]
        call_environment = Environment(parent=self.environment) # Functions see globals, not lexical scope
        
        for (param_type, param_name), arg_value in zip(func_node.params, args):
            call_environment.declare(param_name, arg_value)
        
        try:
            self.visit(func_node.body, call_environment)
        except ReturnValue as ret:
            return ret.value
        
        return None

    def visit_ReturnNode(self, node, env):
        value = self.visit(node.value, env)
        raise ReturnValue(value)

    def visit_BinOpNode(self, node, env):
        left_val = self.visit(node.left, env)
        right_val = self.visit(node.right, env)
        op_type = node.op.type

        if op_type == 'PLUS': return left_val + right_val
        if op_type == 'MINUS': return left_val - right_val
        if op_type == 'MUL': return left_val * right_val
        if op_type == 'DIV':
            if right_val == 0:
                raise ZeroDivisionError(f"Division by zero at line {node.left.lineno}")
            return left_val / right_val
        
        # Boolean comparisons
        if op_type == 'EQ': return left_val == right_val
        if op_type == 'NEQ': return left_val != right_val
        if op_type == 'LT': return left_val < right_val
        if op_type == 'GT': return left_val > right_val
        if op_type == 'LTE': return left_val <= right_val
        if op_type == 'GTE': return left_val >= right_val

    def visit_UnaryOpNode(self, node, env):
        expr_val = self.visit(node.expr, env)
        if node.op.type == 'NOT':
            return not expr_val
        if node.op.type == 'MINUS':
            return -expr_val

    def visit_NumNode(self, node, env): return int(node.value)
    def visit_FloatNode(self, node, env): return float(node.value)
    def visit_StringNode(self, node, env): return node.value[1:-1] # Remove quotes
    def visit_CharNode(self, node, env): return node.value[1:-1] # Remove quotes
    def visit_BoolNode(self, node, env): return True if node.value == 'true' else False
    def visit_VarNode(self, node, env): return env.get(node.value)

    def visit_ArrayLiteralNode(self, node, env):
        return [self.visit(elem, env) for elem in node.elements]

    def visit_ArrayAccessNode(self, node, env):
        array = env.get(node.name)
        index = self.visit(node.index, env)
        if not 0 <= index < len(array):
            raise IndexError(f"Array index out of bounds at line {node.lineno}")
        return array[index]