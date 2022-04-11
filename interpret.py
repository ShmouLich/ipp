import argparse
import re
import xml.etree.ElementTree as et


# classes
class Argument:
    def __init__(self, arg_type, arg_value):
        self.type = arg_type  # var, int, string, nil
        self.value = arg_value  # for type 'var' contains name of variable, for others contains value

    def in_global_frame(self):
        return self.value in program.global_frame

    def in_local_frames(self):
        if len(program.local_frames) == 0:
            return False

        frame = program.local_frames.pop()

        if self.value in frame:
            program.local_frames.append(frame)
            return True

        program.local_frames.append(frame)
        return False

    def in_temporary_frame(self):
        return self.value in program.temporary_frame

    def is_var(self):
        return self.type == "var"

    def print_self(self):
        print("   arg of type", self.type, "with value", self.value)


class Instruction:
    def __init__(self, opcode, order_num):
        self.opcode = opcode.upper()  # instruction name
        self.order_num = order_num  # order of instruction in program
        self.arguments = []  # list of all arguments

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


class Interpret:
    def __init__(self):
        self.local_frames = []  # stack of local frames
        self.temporary_frame = {}
        self.global_frame = {}
        self.instructions = []  # list of instructions
        self.labels = {}
        self.program_counter = 0
        self.calls = []
        self.data_stack = []

    def print_self(self):
        print("current PC:", self.program_counter)

        print("local frames stack:")
        for frame in self.local_frames:
            print(frame)

        print("temporary frames stack:")
        print(self.temporary_frame)

        print("global frames stack:")
        print(self.global_frame)

        print("labels:")
        print(self.labels)

        print("data stack:")
        print(self.data_stack)

        print("all instructions:")
        for instruction in self.instructions:
            print("instruction name:", instruction.opcode, "position:", instruction.order_num)
            num = 1
            for i in instruction.arguments:
                print("   arg no.", num, ":", i.type, i.value)
                num = num + 1


def get_value_from_frame(var: Argument):
    if var.in_global_frame():
        return program.global_frame[var.value]
    elif var.in_temporary_frame():
        return program.temporary_frame[var.value]
    elif var.in_local_frames():
        frame = program.local_frames.pop()
        ret = frame[var.value]
        program.local_frames.append(frame)
        return ret
    else:
        print("no variable of name", var.value, "defined in any frame")
        exit(52)


def get_type_from_frame(var: Argument):
    if var.in_global_frame():
        return program.global_frame[var.value].type
    elif var.in_temporary_frame():
        return program.temporary_frame[var.value].type
    elif var.in_local_frames():
        frame = program.local_frames.pop()
        ret = frame[var.value].type
        program.local_frames.append(frame)
        return ret
    else:
        print("no variable of name", var.value, "defined in any frame")
        exit(52)


def set_value_to_any_frame(name, value):
    dst = Argument("nil", name)
    src = Argument("nil", value)
    move_to_variable(dst, src)


def get_operand(op: Argument):
    if op.is_var():
        return get_value_from_frame(op)
    else:
        return op.value


def save_label(instruction):
    label = instruction.arguments.pop()
    label_name = label.value
    instruction.arguments.append(label)

    program.labels[label_name] = int(instruction.order_num)


# IPPCODE22 functions


def move_to_variable(dst: Argument, src: Argument):
    if dst.in_global_frame():
        program.global_frame[dst.value] = src.value
    elif dst.in_local_frames():
        frame = program.local_frames.pop()
        frame[dst.value] = src.value
        program.local_frames.append(frame)
    elif dst.in_temporary_frame():
        program.temporary_frame[dst.value] = src.value
    else:
        print("no variable of name", dst.value, "defined in any frame")
        exit(52)


def create_frame():
    program.temporary_frame = {}


def push_frame():
    program.local_frames.append(program.temporary_frame)


def pop_frame():
    if len(program.local_frames) == 0:
        exit(55)

    program.temporary_frame = program.local_frames.pop()


def define_variable(var: Argument):
    if not var.is_var():
        exit(52)

    if "GF" in var.value:
        program.global_frame[var.value] = "nil"

    if "LF" in var.value:
        current_frame = program.local_frames.pop()
        current_frame[var.value] = "nil"
        program.local_frames.append(current_frame)

    if "TF" in var.value:
        program.temporary_frame[var.value] = "nil"


def call_function(name):
    if name not in program.labels:
        exit(22)

    program.calls.append(program.program_counter)
    program.program_counter = program.labels[name]


def return_from_function():
    if len(program.calls) == 0:
        exit(56)

    program.program_counter = program.calls.pop()


def push(var: Argument):
    program.data_stack.append(var)


def pop(var: Argument):
    if len(program.data_stack) == 0:
        exit(56)

    popped = program.data_stack.pop()
    var.value = popped.value
    var.type = popped.type


def addition(dst: Argument, var1: Argument, var2: Argument):
    num1 = get_operand(var1)
    num2 = get_operand(var2)

    set_value_to_any_frame(dst.value, int(num1) + int(num2))
    dst.type = "int"


def subtraction(dst: Argument, var1: Argument, var2: Argument):
    num1 = get_operand(var1)
    num2 = get_operand(var2)

    set_value_to_any_frame(dst.value, int(num1) - int(num2))
    dst.type = "int"


def multiplication(dst: Argument, var1: Argument, var2: Argument):
    num1 = get_operand(var1)
    num2 = get_operand(var2)

    set_value_to_any_frame(dst.value, int(num1) * int(num2))
    dst.type = "int"


def division(dst: Argument, var1: Argument, var2: Argument):
    num1 = get_operand(var1)
    num2 = get_operand(var2)

    set_value_to_any_frame(dst.value, int(int(num1) / int(num2)))
    dst.type = "int"


def less_than(dst: Argument, var1: Argument, var2: Argument):
    num1 = get_operand(var1)
    num2 = get_operand(var2)

    set_value_to_any_frame(dst.value, num1 < num2)
    dst.type = "bool"


def greater_than(dst: Argument, var1: Argument, var2: Argument):
    num1 = get_operand(var1)
    num2 = get_operand(var2)

    set_value_to_any_frame(dst.value, num1 > num2)
    dst.type = "bool"


def equals(dst: Argument, var1: Argument, var2: Argument):
    num1 = get_operand(var1)
    num2 = get_operand(var2)

    set_value_to_any_frame(dst.value, num1 == num2)
    dst.type = "bool"


def logical_and(dst: Argument, var1: Argument, var2: Argument):
    num1 = get_operand(var1)
    num2 = get_operand(var2)

    set_value_to_any_frame(dst.value, num1 and num2)
    dst.type = "bool"


def logical_or(dst: Argument, var1: Argument, var2: Argument):
    num1 = get_operand(var1)
    num2 = get_operand(var2)

    set_value_to_any_frame(dst.value, num1 or num2)
    dst.type = "bool"


def logical_not(dst: Argument, var: Argument):
    num1 = get_operand(var)

    set_value_to_any_frame(dst.value, not num1)
    dst.type = "bool"


def integer_to_char(dst: Argument, char: Argument):
    try:
        dst.value = chr(get_operand(char))
        dst.type = "str"
    except ValueError:
        exit(58)


def string_to_int(dst: Argument, string: Argument, position: Argument):
    string_value = get_operand(string)
    offset = get_operand(position)

    try:
        dst.value = ord(string_value[offset])
        dst.type = "int"
    except IndexError:
        exit(58)


def read_input(dst: Argument, var_type):
    user_in = input()

    if var_type == "string":
        user_in = str(user_in)
        dst.type = "string"
    elif var_type == "int":
        user_in = int(user_in)
        dst.type = "int"
    elif var_type == "bool":
        if user_in.upper() == "TRUE":
            user_in = True
        else:
            user_in = False
        dst.type = "bool"
    else:
        user_in = "nil"
        dst.type = "nil"

    dst.value = user_in


def write_output(string: Argument):
    print(get_value_from_frame(string))


def concatenate(dst: Argument, first_string: Argument, second_string: Argument):
    str1 = get_operand(first_string)
    str2 = get_operand(second_string)

    set_value_to_any_frame(dst.value, str(str1) + str(str2))
    dst.type = "str"


def string_length(dst: Argument, string: Argument):
    length = len(get_operand(string))

    set_value_to_any_frame(dst.value, length)
    dst.type = "int"


def get_character(dst: Argument, string: Argument, position: Argument):
    string_value = get_operand(string)
    offset = get_operand(position)

    try:
        dst.value = string_value[offset]
        dst.type = "string"
    except IndexError:
        exit(58)


def set_character(dst: Argument, string: Argument, position: Argument):
    string_value = get_operand(string)
    offset = get_operand(position)

    try:
        dst.value[offset] = string_value
        dst.type = "string"
    except IndexError:
        exit(58)


def get_type(dst: Argument, queried_symbol):
    if queried_symbol.type == "var":
        dst.value = str(get_type_from_frame(queried_symbol))
    else:
        dst.value = queried_symbol.type

    dst.type = "string"


def jump(name):
    if name in program.labels:
        program.program_counter = program.labels[name] - 1


def jump_if_equal(name, var1: Argument, var2: Argument):
    if var1.type == var2.type and var1.value == var2.value:
        jump(name)


def jump_if_not_equal(name, var1: Argument, var2: Argument):
    if not (var1.type == var2.type and var1.value == var2.value):
        jump(name)


def exit_program(error_code):
    if error_code < 0 or error_code > 49:
        exit(57)
    else:
        exit(error_code)


def debug_print(var: Argument):
    print(var.value)


def state_print():
    program.print_self()


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
        pass

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

    if current_instruction.opcode == "LABEL":
        save_label(current_instruction)

program.instructions.sort()

while program.program_counter < len(program.instructions):
    interpret(program.instructions[program.program_counter])
    program.program_counter += 1
