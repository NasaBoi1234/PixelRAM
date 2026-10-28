from asm2 import Prog, of, pg

STATE_PAGE = 31


def set_pixel(program, x, y, color):
    program.load('A', x)
    program.load('B', y)
    program.load('C', color)
    program.ins('SETPX', 'C')


def store(program, offset, register):
    program.load('C', STATE_PAGE)
    program.load('D', offset)
    program.ins('STM', register)


def load_state(program, offset, register):
    program.load('C', STATE_PAGE)
    program.load('D', offset)
    program.ins('LDM', register)
    program.forget()


def build_program():
    program = Prog()

    program.load('C', 0)
    program.ins('FILL', 'C')

    stars = [
        (7, 7), (15, 13), (24, 5), (33, 10), (42, 16), (53, 8),
        (4, 25), (13, 30), (22, 21), (31, 27), (40, 23), (49, 32),
        (59, 19), (9, 42), (19, 37), (29, 46), (38, 40), (48, 51),
        (57, 44), (3, 55),
    ]
    for x, y in stars:
        set_pixel(program, x, y, 12)
        set_pixel(program, x + 1, y, 13)

    # Fly the starfield sideways before starting the main interactive scene.
    program.load('B', 8)
    program.label('fly_in')
    program.load('A', 3)
    program.ins('SCROLL', 'A')
    program.ins('SOUND', 48, 2)
    program.ins('WAIT')
    program.load('C', 0)
    program.ins('SUBV', 'B', 1)
    program.ins('SKEQ', 'B', 'C')
    program.ins('JMP', pg('fly_in'), of('fly_in'))

    # A 4x4 ship tile at (0, 0), plus a blank 4x4 tile at (8, 0).
    for x, y, color in [
        (1, 0, 10), (2, 0, 10), (3, 0, 10), (2, 1, 12),
        (0, 2, 9), (1, 2, 9), (2, 2, 9), (3, 2, 9),
        (1, 3, 4), (2, 3, 4),
    ]:
        set_pixel(program, x, y, color)

    for x, y in [(8, 0), (9, 0), (10, 0), (11, 0),
                 (8, 1), (9, 1), (10, 1), (11, 1),
                 (8, 2), (9, 2), (10, 2), (11, 2),
                 (8, 3), (9, 3), (10, 3), (11, 3)]:
        set_pixel(program, x, y, 0)

    # x, y, dx, frame, and a sampled background color live in RAM.
    for offset, value in [(0, 24), (1, 28), (2, 1), (3, 0), (4, 0)]:
        program.load('A', value)
        store(program, offset, 'A')

    program.label('main')
    load_state(program, 0, 'A')
    load_state(program, 1, 'B')
    program.ins('GETPX', 'C')
    program.ins('MOVE', 'A', 'C')
    store(program, 4, 'A')

    # Erase the previous ship, then update its position and direction.
    load_state(program, 0, 'C')
    load_state(program, 1, 'D')
    program.load('A', 8)
    program.load('B', 0)
    program.ins('COPYBLOCK', 4, 4)

    load_state(program, 0, 'A')
    load_state(program, 2, 'B')
    program.ins('ADD', 'A', 'B')
    program.ins('ANDV', 'A', 63)
    store(program, 0, 'A')

    program.load('C', 60)
    program.ins('SKLT', 'A', 'C')
    program.ins('JMP', pg('reverse_right'), of('reverse_right'))
    program.ins('JMP', pg('check_left'), of('check_left'))

    program.label('reverse_right')
    program.load('A', 255)
    store(program, 2, 'A')
    program.ins('JMP', pg('check_left'), of('check_left'))

    program.label('check_left')
    load_state(program, 0, 'A')
    program.load('C', 4)
    program.ins('SKLT', 'A', 'C')
    program.ins('JMP', pg('draw_ship'), of('draw_ship'))
    program.load('A', 1)
    store(program, 2, 'A')

    program.label('draw_ship')
    load_state(program, 0, 'C')
    load_state(program, 1, 'D')
    program.load('A', 0)
    program.load('B', 0)
    program.ins('COPYBLOCK', 4, 4)

    load_state(program, 3, 'A')
    program.ins('ADDV', 'A', 1)
    program.ins('XORV', 'A', 3)
    program.ins('MULV', 'A', 3)
    program.ins('ANDV', 'A', 15)
    store(program, 3, 'A')

    program.load('C', 0)
    program.ins('SKNE', 'A', 'C')
    program.ins('SOUND', 72, 3)
    program.load('C', 8)
    program.ins('SKEQ', 'A', 'C')
    program.ins('JMP', pg('continue'), of('continue'))
    program.ins('SOUND', 84, 3)

    program.label('continue')
    load_state(program, 0, 'A')
    load_state(program, 1, 'B')
    load_state(program, 4, 'C')
    program.ins('ADD', 'A', 'C')
    program.ins('SUB', 'A', 'C')
    program.ins('MUL', 'A', 'B')
    program.ins('AND', 'A', 'B')
    program.ins('XOR', 'A', 'B')
    program.ins('WAIT')
    program.ins('JMP', pg('main'), of('main'))

    program.label('unused_halt_guard')
    program.ins('JMP', pg('unused_halt_guard'), of('unused_halt_guard'))
    return program.link()


def write_memory_file(code, path='opcode_showcase_memory.txt'):
    memory = [0] * 8192
    memory[4096:4096 + len(code)] = code
    with open(path, 'w') as output:
        output.write('\n'.join(map(str, memory)))
        output.write('\n')


if __name__ == '__main__':
    code = build_program()
    print(bytes(code).hex())
    write_memory_file(code)
