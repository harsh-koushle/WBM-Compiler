# ast_nodes.py

# ====================================================================================
# This file defines the structure of our language's Abstract Syntax Tree (AST).
# Every construct in the language, like a variable declaration or a function call,
# will be represented by one of these "node" classes. The parser's job is to
# build a tree of these nodes from the source code.
# ====================================================================================

class ASTNode:
    """Base class for all AST nodes."""
    pass

# --- Program and Block Nodes ---

class ProgramNode(ASTNode):
    """Represents the entire program: a list of statements."""
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"ProgramNode({self.statements})"

class BlockNode(ASTNode):
    """Represents a block of code enclosed in curly braces {}, like a function body."""
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"BlockNode({self.statements})"

# --- Statement Nodes ---

class VarDeclNode(ASTNode):
    """Represents a variable declaration, e.g., int x = 10; """
    def __init__(self, var_type, var_name, value, lineno):
        self.var_type = var_type
        self.var_name = var_name
        self.value = value
        self.lineno = lineno
    def __repr__(self):
        return f"VarDeclNode(type={self.var_type}, name='{self.var_name}', value={self.value})"

class AssignmentNode(ASTNode):
    """NEW: Represents an assignment to an existing variable, e.g., x = 20; or my_array[0] = 5; """
    def __init__(self, left, right, lineno):
        self.left = left    # The variable or array element being assigned to
        self.right = right  # The value being assigned
        self.lineno = lineno
    def __repr__(self):
        return f"AssignmentNode(left={self.left}, right={self.right})"

class PrintNode(ASTNode):
    """Represents a print statement, e.g., print(x); """
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno
    def __repr__(self):
        return f"PrintNode(value={self.value})"

class IfNode(ASTNode):
    """NEW: Represents an if-else statement."""
    def __init__(self, condition, then_block, else_block, lineno):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block  # Can be None if there is no else part
        self.lineno = lineno
    def __repr__(self):
        return f"IfNode(condition={self.condition}, then={self.then_block}, else={self.else_block})"

class WhileNode(ASTNode):
    """NEW: Represents a while loop."""
    def __init__(self, condition, body_block, lineno):
        self.condition = condition
        self.body_block = body_block
        self.lineno = lineno
    def __repr__(self):
        return f"WhileNode(condition={self.condition}, body={self.body_block})"

class ForNode(ASTNode):
    """NEW: Represents a C-style for loop."""
    def __init__(self, init, condition, update, body_block, lineno):
        self.init = init            # e.g., int i = 0
        self.condition = condition  # e.g., i < 10
        self.update = update        # e.g., i = i + 1
        self.body_block = body_block
        self.lineno = lineno
    def __repr__(self):
        return f"ForNode(init={self.init}, cond={self.condition}, update={self.update}, body={self.body_block})"

# --- Function-related Nodes ---

class FuncDefNode(ASTNode):
    """Represents a function definition."""
    def __init__(self, return_type, func_name, params, body, lineno):
        self.return_type = return_type
        self.func_name = func_name
        self.params = params
        self.body = body
        self.lineno = lineno
    def __repr__(self):
        return f"FuncDefNode(name='{self.func_name}', params={self.params}, body={self.body})"

class ReturnNode(ASTNode):
    """Represents a return statement."""
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno
    def __repr__(self):
        return f"ReturnNode(value={self.value})"

# --- Expression Nodes ---

class BinOpNode(ASTNode):
    """Represents a binary operation, e.g., x + y or i < 10."""
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"BinOpNode(left={self.left}, op='{self.op.value}', right={self.right})"

class UnaryOpNode(ASTNode):
    """NEW: Represents a unary operation, e.g., !is_active."""
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    def __repr__(self):
        return f"UnaryOpNode(op='{self.op.value}', expr={self.expr})"

class FuncCallNode(ASTNode):
    """Represents a function call, e.g., add(5, 10)."""
    def __init__(self, func_name, args, lineno):
        self.func_name = func_name
        self.args = args
        self.lineno = lineno
    def __repr__(self):
        return f"FuncCallNode(name='{self.func_name}', args={self.args})"

# --- Literal and Variable Nodes ---

class NumNode(ASTNode):
    """Represents an integer literal."""
    def __init__(self, token):
        self.value = token.value
        self.lineno = token.lineno
    def __repr__(self):
        return f"NumNode({self.value})"

class FloatNode(ASTNode):
    """Represents a float literal."""
    def __init__(self, token):
        self.value = token.value
        self.lineno = token.lineno
    def __repr__(self):
        return f"FloatNode({self.value})"

class StringNode(ASTNode):
    """NEW: Represents a string literal."""
    def __init__(self, token):
        self.value = token.value
        self.lineno = token.lineno
    def __repr__(self):
        return f"StringNode({self.value})"

class CharNode(ASTNode):
    """Represents a character literal."""
    def __init__(self, token):
        self.value = token.value
        self.lineno = token.lineno
    def __repr__(self):
        return f"CharNode({self.value})"

class BoolNode(ASTNode):
    """Represents a boolean literal (true or false)."""
    def __init__(self, token):
        self.value = token.value
        self.lineno = token.lineno
    def __repr__(self):
        return f"BoolNode({self.value})"

class VarNode(ASTNode):
    """Represents a variable being used/accessed."""
    def __init__(self, token):
        self.value = token.value
        self.lineno = token.lineno
    def __repr__(self):
        return f"VarNode('{self.value}')"

# --- Array-related Nodes ---

class ArrayTypeNode(ASTNode):
    """NEW: Represents an array type, like int[] or float[]."""
    def __init__(self, base_type):
        self.base_type = base_type
    def __repr__(self):
        return f"ArrayTypeNode(base_type={self.base_type})"

class ArrayLiteralNode(ASTNode):
    """NEW: Represents an array literal, e.g., {1, 2, 3}."""
    def __init__(self, elements, lineno):
        self.elements = elements
        self.lineno = lineno
    def __repr__(self):
        return f"ArrayLiteralNode(elements={self.elements})"

class ArrayAccessNode(ASTNode):
    """NEW: Represents accessing an array element, e.g., my_array[i]."""
    def __init__(self, name, index, lineno):
        self.name = name
        self.index = index
        self.lineno = lineno
    def __repr__(self):
        return f"ArrayAccessNode(name='{self.name}', index={self.index})"