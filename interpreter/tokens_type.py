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
    FUN = 'FUN'
    # MAIN = 'MAIN'
    INT = 'INT'
    FLOAT = 'FLOAT'
    LET = 'LET'
    IF = 'IF'
    AND = 'AND'
    OR = 'OR'
    NON = 'NON'
    DO = 'DO'
    END = 'END'
    #types
    INTEGER_VALUE = 'INTEGER_VALUE'
    REAL_VALUE = 'REAL_VALUE'
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    ID = 'ID'
    EOF = 'EOF'

    