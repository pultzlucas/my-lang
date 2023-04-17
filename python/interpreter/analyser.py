from interpreter.tokens_type import TokenType as Tk
from interpreter.ast.objects import (
    BinOpNode,
    FactorNode,
    UnaryOpNode,
    CompoundNode,
    AssignNode,
    NoOpNode,
    VarNode,
    BlockNode,
    ProgramNode,
    VarDeclarationNode,
    TypeNode,
    ProcedureDeclarationNode,
    ParamNode,
    ProcedureCallNode
)

from interpreter.exceptions import ParserError, ErrorCode 

ADITIVE_OPERATOR = (Tk.PLUS, Tk.MINUS)
RELATIONAL_OPERATOR = (Tk.EQ, Tk.NOT_EQ, Tk.GT, Tk.LT, Tk.EQ_GT, Tk.EQ_LT)
MULTIPLICATIVE_OPERATOR = (Tk.MUL, Tk.DIV, Tk.MOD, Tk.FLOORDIV)


class Analyser:
    def __init__(self, lexer) -> None:
        self.lexer = lexer
        pass

    def eat(self, token_type):
        if self.lexer.current_token.type == token_type:
            self.lexer.current_token = self.lexer.next_token()
            return
        self.error(
            error_code=ErrorCode.UNEXPECTED_TOKEN,
            token=self.lexer.current_token,
        )

    def error(self, error_code, token):
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )

    def factor(self):
        token = self.lexer.current_token
        if token.type == Tk.INTEGER_CONST:
            self.eat(Tk.INTEGER_CONST)
            return FactorNode(token)
        elif token.type == Tk.REAL_CONST:
            self.eat(Tk.REAL_CONST)
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
        """
        term
            : factor (EXPONENT term)?
        """
        node = self.factor()
        token = self.lexer.current_token
        if token.type == Tk.EXPONENT:
            self.eat(Tk.EXPONENT)
            node = BinOpNode(left=node, op=token, right=self.term())
        return node

    def simple_term(self):
        """
        simple_term
            : term (MULTIPLICATIVE_OPERATOR simple_term)?
            ;
        """
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
        """
        simple_expr
            : simple_term (ADITIVE_OPERATOR simple_term)?
            ;
        """
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
        """
        relational_expr
            : simple_term (RELATIONAL_OPERATOR relational_expr)?
            ;
        """
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
        """
        and_expr
            : relational_expr (AND and_expr)?
            ;
        """
        node = self.relational_expr()
        if self.lexer.current_token.type == Tk.AND:
            token = self.lexer.current_token
            if token.type == Tk.AND:
                self.eat(Tk.AND)
            node = BinOpNode(left=node, op=token, right=self.and_expr())
        return node

    def or_expr(self):
        """
        or_expr
            : simple_expr (relational_operator simple_expr)*
            ;
        """
        node = self.and_expr()
        if self.lexer.current_token.type == Tk.OR:
            token = self.lexer.current_token
            if token.type == Tk.OR:
                self.eat(Tk.OR)
            node = BinOpNode(left=node, op=token, right=self.or_expr())
        return node

    def expr(self):
        """
        expr
            : or_expr
            ;
        """
        return self.or_expr()

    def program(self):
        self.eat(Tk.PROGRAM)
        var = self.variable()
        self.eat(Tk.SEMICOLON)
        block = self.block()
        self.eat(Tk.DOT)
        return ProgramNode(name=var.value, block=block)

    def block(self):
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = BlockNode(declaration_nodes, compound_statement_node)
        return node

    def formal_parameters(self):
        param_nodes = []
        param_tokens = [self.lexer.current_token]
        self.eat(Tk.ID)
        while self.lexer.current_token.type == Tk.COMMA:
            self.eat(Tk.COMMA)
            param_tokens.append(self.lexer.current_token)
            self.eat(Tk.ID)
        self.eat(Tk.COLON)
        type_node = self.type_spec()
        for param_token in param_tokens:
            param_node = ParamNode(VarNode(param_token), type_node)
            param_nodes.append(param_node)
        return param_nodes

    def formal_parameter_list(self):
        params = self.formal_parameters()
        if self.lexer.current_token.type == Tk.SEMICOLON:
            self.eat(Tk.SEMICOLON)
            params.extend(self.formal_parameter_list())
        return params
    
    def proccall_statement(self):
        token = self.lexer.current_token
        proc_name = self.lexer.current_token.value
        self.eat(Tk.ID)
        self.eat(Tk.LPAREN)
        actual_params = []
        if self.lexer.current_token.type != Tk.RPAREN:
            node = self.expr()
            actual_params.append(node)

        while self.lexer.current_token.type == Tk.COMMA:
            self.eat(Tk.COMMA)
            node = self.expr()
            actual_params.append(node)

        self.eat(Tk.RPAREN)

        node = ProcedureCallNode(
            proc_name=proc_name,
            actual_params=actual_params,
            token=token,
        )
        return node

    def declarations(self):
        declarations = []
        while self.lexer.current_token.type == Tk.VAR:
            self.eat(Tk.VAR)
            while self.lexer.current_token.type == Tk.ID:
                var_declaration = self.variable_declaration()
                declarations.extend(var_declaration)
                self.eat(Tk.SEMICOLON)
        while self.lexer.current_token.type == Tk.PROCEDURE:
            declarations.append(self.procedure_declaration())
        return declarations


    def procedure_declaration(self):
        self.eat(Tk.PROCEDURE)
        proc_name = self.lexer.current_token.value
        self.eat(Tk.ID)
        params = []
        if self.lexer.current_token.type == Tk.LPAREN:
            self.eat(Tk.LPAREN)
            params = self.formal_parameter_list()
            self.eat(Tk.RPAREN)
        self.eat(Tk.SEMICOLON)
        block_node = self.block()
        proc_decl = ProcedureDeclarationNode(proc_name, params, block_node)
        self.eat(Tk.SEMICOLON)
        return proc_decl


    def variable_declaration(self):
        var_nodes = [VarNode(self.lexer.current_token)]
        self.eat(Tk.ID)
        while self.lexer.current_token.type == Tk.COMMA:
            self.eat(Tk.COMMA)
            var_nodes.append(VarNode(self.lexer.current_token))
            self.eat(Tk.ID)
        self.eat(Tk.COLON)
        type_spec = self.type_spec()
        return [
            VarDeclarationNode(var_node, type_spec) for var_node in var_nodes
        ]

    def type_spec(self):
        token = self.lexer.current_token
        if token.type == Tk.INTEGER:
            self.eat(Tk.INTEGER)
        if token.type == Tk.REAL:
            self.eat(Tk.REAL)
        return TypeNode(token)

    def compound_statement(self):
        self.eat(Tk.BEGIN)
        nodes = self.statement_list()
        self.eat(Tk.END)

        root = CompoundNode()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self):
        node = self.statement()
        results = [node]
        while self.lexer.current_token.type == Tk.SEMICOLON:
            self.eat(Tk.SEMICOLON)
            results.append(self.statement())
        return results

    def statement(self):
        if self.lexer.current_token.type == Tk.BEGIN:
            node = self.compound_statement()
        elif (self.lexer.current_token.type == Tk.ID and
              self.lexer.current_char == '('
        ):
            node = self.proccall_statement()
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

    def variable(self):
        node = VarNode(self.lexer.current_token)
        self.eat(Tk.ID)
        return node

    def empty(self):
        return NoOpNode()

    def parse(self):
        node = self.program()
        if self.lexer.current_token.type != Tk.EOF:
            self.error(Tk.EOF, self.lexer.current_token.type)
        return node
