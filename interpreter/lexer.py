from interpreter.tokens_type import TokenType as Tk
from interpreter.exceptions import LexerError

class Token():
    def __init__(self, type, value, lineno=None, column=None):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.column = column

    def __str__(self):
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column,
        )

    def __repr__(self):
        return self.__str__()

def _build_reserved_keywords():
    tt_list = list(Tk)
    start_index = tt_list.index(Tk.FUN)
    end_index = tt_list.index(Tk.END)
    reserved_keywords = {
        token_type.value: token_type
        for token_type in tt_list[start_index:end_index + 1]
    }
    return reserved_keywords

RESERVED_KEYWORDS = _build_reserved_keywords()

class Lexer():
    def __init__(self, text) -> None:
        self.lineno = 1
        self.column = 1
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.current_token = self.next_token()

    def error(self):
        s = "Lexer error on '{lexeme}' line: {lineno} column: {column}".format(
            lexeme=self.current_char,
            lineno=self.lineno,
            column=self.column,
        )
        raise LexerError(message=s)

    def next_char(self):
        if self.current_char == '\n':
            self.lineno += 1
            self.column = 0

        self.pos += 1
        if not self.pos > len(self.text) - 1:
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None
    
    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def get_number_tk(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.next_char()

        if self.current_char == '.':
            result += self.current_char
            self.next_char()

            while (
                self.current_char is not None and
                self.current_char.isdigit()
            ):
                result += self.current_char
                self.next_char()

            token = Token(Tk.REAL_VALUE, float(result))
        else:
            token = Token(Tk.INTEGER_VALUE, int(result))

        return token

    def skip_spaces(self):
        while self.current_char is not None and self.current_char.isspace():
            self.next_char()

    def _id(self):
        token = Token(type=None, value=None, lineno=self.lineno, column=self.column)
        value = ''
        while self.current_char is not None and self.current_char.isalnum() or self.current_char == '-':
            value += self.current_char
            self.next_char()
        token_type = RESERVED_KEYWORDS.get(value.upper())
        if token_type is None:
            token.type = Tk.ID
            token.value = value
        else:
            # reserved keyword
            token.type = token_type
            token.value = value.upper()
        return token

    def get_string_tk(self):
        self.next_char()
        string = ''
        while self.current_char is not None and self.current_char != "'":
            string += self.current_char
            self.next_char()
        self.next_char()
        return Token(Tk.STRING, str(string))
    
    def skip_comment(self):
        while self.current_char != '}':
            self.next_char()
        self.next_char() 

    def next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_spaces()
                continue

            if self.current_char == "{":
                self.next_char()
                self.skip_comment()
                continue

            if self.current_char == '>' and self.peek() == '=':
                self.next_char()
                return Token(Tk.EQ_GT, '>=')
            
            if self.current_char == '<' == self.peek() == '=':
                self.next_char()
                self.next_char()
                return Token(Tk.EQ_LT, '<=')
            
            if self.current_char == '*' and self.peek() == '*':
                self.next_char()
                self.next_char()
                return Token(Tk.EXPONENT, '**')
            
            if self.current_char == '/' and self.peek() == '/':
                self.next_char()
                self.next_char()
                return Token(Tk.FLOORDIV, '//')
            
            if self.current_char == '=' and self.peek() == '=':
                self.next_char()
                self.next_char()
                return Token(Tk.EQ, '==')
            
            if self.current_char == '!' and self.peek() == '=':
                self.next_char()
                self.next_char()
                return Token(Tk.NOT_EQ, '!=')
            
            if self.current_char.isdigit():
                return self.get_number_tk()
            
            if self.current_char == "'":
                return self.get_string_tk()
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()

            try:
                token_type = Tk(self.current_char)
            except ValueError:
                self.error()
            else:
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    lineno=self.lineno,
                    column=self.column,
                )
                self.next_char()
                return token
            
        return Token(Tk.EOF, None)
        