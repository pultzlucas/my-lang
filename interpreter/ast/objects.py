class AST():
    pass

class ProgramNode(AST):
    def __init__(self, init_block, utils = []):
        self.init_block = init_block
        self.utils = utils

    def dict(self):
        return {
            'init_block': self.init_block.dict(),
            'utils': [stt.dict() for stt in self.utils] 
        }
    
class FunctionDeclarationNode(AST):
    def __init__(self, fun_name, formal_params, block_node):
        self.fun_name = fun_name
        self.formal_params = formal_params  # a list of Param nodes
        self.block_node = block_node

    def dict(self):
        return {
            'fun_name': self.fun_name,
            'formal_params': [param.dict() for param in self.formal_params],
            'block': self.block_node.dict()
        }

class FunctionCallNode(AST):
    def __init__(self, fun_name, actual_params, token):
        self.fun_name = fun_name
        self.actual_params = actual_params  # a list of AST nodes
        self.token = token
        self.proc_symbol = None

    def dict(self):
        return {
            'fun_name': self.fun_name,
            'params': [param.dict() for param in self.actual_params]
        }

class BlockNode(AST):
    def __init__(self, statements = []):
        self.statements = statements

    def dict(self):
        return [stt.dict() for stt in self.statements]

class TypeNode(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def dict(self):
        return str(self.value)
    
class BinOpNode(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right
    
    def dict(self):
        return {
            'left': self.left.dict(),
            'op': self.op.value,
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
            'var': self.left.value,
            'op': self.op.value,
            'value': self.right.dict()
        }

class VarDeclarationNode(AST):
    def __init__(self, var_node, type_node, assign_node=None):
        self.var_node = var_node
        self.type_node = type_node
        self.assign_node = assign_node

    def dict(self):
        return {
            'var': self.var_node.value,
            'type' : self.type_node.value,
            'value' : self.assign_node.dict() if self.assign_node else None
        }

class VarNode(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def dict(self):
        return {
            'var': self.value,
            'value' : self.value
        }

class NoOpNode(AST):
    def dict(self):
        return 'empty'
    
class ParamNode(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node
    
    def dict(self): 
        return {
            'var' : self.var_node.value,
            'type' : self.type_node.value
        }
    
class ConditionalOpNode(AST):
    def __init__(self, condition_expr, block_node):
        self.condition_expr = condition_expr
        self.block_node = block_node

    def dict(self):
        return {
            'condition_expr': self.condition_expr.dict(),
            'block': self.block_node.dict()
        }