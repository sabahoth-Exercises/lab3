"""Модель процессора, позволяющая выполнить странслированные программы на языке Brainfuck.
"""
import logging

from isa import *
from math import copysign
from translator import *

count = 0
char_mode = False


class DataPath:
    def __init__(self, data_memory_size, input_buffer):
        assert data_memory_size > 0, "Data_memory size should be non-zero"
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * data_memory_size
        self.data_address = 0
        self.acc = 0
        self.dr = 0
        self.input_buffer = input_buffer
        self.output_buffer = []
        self.max_data = 2147483647
        self.min_data = -2147483648
        self.result_address = 8

    def latch_data_addr(self, new_addr):
        """ Данная функция позволяет загружать новые значения (адреса) в регистр адреса """
        assert 0 <= new_addr < self.data_memory_size, \
            f"out of memory: {format(self.data_address)}"

        self.data_address = new_addr

    def latch_dr(self, sel, arg, op_type):
        """ Защелкнуть DR = прочитать данные из памяти
            sel = 1 Считать данные из декодера инструкций
            sel = 2 Считать данные из текущего адреса памяти
            sel = 3 Защелкнуть данные с АЛУ"""
        if sel == 1:
            self.dr = arg
        elif sel == 2:
            self.dr = self.data_memory[self.data_address]
        else:
            self.dr = self.alu(op_type)

    def latch_acc(self, op_type):
        """Защелкнуть новое значение AC, новое значение приходит из ALU
            в зависимости от входного сигнала выбирается операция на ALU"""
        self.acc = self.alu(op_type)

    def alu(self, op_type):
        global flag
        cur_value = 0
        match op_type:
            case "add":
                cur_value = self.data_memory[self.data_address] + self.dr
            case "mod":
                cur_value = self.data_memory[self.data_address] % self.dr
            case "sub":
                cur_value = self.data_memory[self.data_address] - self.dr
            case "less":
                cur_value = self.dr < self.data_memory[self.data_address]
                flag = (self.dr < self.data_memory[self.data_address])
            case "more":
                cur_value = self.dr > self.data_memory[self.data_address]
                flag = (self.dr > self.data_memory[self.data_address])
            case Opcode.LD:
                cur_value = self.dr

        # Проверка на переполнение
        if abs(cur_value) > self.max_data:
            cur_value = copysign(abs(cur_value) & MUSK_NUMBER, cur_value)

        return cur_value

    def output(self, data_type):
        """ Вывод:
        Если data_type True : вывод числа
        Если data_type False : вывод символа производится через ASCII-символы по спецификации
        - вывод осуществляется просто в буфер. """

        if data_type:
            logging.debug('output: %s', repr(str(self.result_address)))
            self.output_buffer.append(str(self.data_memory[self.data_address]))
        else:
            symbol = chr(self.data_memory[self.data_address])

            logging.debug('output: %s << %s', repr(
                ''.join(self.output_buffer)), repr(symbol))
            self.output_buffer.append(symbol)

    def wr(self, sel):
        """wr (от WRite), сохранить в память."""
        if sel:
            if len(self.input_buffer) == 0:
                raise EOFError()
            symbol = self.input_buffer.pop(0)
            symbol_code = ord(symbol)
            assert -128 <= symbol_code <= 127, \
                "input token is out of bound: {}".format(symbol_code)
            self.data_memory[self.data_address] = symbol_code
            logging.debug('input: %s', repr(symbol))
            assert self.min_data <= self.data_memory[self.data_address] <= self.max_data, \
                f"acc value is out of bound: {self.data_memory[self.data_address]}"

        else:
            self.data_memory[self.data_address] = self.acc
            if isinstance(self.acc, int):
                assert self.min_data <= self.data_memory[self.data_address] <= self.max_data, \
                    f"acc value is out of bound: {self.data_memory[self.data_address]}"

    def zero(self):
        """Флаг"""
        return self.acc == 0

    def neg(self):
        """ Флаг нужен для проверки на знак """
        return self.acc < 0

    def flag_status(self):
        return flag


class ControlUnit:
    """Блок управления процессора. Выполняет декодирование инструкций и
    управляет состоянием процессора, включая обработку данных (DataPath).

    Считается, что любая инструкция может быть в одно слово. Следовательно,
    индекс памяти команд эквивалентен номеру инструкции."""

    def __init__(self, program, data_path):
        self.program = program
        self.data_path = data_path
        self.program_counter = 0
        self._tick = 0
        self.current_arg = 0
        self.loop_stack = []
        self.result = 0

    def tick(self):
        """Счётчик тактов процессора. Вызывается при переходе на следующий такт."""
        self._tick += 1

    def get_current_arg(self):
        return self.current_arg

    def current_tick(self):
        return self._tick

    def latch_program_counter(self, sel_next):
        self.tick()
        if sel_next:
            self.program_counter += 1
        else:
            instr = self.program[self.program_counter]
            assert 'arg' in instr, "internal error"
            self.program_counter = instr["arg"][0]

    def decode_and_execute_instruction(self):
        instr = self.program[self.program_counter]
        opcode = instr["opcode"]

        match opcode:
            case Opcode.HALT:
                raise StopIteration()
            case Opcode.LD | Opcode.SAVE:
                self.execute_ld(instr, opcode)
            case Opcode.SAVE:
                self.execute_save(instr)
            case Opcode.MOD:
                self.execute_mod(instr, opcode)
            case Opcode.ADD | Opcode.MINUS | Opcode.CMPLESS | Opcode.CMPMORE:
                self.execute_alu(instr, opcode)
            case Opcode.JNE:
                self.execute_jne()
            case Opcode.LOOP:
                self.execute_loop(instr)
            case Opcode.PRINT | Opcode.PRINTLN:
                self.execute_print(instr, opcode)
            case Opcode.READ:
                self.execute_read(instr)

    def execute_mod(self, instr, opcode):
        self.data_path.latch_data_addr(instr["arg"][0])
        self.data_path.latch_dr(1, instr["arg"][1], None)
        self.tick()

        self.data_path.latch_acc(opcode)
        self.tick()
        self.latch_program_counter(sel_next=True)

    def execute_ld(self, instr, opcode):
        global char_mode
        self.data_path.latch_data_addr(instr["arg"][0])
        if opcode == Opcode.LD:
            if count < 3:
                char_mode = True
            if isinstance(instr["arg"][1], str):
                if char_mode:
                    self.data_path.latch_dr(1, ord(instr["arg"][1]), None)
                else:
                    self.data_path.latch_dr(1, int(instr["arg"][1]), None)
            else:
                self.data_path.latch_dr(1, instr["arg"][1], None)
            self.tick()
            self.data_path.latch_acc(opcode)
        if instr["arg"][0] == 2:
            self.data_path.result_address = self.data_path.data_memory[self.data_path.data_address]
        self.tick()
        self.data_path.wr(False)
        self.tick()
        self.latch_program_counter(sel_next=True)

    def execute_save(self, instr):
        self.data_path.latch_data_addr(instr["arg"][1])
        self.tick()

        self.data_path.write(False)
        self.tick()
        self.latch_program_counter(sel_next=True)

    def execute_alu(self, instr, opcode):
        self.data_path.latch_data_addr(instr["arg"][0])
        self.tick()

        self.data_path.latch_dr(2, None, None)
        self.tick()
        self.data_path.latch_data_addr(instr["arg"][1])
        self.tick()
        arg_counter = 2
        while arg_counter < len(instr["arg"]):
            self.data_path.latch_dr(3, None, opcode)
            self.tick()
            self.data_path.latch_data_addr(instr["arg"][arg_counter])
            arg_counter += 1
            self.tick()
        self.data_path.latch_acc(opcode)
        self.tick()
        self.latch_program_counter(sel_next=True)

    def execute_loop(self, instr):
        self.loop_stack.append(instr["arg"][0])
        self.tick()
        self.latch_program_counter(sel_next=True)

    def execute_jne(self):
        var = self.data_path.flag_status()
        last_loop_number = self.loop_stack[len(self.loop_stack) - 1]
        if var:
            self.program_counter = last_loop_number
        else:
            self.loop_stack.pop()
        self.tick()
        self.latch_program_counter(sel_next=True)

    def execute_print(self, instr, opcode):
        self.data_path.latch_data_addr(instr["arg"][0])
        self.tick()
        if opcode == Opcode.PRINT.value:
            self.data_path.output(True)
        else:
            self.data_path.output(False)
        self.tick()
        self.latch_program_counter(sel_next=True)

    def execute_read(self, instr):
        self.data_path.latch_data_addr(instr["arg"][0])
        self.tick()
        self.data_path.wr(True)
        self.tick()
        self.latch_program_counter(sel_next=True)

    def __repr__(self):
        state = "{{TICK: {}, PC: {}, ADDR: {}, OUT: {}, AC: {}, DR: {}}}".format(
            self._tick,
            self.program_counter,
            self.data_path.data_address,
            self.data_path.data_memory[self.data_path.data_address],
            self.data_path.acc,
            self.data_path.dr,
        )

        instr = self.program[self.program_counter]
        opcode = instr["opcode"]
        arg = instr.get("arg", "")
        action = "{} {}".format(opcode, arg)

        return "{} {}".format(state, action)


def simulation(instructions, input_tokens, data_memory_size, limit):
    data_path = DataPath(data_memory_size, input_tokens)
    control_unit = ControlUnit(instructions, data_path)
    instr_counter = 0

    logging.debug('%s', control_unit)
    try:
        while True:
            assert limit > instr_counter, "too long execution, increase limit!"
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug('%s', control_unit)
    except EOFError:
        logging.warning('Input buffer is empty!')
    except StopIteration:
        pass
    if char_mode:
        logging.info('output_buffer: %s', repr(''.join(data_path.output_buffer)))
        return ''.join(data_path.output_buffer), instr_counter, control_unit.current_tick()
    else:
        logging.info('output_buffer: %s', str(data_path.result_address))
        return str(data_path.result_address), instr_counter, control_unit.current_tick()


def main(args):
    assert len(args) == 2, "Wrong arguments: machine.py <code_file> <input_file>"
    code_file, input_file = args
    global count
    instructions = read_code(code_file)
    for vl in instructions:
        a = vl["opcode"]
        if a == "ld":
            count += 1

    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_token = []
        for char in input_text:
            input_token.append(char)

    output, instr_counter, ticks = simulation(instructions, input_tokens=input_token, data_memory_size=100,
                                              limit=100000)

    print(''.join(output))
    print("instr_counter: ", instr_counter, "ticks:", ticks)


if __name__ == '__main__':
    import sys

    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
