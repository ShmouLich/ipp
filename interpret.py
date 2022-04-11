import argparse
import re
import xml.etree.ElementTree as et


# classes
class Argument:
    def __init__(self, arg_type, arg_value):
        self.type = arg_type
        self.value = arg_value


class Instruction:
    def __init__(self, opcode, order_num):
        self.opcode = opcode.upper()
        self.order_num = order_num
        self.arguments = []

    def __lt__(self, other):
        if self.order_num < other.order_num:
            return True
        else:
            return False

    def append_argument(self, argument_type, value):
        self.arguments.append(Argument(argument_type, value))

    def print_self(self):
        print("instruction name:", self.opcode)
        num = 1
        for i in self.arguments:
            print("   arg no.", num, ":", i.type, i.value)
            num = num + 1


class Variable:
    def __init__(self, var_type, var_value):
        self.type = var_type
        self.value = var_value


class Interpret:
    def __init__(self):
        self.local_frames = []          # stack of local frames
        self.temporary_frame = {}
        self.global_frame = {}
        self.instructions = []          # list of instructions

    def print_self(self):
        for instruction in self.instructions:
            print("instruction name:", instruction.opcode, "position:", instruction.order_num)
            num = 1
            for i in instruction.arguments:
                print("   arg no.", num, ":", i.type, i.value)
                num = num + 1


def move_to_variable(src, dst):
    if not (dst in program.global_frame or any(dst in lf for lf in program.local_frames) or dst in program.temporary_frame):
        # undefined variable
        exit(22)


def create_frame():
    global temporary_frame
    temporary_frame = {}


def push_frame():
    pass


def pop_frame():
    pass


def define_variable(var: Variable):
    pass


def call_function(name):
    pass


def return_from_function():
    pass


def push(var: Variable):
    pass


def pop(var: Variable):
    pass


def addition(dst: Variable, var1: Variable, var2: Variable):
    pass


def subtraction(dst: Variable, var1: Variable, var2: Variable):
    pass


def multiplication(dst: Variable, var1: Variable, var2: Variable):
    pass


def division(dst: Variable, var1: Variable, var2: Variable):
    pass


def less_than(dst: Variable, var1: Variable, var2: Variable):
    pass


def greater_than(dst: Variable, var1: Variable, var2: Variable):
    pass


def equals(dst: Variable, var1: Variable, var2: Variable):
    pass


def logical_and(dst: Variable, var1: Variable, var2: Variable):
    pass


def logical_or(dst: Variable, var1: Variable, var2: Variable):
    pass


def logical_not(dst: Variable, var: Variable):
    pass


def integer_to_char(dst: Variable, char:Variable):
    pass


def string_to_int(dst: Variable, string: Variable, position: Variable):
    pass


def read_input(dst: Variable, var_type):
    pass


def write_output(string: Variable):
    pass


def concatenate(dst: Variable, first_string: Variable, second_string: Variable):
    pass


def string_length(dst: Variable, string: Variable):
    pass


def get_character(dst: Variable, var1: Variable, var2: Variable):
    pass


def set_character(dst: Variable, var1: Variable, var2: Variable):
    pass


def get_type(dst: Variable, queried_symbol):
    pass


def label(name):
    pass


def jump(name):
    pass


def jump_if_equal(name, var1: Variable, var2: Variable):
    pass


def jump_if_not_equal(name, var1: Variable, var2: Variable):
    pass


def exit_program(error_code):
    pass


def debug_print(var: Variable):
    pass


def state_print():
    pass


def interpret(command: Instruction):
    if command.opcode == "MOVE":
        move_to_variable(command.arguments[0], command.arguments[1])

    elif command.opcode == "CREATEFRAME":
        create_frame()

    elif command.opcode == "PUSHFRAME":
        push_frame()

    elif command.opcode == "POPFRAME":
        pop_frame()

    elif command.opcode == "DEFVAR":
        define_variable(command.arguments[0])

    elif command.opcode == "CALL":
        call_function(command.arguments[0])

    elif command.opcode == "RETURN":
        return_from_function()

    elif command.opcode == "PUSHS":
        push(command.arguments[0])

    elif command.opcode == "POPS":
        pop(command.arguments[0])

    elif command.opcode == "ADD":
        addition(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "SUB":
        subtraction(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "MUL":
        multiplication(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "IDIV":
        division(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "LT":
        less_than(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "GT":
        greater_than(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "EQ":
        equals(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "AND":
        logical_and(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "OR":
        logical_or(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "NOT":
        logical_not(command.arguments[0], command.arguments[1])

    elif command.opcode == "INT2CHAR":
        integer_to_char(command.arguments[0], command.arguments[1])

    elif command.opcode == "STRI2INT":
        string_to_int(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "READ":
        read_input(command.arguments[0], command.arguments[1])

    elif command.opcode == "WRITE":
        write_output(command.arguments[0])

    elif command.opcode == "CONCAT":
        concatenate(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "STRLEN":
        string_length(command.arguments[0], command.arguments[1])

    elif command.opcode == "GETCHAR":
        get_character(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "SETCHAR":
        set_character(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "TYPE":
        get_type(command.arguments[0], command.arguments[1])

    elif command.opcode == "LABEL":
        label(command.arguments[0])

    elif command.opcode == "JUMP":
        jump(command.arguments[0])

    elif command.opcode == "JUMPIFEQ":
        jump_if_equal(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "JUMPIFNEQ":
        jump_if_not_equal(command.arguments[0], command.arguments[1], command.arguments[2])

    elif command.opcode == "EXIT":
        exit_program(command.arguments[0])

    elif command.opcode == "DPRINT":
        debug_print(command.arguments[0])

    elif command.opcode == "BREAK":
        state_print()

    else:
        # unknown instruction
        exit(22)


# argument parsing
helpString = "interprets xml representation of IPPcode22\n" \
             "usage: interpret.py\n" \
             "options:\n" \
             "--source=file file with xml representation of sourcecode\n" \
             "--input=file  file with inputs for sourcecode"

parser = argparse.ArgumentParser()
parser.add_argument('--source', metavar="FILE", type=str)
parser.add_argument('--input', metavar="FILE", type=str)
args = parser.parse_args()

file = open(args.source, 'r')

tree = et.parse(args.source)
root = tree.getroot()

# check xml

if root.tag != "program":
    print("error 22\n")
    exit(22)

for child in root:
    if child.tag != "instruction":
        print("error 22\n")
        exit(22)

    attributes = list(child.attrib.keys())
    if not ("order" in attributes) or not ("opcode" in attributes):
        exit(22)

    for sub_element in child:
        if not (re.match(r"arg[123]", sub_element.tag)):
            exit(22)

program = Interpret()

for child in root:
    current_instruction = Instruction(child.attrib["opcode"], child.attrib["order"])

    for args in child:
        current_instruction.append_argument(args.attrib["type"], args.text)

    program.instructions.insert(int(current_instruction.order_num), current_instruction)

program.instructions.sort()
# program.print_self()

for inst in program.instructions:
    interpret(inst)
