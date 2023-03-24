from nodes import *
from tokens import *
from lexer import Lexer

___all__ = ["Parser"]

stack = []


class Parser:
    def __init__(self, lex):
        self.next_token = None
        self.lex = lex
        self.program = []
        self.curr_token = None
        self.update()
        self.update()
        self.memory = {}
        self.instructions = []
        self.variable_to_be_assigned = -1
        self.prev_token = None

    def update(self):
        self.prev_token = self.curr_token
        self.curr_token = self.next_token
        self.next_token = next(self.lex)

    def is_next(self, t):
        if self.next_token != t:
            raise AssertionError(f"expected {t} but got {self.next_token.name}")
        self.update()

    def __iter__(self):
        return self

    def __next__(self) -> Statement:
        ''' This is the generator that need to be called to get the statement.'''
        while self.curr_token.name != EOF:
            if statement := self.parse_statement():
                return statement
        else:
            return EOF

    def parse_statement(self) -> Statement:
        if self.curr_token == ILLEGAL:
            raise SyntaxError(f"invalid input: {self.curr_token.value}")
        if expression := self.parse_let_statement():
            return expression
        elif expression := self.print_statememt():
            return expression
        elif expression := self.line_statememt():
            return expression
        elif expression := self.read_statememt():
            return expression
        elif expression := self.parse_assign_statement():
            return expression
        elif expression := self.parse_if_expression():
            return expression
        elif expression := self.parse_while_expression():
            return expression
        if expression != None:
            return expression
        else:
            expression = self.parse_expression(Priority.LOWEST)
            if self.next_token == Token.SEMICOLON:
                self.update()
                self.update()
            return expression

    def print_statememt(self) -> Statement:
        if self.curr_token == Token.PRINT:
            state = self.curr_token.value
            self.is_next(Token.LPAREN)
            self.update()
            value = self.parse_expression(Priority.LOWEST)
            self.instructions.append(
                {'opcode': "print", 'arg': [list(self.memory.keys()).index(self.curr_token.value)]})
            self.is_next(Token.RPAREN)
            self.is_next(Token.SEMICOLON)
            self.update()
            return PrintStatement(state, value)

    def line_statememt(self) -> Statement:
        if self.curr_token == Token.LINE:
            state = self.curr_token.value
            self.is_next(Token.LPAREN)
            self.update()
            value = self.parse_expression(Priority.LOWEST)
            self.instructions.append(
                {'opcode': "println", 'arg': [list(self.memory.keys()).index(self.curr_token.value)]})
            self.is_next(Token.RPAREN)
            self.is_next(Token.SEMICOLON)
            self.update()
            return LineStatement(state, value)

    def read_statememt(self) -> Statement:
        if self.curr_token == Token.READ:
            state = self.curr_token.value
            self.is_next(Token.LPAREN)
            self.update()
            value = self.parse_expression(Priority.LOWEST)
            self.instructions.append(
                {'opcode': "read", 'arg': [list(self.memory.keys()).index(self.curr_token.value)]})
            self.is_next(Token.RPAREN)
            self.is_next(Token.SEMICOLON)
            self.update()
            return ReadStatement(state, value)

    def parse_let_statement(self) -> Statement:
        if self.curr_token == Token.LET:
            self.is_next(Token.ID)
            variable = self.curr_token.value
            self.is_next(Token.ASSIGN)  # =
            self.update()
            value = self.parse_expression(Priority.LOWEST)
            self.is_next(Token.SEMICOLON)
            self.update()
            self.memory[variable] = value
            arg = list(self.memory.keys()).index(variable)
            instr = ({'opcode': "ld", 'arg': [arg, str(value)]})
            self.instructions.append(instr)
            return LetStatement(variable, value)

    def parse_assign_statement(self) -> Statement:
        if self.curr_token == Token.ID:
            variable = self.curr_token.value
            self.is_next(Token.ASSIGN)  # =
            self.update()
            self.variable_to_be_assigned = variable
            value = self.parse_expression(Priority.LOWEST)
            self.is_next(Token.SEMICOLON)
            self.update()
            return AssignStatement(variable, value)

    def parse_block_Statements(self) -> Statement:
        self.is_next(Token.LBRACE)
        self.update()
        block = []
        while self.curr_token != Token.RBRACE:
            stmt = self.parse_statement()
            block.append(stmt)
        else:
            self.update()
        return BlockStatement(block)

    def parse_expression(self, precedence: Priority) -> Expression:
        expression = self.parse_datatypes() or self.parse_unary()
        if expression == None:
            raise SyntaxError(f"operand '{self.curr_token.value}' not defined")

        infix_list = [
            # athemetic oeprator
            Token.PLUS, Token.MINUS,
            Token.DIVIDE, Token.TIMES,
            Token.MODULUS, Token.POWER,
            # comparision operator
            Token.EQUAL, Token.LARGE,
            Token.LARGEEQ, Token.SMALL,
            Token.SMALLEQ, Token.NOTEQ,
            # logical operator
            Token.AND, Token.OR
        ]
        while self.next_token != Token.SEMICOLON and \
                precedence.value <= get_precedence(self.next_token).value:
            # infix function needs to call infix list
            if self.next_token.name in infix_list:
                self.update()
                if self.curr_token.name == Token.PLUS:
                    arg = list(self.memory.keys()).index(self.next_token.value)
                    arg1 = list(self.memory.keys()).index(self.prev_token.value)
                    instr = ({'opcode': "add", 'arg': [arg, arg1]})
                    self.instructions.append(instr)
                    arg2 = list(self.memory.keys()).index(self.variable_to_be_assigned)
                    instr = ({'opcode': "save", 'arg': [arg2]})
                    self.instructions.append(instr)
                if self.curr_token.name == Token.MODULUS:
                    arg = list(self.memory.keys()).index(self.next_token.value)
                    instr = ({'opcode': "mod", 'arg': [arg]})
                    self.instructions.append(instr)
                    arg2 = list(self.memory.keys()).index(self.variable_to_be_assigned)
                    instr = ({'opcode': "save", 'arg': [arg2]})
                    self.instructions.append(instr)
                if self.curr_token.name == Token.SMALL:
                    arg0 = list(self.memory.keys()).index(self.next_token.value) + 1
                    instr = ({'opcode': "loop", 'arg': [arg0]})
                    self.instructions.append(instr)
                    arg = list(self.memory.keys()).index(self.next_token.value)
                    arg1 = list(self.memory.keys()).index(self.prev_token.value)
                    instr = ({'opcode': "less", 'arg': [arg1, arg]})
                    self.instructions.append(instr)
                if self.curr_token.name == Token.LARGE:
                    arg0 = list(self.memory.keys()).index(self.next_token.value) + 1
                    instr = ({'opcode': "loop", 'arg': [arg0]})
                    self.instructions.append(instr)
                    arg = list(self.memory.keys()).index(self.next_token.value)
                    arg1 = list(self.memory.keys()).index(self.prev_token.value)
                    instr = ({'opcode': "more", 'arg': [arg1, arg]})
                    self.instructions.append(instr)
                expression = self.parse_infix_expression(expression)
            else:
                break
        return expression

    def parse_infix_expression(self, left: Expression) -> Expression:
        operator = self.curr_token.value
        precedence = get_precedence(self.curr_token)
        self.update()
        right = self.parse_expression(precedence)
        return InfixExpression(left, operator, right)

    def parse_if_expression(self) -> Expression:
        if self.curr_token == Token.IF:
            self.is_next(Token.LPAREN)
            self.update()
            condition = self.parse_expression(Priority.LOWEST)
            self.is_next(Token.RPAREN)
            true_stmt = self.parse_block_Statements()
            false_stmt = None
            return IfStatement(condition, true_stmt, false_stmt)

    def parse_while_expression(self) -> Expression:
        if self.curr_token == Token.WHILE:
            self.is_next(Token.LPAREN)
            self.update()
            condition = self.parse_expression(Priority.LOWEST)
            self.is_next(Token.RPAREN)
            block = self.parse_block_Statements()
            instr = ({'opcode': "jne", 'arg': None})
            self.instructions.append(instr)
            return WhileStatement(condition, block)

    def parse_datatypes(self) -> Expression:
        datatypes = [
            Token.INT.name,
            Token.FLOAT.name,
            Token.TRUE.name,
            Token.FALSE.name,
            Token.STRING.name,
        ]
        if self.curr_token.name in datatypes:
            return Literal(self.curr_token.name, self.curr_token.value)
        elif self.curr_token == Token.ID:
            return Identifier(self.curr_token.value)

    def parse_unary(self):
        if self.curr_token.name in [Token.NOT, Token.MINUS]:
            operator = self.curr_token.value
            precedence = get_precedence(self.curr_token)
            self.update()
            right = self.parse_expression(Priority.HIGHER)
            return PrefixExpression(operator, right)
        elif self.curr_token.name == Token.LPAREN:
            self.update()
            expression = self.parse_expression(Priority.LOWEST)
            self.is_next(Token.RPAREN)
            return expression


def main(args):
    from isa import write_code

    assert len(args) == 2, \
        "Wrong arguments: parser.py <input_file> <target_file>"
    source, target = args

    with open(source, "rt", encoding="utf-8") as f:
        source = f.read()

    parser = Parser(Lexer(source))
    for i in parser:
        if i == EOF:
            instr = ({'opcode': "halt"})
            parser.instructions.append(instr)
            break
    print("source LoC:", len(source.split()), "code instr:", len(parser.instructions))
    write_code(target, parser.instructions)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])