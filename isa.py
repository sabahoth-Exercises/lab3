import json
from nodes import *

#  Маска для переполнения чисел
MUSK_NUMBER = 2 ** 32 - 1


class Opcode(str, Enum):
    """Opcode для ISA."""

    OPEN_BRACKET = '('
    CLOSE_BRACKET = ')'
    LD = "ld"
    SAVE = 'save'
    ADD = 'add'
    MOD = "mod"
    JZ = 'jz'
    CMPEQU = "cmpequ"
    HALT = 'halt'
    JMP = "jmp"
    PRINT = 'print'
    PRINTLN = 'println'
    READ = 'read'
    LOOP = "loop"
    JNE = "jne"
    MINUS = "sub"
    CMPLESS = "less",
    CMPMORE = "more",


# Список всех спец символов
correct_words = ["(", ")", "=", "%", "<", ">", "+", "-", "/", "*", "print", "println", "read", "ld"]
"""Cловарь символов, непосредственно транслируемых в машинный код"""
symbol2opcode = {
    Token.PRINT.value: Opcode.PRINT,
    Token.MODULUS.value: Opcode.MOD,
    Token.PLUS.value: Opcode.ADD,
    Token.MINUS.value: Opcode.MINUS,
    "<": Opcode.CMPLESS,
    Token.LARGE: Opcode.CMPMORE,
    "=": Opcode.CMPEQU,
    "ld": Opcode.LD,
    "read": Opcode.READ,
    "println": Opcode.PRINTLN
}


class Term(namedtuple('Term', 'pos symbol')):
    """Описание выражения из исходного текста программы."""
    # сделано через класс, чтобы был docstring


def write_code(filename, instructions):
    """Записать машинный код в файл."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(instructions, indent=4))
        instructions.clear()


def read_code(filename):
    """Прочесть машинный код из файла."""
    with open(filename, encoding="utf-8") as file:
        instructions = json.loads(file.read())

    for instr in instructions:
        # Конвертация строки в Opcode
        instr['opcode'] = Opcode(instr['opcode']).value
    return instructions
