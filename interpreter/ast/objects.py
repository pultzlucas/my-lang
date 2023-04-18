class AST():
    pass

class ProgramMainNode(AST):
    def __init__(self, formal_params, block_node):
        self.formal_params = formal_params  # a list of Param nodes
        self.block_node = block_node

class FunctionDeclarationNode(AST):
    def __init__(self, proc_name, formal_params, block_node):
        self.proc_name = proc_name
        self.formal_params = formal_params  # a list of Param nodes
        self.block_node = block_node

class FunctionCallNode(AST):
    def __init__(self, proc_name, actual_params, token):
        self.proc_name = proc_name
        self.actual_params = actual_params  # a list of AST nodes
        self.token = token
        self.proc_symbol = None

class BlockNode(AST):
    def __init__(self, compound_statement):
        self.statements = []

class VarDeclarationNode(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node

class TypeNode(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class BinOpNode(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right
    
    def dict(self):
        return {
            'left': self.left.dict(),
            'op': self.op.type,
            'right': self.right.dict()
        }
    
class FactorNode(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def dict(self):
        return self.value
    
class UnaryOpNode(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
        
    def dict(self):
        return self.op

class AssignNode(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    def dict(self):
        return {
            'var': self.left,
            'op': self.op,
            'value': self.left
        }

class VarNode(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def dict(self):
        return {
            'var': self.token,
            'value': self.value
        }

class NoOpNode(AST):
    pass
    def dict(self):
        return 'empty'
    
class ParamNode(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node