from math import sin, tau

from asm2 import Prog, of, pg


def build_program():
    program = Prog()

    # A and B are the pixel coordinates. D is the animation phase.
    program.load('A', 0)
    program.load('B', 0)
    program.load('D', 0)

    program.label('row_loop')
    program.load('A', 0)

    program.label('pixel_loop')
    program.ins('CALL', pg('shade'), of('shade'))
    program.ins('ADDV', 'A', 1)
    program.load('C', 64)
    program.ins('SKEQ', 'A', 'C')
    program.ins('JMP', pg('pixel_loop'), of('pixel_loop'))

    program.ins('ADDV', 'B', 1)
    program.load('C', 64)
    program.ins('SKEQ', 'B', 'C')
    program.ins('JMP', pg('row_loop'), of('row_loop'))

    program.ins('ADDV', 'D', 1)
    program.load('B', 0)
    program.ins('WAIT')
    program.ins('JMP', pg('row_loop'), of('row_loop'))

    # The shader samples two waveforms and combines them into animated plasma.
    program.label('shade')
    program.ins('PUSH', 'A')
    program.ins('PUSH', 'B')
    program.ins('PUSH', 'D')

    program.ins('MOVE', 'D', 'A')
    program.ins('MULV', 'D', 3)
    program.ins('LOAD', 'C', pg('wave'))
    program.ins('LDM', 'C')
    program.ins('PUSH', 'C')

    program.ins('MOVE', 'D', 'B')
    program.ins('MULV', 'D', 5)
    program.ins('LOAD', 'C', pg('wave'))
    program.ins('LDM', 'C')
    program.ins('POP', 'A')
    program.ins('XOR', 'C', 'A')
    program.ins('POP', 'D')
    program.ins('ADD', 'C', 'D')
    program.ins('ANDV', 'C', 15)
    program.ins('POP', 'B')
    program.ins('POP', 'A')
    program.ins('SETPX', 'C')
    program.ins('RET')

    program.label('wave')
    code = program.link()
    wave = [round((sin(tau * index / 256) + 1) * 7.5) for index in range(256)]
    return code + wave


def write_memory_file(code, path='demo_memory.txt'):
    memory = [0] * 8192
    memory[4096:4096 + len(code)] = code
    with open(path, 'w') as output:
        output.write('\n'.join(map(str, memory)))
        output.write('\n')


if __name__ == '__main__':
    code = build_program()
    print(bytes(code).hex())
    write_memory_file(code)