from interpreter.tokens_type import TokenType as Tk
from interpreter.ast.visitor import NodeVisitor
from interpreter.stack import CallStack, ActivationRecord, ARType
import json 

_SHOULD_LOG_STACK = False

class ASTJsonBuilder():
    def __init__(self, ast):
        self.ast = ast
        self.json_obj = {}

    def run(self):
        return json.dumps(self.ast.dict(), indent = 4)

class Executor(NodeVisitor):
    def __init__(self, ast):
        self.ast = ast
        self.call_stack = CallStack()

    def run(self):
        return self.visit(self.ast)
    
    def log(self, msg):
        if _SHOULD_LOG_STACK:
            print(msg)

    def visit_ProgramNode(self, node):
        self.log(f'ENTER: main')
        ar = ActivationRecord(
            name='main',
            type=ARType.PROGRAM,
            nesting_level=1,
        )
        self.call_stack.push(ar)
        self.log(str(self.call_stack))
        self.visit(node.init_block)
        self.log(f'LEAVE: main')
        self.log(str(self.call_stack))
        self.call_stack.pop()

    def visit_VarDeclarationNode(self, node):
        # Do nothing
        pass

    def visit_TypeNode(self, node):
        # Do nothing
        pass

    def visit_BinOpNode(self, node):
        if node.op.type == Tk.PLUS: return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == Tk.MINUS: return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == Tk.MUL: return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == Tk.DIV: return self.visit(node.left) / self.visit(node.right)
        elif node.op.type == Tk.MOD: return self.visit(node.left) % self.visit(node.right)
        elif node.op.type == Tk.FLOORDIV: return self.visit(node.left) // self.visit(node.right)
        elif node.op.type == Tk.EXPONENT: return self.visit(node.left) ** self.visit(node.right)
        elif node.op.type == Tk.AND: return self.visit(node.left) and self.visit(node.right)
        elif node.op.type == Tk.OR: return self.visit(node.left) or self.visit(node.right)
        elif node.op.type == Tk.GT: return self.visit(node.left) > self.visit(node.right)
        elif node.op.type == Tk.LT: return self.visit(node.left) < self.visit(node.right)
        elif node.op.type == Tk.EQ_GT: return self.visit(node.left) >= self.visit(node.right)
        elif node.op.type == Tk.EQ_LT: return self.visit(node.left) <= self.visit(node.right)
        elif node.op.type == Tk.EQ: return self.visit(node.left) == self.visit(node.right)
        elif node.op.type == Tk.NOT_EQ: return self.visit(node.left) != self.visit(node.right)

    def visit_FactorNode(self, node):
        return node.value
    
    def visit_UnaryOpNode(self, node):
        if node.op.type == Tk.PLUS:
            return +self.visit(node.expr)
        elif node.op.type == Tk.MINUS:
            return -self.visit(node.expr)
        elif node.op.type == Tk.NOT:
            return not self.visit(node.expr)
        
    def visit_BlockNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_NoOpNode(self, node):
        pass

    def visit_AssignNode(self, node):
        var_name = node.left.value
        var_value = self.visit(node.right)
        ar = self.call_stack.peek()
        ar[var_name] = var_value

    def visit_VarNode(self, node):
        var_name = node.value
        ar = self.call_stack.peek()
        var_value = ar.get(var_name)
        return var_value
        
    def visit_FunctionDeclarationNode(self, node):
        pass

    def visit_FunctionCallNode(self, node):
        fun_name = node.fun_name
        fun_symbol = node.fun_symbol
        ar = ActivationRecord(
            name=fun_name,
            type=ARType.PROCEDURE,
            nesting_level=fun_symbol.scope_level + 1,
        )
        formal_params = fun_symbol.formal_params
        actual_params = node.actual_params
        for param_symbol, argument_node in zip(formal_params, actual_params):
            ar[param_symbol.name] = self.visit(argument_node)
        self.call_stack.push(ar) 
        self.log(f'ENTER: PROCEDURE {fun_name}')
        self.log(str(self.call_stack))

        self.visit(fun_symbol.block_ast)  
        self.log(f'LEAVE: PROCEDURE {fun_name}')
        self.log(str(self.call_stack))
        self.call_stack.pop()