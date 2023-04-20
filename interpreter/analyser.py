from interpreter.tokens_type import TokenType as Tk
from interpreter.ast.objects import (
    BinOpNode,
    FactorNode,
    UnaryOpNode,
    AssignNode,
    NoOpNode,
    VarNode,
    BlockNode,
    FunctionDeclarationNode,
    ParamNode,
    TypeNode,
    VarDeclarationNode,
    ProgramNode
)

from interpreter.exceptions import ParserError, ErrorCode 

ADITIVE_OPERATOR = (Tk.PLUS, Tk.MINUS)
RELATIONAL_OPERATOR = (Tk.EQ, Tk.NOT_EQ, Tk.GT, Tk.LT, Tk.EQ_GT, Tk.EQ_LT)
MULTIPLICATIVE_OPERATOR = (Tk.MUL, Tk.DIV, Tk.MOD, Tk.FLOORDIV)


class Analyser:
    def __init__(self, lexer) -> None:
        self.lexer = lexer
        pass

    def parse(self):
        node = self.program()
        if self.lexer.current_token.type != Tk.EOF:
            self.error(Tk.EOF, self.lexer.current_token.type)
        return node

    def eat(self, token_type):
        if self.lexer.current_token.type == token_type:
            self.lexer.current_token = self.lexer.next_token()
            return
        self.error(token_type, self.lexer.current_token.type)

    def error(self, expected, unexpected):
        raise Exception(f'Unexpected token "{unexpected}", expected "{expected}"')

    def program(self):
        return ProgramNode(declarations=self.declarations())        

    def declarations(self):
        declarations = [self.function_declaration()]
        while self.lexer.current_token.type == Tk.FUN:
            declarations.append(self.function_declaration())
        if len(declarations) == 0:
            return [self.empty()]
        return declarations

    def variable_declaration(self):
        var_node = VarNode(self.lexer.current_token)
        self.eat(Tk.ID)
        self.eat(Tk.COLON)
        type_spec = self.type_spec()
        return VarDeclarationNode(var_node, type_spec)

    def function_declaration(self):
        self.eat(Tk.FUN)
        fun_name = self.lexer.current_token.value
        self.eat(Tk.ID)
        params = []
        if self.lexer.current_token.type == Tk.LPAREN:
            self.eat(Tk.LPAREN)
            if self.lexer.current_token.type != Tk.RPAREN:
                params = self.formal_parameter_list()
            self.eat(Tk.RPAREN)
        block_node = self.block()
        fun_decl = FunctionDeclarationNode(fun_name, params, block_node)
        return fun_decl

    def formal_parameter_list(self):
        params = [self.formal_parameter()]
        if self.lexer.current_token.type == Tk.COMMA:
            self.eat(Tk.SEMICOLON)
            params.extend(self.formal_parameter_list())
        return params

    def formal_parameter(self):
        param_token = self.variable()
        self.eat(Tk.COLON)
        type_node = self.type_spec()
        return ParamNode(param_token, type_node)

    def type_spec(self):
        token = self.lexer.current_token
        if token.type == Tk.INT:
            self.eat(Tk.INT)
        if token.type == Tk.FLOAT:
            self.eat(Tk.FLOAT)
        return TypeNode(token)

    def variable(self):
        node = VarNode(self.lexer.current_token)
        self.eat(Tk.ID)
        return node

    def block(self):
        self.eat(Tk.DO)
        statement_list = self.statement_list()
        self.eat(Tk.END)
        return BlockNode(statement_list)

    
    # def funcall_statement(self):
    #     token = self.lexer.current_token
    #     fun_name = self.lexer.current_token.value
    #     self.eat(Tk.ID)
    #     self.eat(Tk.LPAREN)
    #     actual_params = []
    #     if self.lexer.current_token.type != Tk.RPAREN:
    #         node = self.expr()
    #         actual_params.append(node)

    #     while self.lexer.current_token.type == Tk.COMMA:
    #         self.eat(Tk.COMMA)
    #         node = self.expr()
    #         actual_params.append(node)

    #     self.eat(Tk.RPAREN)

    #     node = FunctionCallNode(
    #         fun_name=fun_name,
    #         actual_params=actual_params,
    #         token=token,
    #     )
    #     return node

    # def variable_declaration(self):
    #     var_nodes = [VarNode(self.lexer.current_token)]
    #     self.eat(Tk.ID)
    #     while self.lexer.current_token.type == Tk.COMMA:
    #         self.eat(Tk.COMMA)
    #         var_nodes.append(VarNode(self.lexer.current_token))
    #         self.eat(Tk.ID)
    #     self.eat(Tk.COLON)
    #     type_spec = self.type_spec()
    #     return [
    #         VarDeclarationNode(var_node, type_spec) for var_node in var_nodes
    #     ]

    def statement_list(self):
        results = [self.statement()]
        while self.lexer.current_token.type == Tk.SEMICOLON:
            self.eat(Tk.SEMICOLON)
            results.append(self.statement())
        return results

    def statement(self):
        if self.lexer.current_token.type == Tk.ID and self.lexer.current_char == ':':
            node = self.variable_declaration()
        elif self.lexer.current_token.type == Tk.ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        left = self.variable()
        token = self.lexer.current_token
        self.eat(Tk.ASSIGN)
        right = self.expr()
        node = AssignNode(left, token, right)
        return node

    def factor(self):
        token = self.lexer.current_token
        if token.type == Tk.INTEGER_VALUE:
            self.eat(Tk.INTEGER_VALUE)
            return FactorNode(token)
        elif token.type == Tk.REAL_VALUE:
            self.eat(Tk.REAL_VALUE)
            return FactorNode(token)
        elif self.lexer.current_token.type == Tk.BOOLEAN:
            self.eat(Tk.BOOLEAN)
            return FactorNode(token)
        elif self.lexer.current_token.type == Tk.STRING:
            self.eat(Tk.STRING)
            return FactorNode(token)
        elif token.type == Tk.PLUS:
            self.eat(Tk.PLUS)
            node = UnaryOpNode(token, self.factor())
            return node
        elif token.type == Tk.MINUS:
            self.eat(Tk.MINUS)
            node = UnaryOpNode(token, self.factor())
            return node
        elif token.type == Tk.NOT:
            self.eat(Tk.NOT)
            node = UnaryOpNode(token, self.factor())
            return node
        elif self.lexer.current_token.type == Tk.LPAREN:
            self.eat(Tk.LPAREN)
            node = self.expr()
            self.eat(Tk.RPAREN)
            return node
        elif self.lexer.current_token.type == Tk.ID:
            return self.variable()
        elif self.lexer.current_token.type == Tk.NON:
            self.eat(Tk.NON)
            return FactorNode(token)

    def term(self):
        node = self.factor()
        token = self.lexer.current_token
        if token.type == Tk.EXPONENT:
            self.eat(Tk.EXPONENT)
            node = BinOpNode(left=node, op=token, right=self.term())
        return node

    def simple_term(self):
        node = self.term()
        if self.lexer.current_token.type in MULTIPLICATIVE_OPERATOR:
            token = self.lexer.current_token
            if self.lexer.current_token.type == Tk.MUL:
                self.eat(Tk.MUL)
            if self.lexer.current_token.type == Tk.DIV:
                self.eat(Tk.DIV)
            if self.lexer.current_token.type == Tk.MOD:
                self.eat(Tk.MOD)
            if self.lexer.current_token.type == Tk.FLOORDIV:
                self.eat(Tk.FLOORDIV)
            node = BinOpNode(left=node, op=token, right=self.simple_term())
        return node

    def simple_expr(self):
        node = self.simple_term()
        if self.lexer.current_token.type in ADITIVE_OPERATOR:
            token = self.lexer.current_token
            if token.type == Tk.PLUS:
                self.eat(Tk.PLUS)
            if token.type == Tk.MINUS:
                self.eat(Tk.MINUS)
            node = BinOpNode(left=node, op=token, right=self.simple_expr())
        return node

    def relational_expr(self):
        node = self.simple_expr()
        if self.lexer.current_token.type in RELATIONAL_OPERATOR:
            token = self.lexer.current_token
            if self.lexer.current_token.type == Tk.EQ:
                self.eat(Tk.EQ)
            if self.lexer.current_token.type == Tk.NOT_EQ:
                self.eat(Tk.NOT_EQ)
            if self.lexer.current_token.type == Tk.GT:
                self.eat(Tk.GT)
            if self.lexer.current_token.type == Tk.LT:
                self.eat(Tk.LT)
            if self.lexer.current_token.type == Tk.EQ_GT:
                self.eat(Tk.EQ_GT)
            if self.lexer.current_token.type == Tk.EQ_LT:
                self.eat(Tk.EQ_LT)
            node = BinOpNode(left=node, op=token, right=self.relational_expr())
        return node

    def and_expr(self):
        node = self.relational_expr()
        if self.lexer.current_token.type == Tk.AND:
            token = self.lexer.current_token
            if token.type == Tk.AND:
                self.eat(Tk.AND)
            node = BinOpNode(left=node, op=token, right=self.and_expr())
        return node

    def or_expr(self):
        node = self.and_expr()
        if self.lexer.current_token.type == Tk.OR:
            token = self.lexer.current_token
            if token.type == Tk.OR:
                self.eat(Tk.OR)
            node = BinOpNode(left=node, op=token, right=self.or_expr())
        return node

    def expr(self):
        return self.or_expr()

    def empty(self):
        return NoOpNode()
