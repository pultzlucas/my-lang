from enum import Enum

class TokenType(Enum):
    # single-character token types
    COLON = ':'
    COMMA = ','
    DOT = '.'
    ASSIGN = '='
    SEMICOLON = ';'
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    EXPONENT = '**'
    MOD = '%'
    LPAREN = '('
    RPAREN = ')'
    NOT = '!'
    GT = '>'
    LT = '<'
    # Misc
    EQ = '=='
    FLOORDIV = '//'
    EQ_LT = '<='
    EQ_GT = '>='
    NOT_EQ = '!='
    # block of reserved words
    PROGRAM = 'PROGRAM'
    INT = 'INT'
    FLOAT = 'FLOAT'
    FUN = 'FUN'
    LET = 'LET'
    AND = 'AND'
    OR = 'OR'
    NON = 'NON'
    DO = 'DO'
    END = 'END'
    #types
    INTEGER_CONST = 'INTEGER_CONST'
    REAL_CONST = 'REAL_CONST'
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    ID = 'ID'
    EOF = 'EOF'

    