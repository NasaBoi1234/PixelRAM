from asm2 import Prog, of, pg


# Quantized from the supplied audio: low pulse, rising response, high accents.
MOTIF = [
    (33, 4), (33, 4), (0, 2), (43, 2),
    (33, 4), (33, 4), (0, 2), (43, 2),
    (33, 4), (33, 4), (72, 2), (43, 2),
    (33, 4), (33, 4), (0, 2), (72, 2),
    (33, 4), (43, 2), (33, 4), (43, 2),
    (33, 4), (33, 4), (72, 2), (43, 2),
    (33, 4), (33, 4), (0, 2), (72, 2),
    (33, 8), (43, 4), (33, 8), (72, 2),
]


def wait_frames(program, frames):
    program.load('B', frames)
    program.label(f'wait_{len(program.items)}')
    program.ins('WAIT')
    program.ins('SUBV', 'B', 1)
    program.load('C', 0)
    program.ins('SKEQ', 'B', 'C')
    program.ins('JMP', pg(f'wait_{len(program.items) - 4}'),
                of(f'wait_{len(program.items) - 4}'))


def build_program():
    program = Prog()
    program.label('song')
    for note, frames in MOTIF:
        program.ins('SOUND', note, 2 if note else 1)
        wait_frames(program, frames)
    program.ins('JMP', pg('song'), of('song'))
    return program.link()


def write_memory_file(code, path='motif_player_memory.txt'):
    memory = [0] * 8192
    memory[4096:4096 + len(code)] = code
    with open(path, 'w') as output:
        output.write('\n'.join(map(str, memory)))
        output.write('\n')


if __name__ == '__main__':
    code = build_program()
    print(bytes(code).hex())
    write_memory_file(code)
