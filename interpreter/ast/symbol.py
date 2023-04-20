from interpreter.ast.visitor import NodeVisitor
from interpreter.exceptions import SemanticError, ErrorCode

class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type
        self.scope_level = 0

_SHOULD_LOG_SCOPE = False

class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

    __repr__ = __str__


class VarSymbol(Symbol):
    def __init__(self, name, type):
        super().__init__(name, type)

    def __str__(self):
        return '<{name}:{type}>'.format(name=self.name, type=self.type)

    __repr__ = __str__


class FunctionSymbol(Symbol):
    def __init__(self, name, formal_params=None):
        super(FunctionSymbol, self).__init__(name)
        self.formal_params = [] if formal_params is None else formal_params
        self.block_ast = None

    def __str__(self):
        return '<{class_name}(name={name}, params={params} block_ast={block_ast})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.formal_params,
            block_ast=self.block_ast
        )

    __repr__ = __str__


class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

        if scope_level == 0:
            self._init_builtins()

    def _init_builtins(self):
        self.insert(BuiltinTypeSymbol('INT'))
        self.insert(BuiltinTypeSymbol('FLOAT'))

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope',
             self.enclosing_scope.scope_name if self.enclosing_scope else None
             )
        ):
            lines.append('%-15s: %s' % (header_name, header_value))
        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def log(self, msg):
        if _SHOULD_LOG_SCOPE:
            print(msg)

    def insert(self, symbol):
        # print('Insert: %s' % symbol)
        symbol.scope_level = self.scope_level
        self._symbols[symbol.name] = symbol

    def lookup(self, name, current_scope_only=False):
        # print('Lookup: %s. (Scope name: %s)' % (name, self.scope_name))
        symbol = self._symbols.get(name)
        if symbol is not None:
            return symbol
        if current_scope_only:
            return None
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)


class SemanticAnalyser(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.current_scope = ScopedSymbolTable('init', scope_level=0)

    def run(self):
        return self.visit(self.tree)
    
    def log(self, msg):
        if _SHOULD_LOG_SCOPE:
            print(msg)

    def error(self, error_code, token):
        raise SemanticError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )

    def visit_BlockNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_ProgramNode(self, node):
        self.log('ENTER scope: global')
        scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = scope

        for decl in node.declarations:
            self.visit(decl)
        self.current_scope = self.current_scope.enclosing_scope
        self.log('LEAVE scope: global')

    def visit_BinOpNode(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_FactorNode(self, node):
        pass

    def visit_UnaryOpNode(self, node):
        self.visit(node.expr)

    def visit_NoOpNode(self, node):
        pass

    def visit_VarDeclarationNode(self, node):
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)

        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        if  self.current_scope.lookup(var_name, current_scope_only=True) is not None:
            self.error(
                error_code=ErrorCode.DUPLICATE_ID,
                token=node.var_node.token,
            )

        self.current_scope.insert(var_symbol)

    def visit_AssignNode(self, node):
        var_name = node.left.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.token)
        self.visit(node.right)

    def visit_VarNode(self, node):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.token)

    def visit_FunctionDeclarationNode(self, node):
        fun_name = node.fun_name
        fun_symbol = FunctionSymbol(fun_name)
        self.current_scope.insert(fun_symbol)

        self.log(f'ENTER scope: {fun_name}')
        # Scope for parameters and local variables
        function_scope = ScopedSymbolTable(
            scope_name=fun_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = function_scope

        # Insert parameters into the function scope
        for param in node.formal_params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            fun_symbol.formal_params.append(var_symbol)

        self.visit(node.block_node)

        self.log(function_scope)

        self.current_scope = self.current_scope.enclosing_scope
        self.log(f'LEAVE scope: {fun_name}')

        # accessed by the interpreter when executing function call
        fun_symbol.block_ast = node.block_node
        
    def visit_FunctionCallNode(self, node):
        function = self.current_scope.lookup(node.fun_name)
        if len(function.formal_params) != len(node.actual_params):
            raise self.error(ErrorCode.UNEXPECTED_TOKEN, node.token)
        for param_node in node.actual_params:
            self.visit(param_node)
        fun_symbol = self.current_scope.lookup(node.fun_name)
        # accessed by the interpreter when executing function call
        node.fun_symbol = fun_symbol


