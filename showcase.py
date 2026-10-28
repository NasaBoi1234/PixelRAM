from asm2 import Prog, of, pg


SPRITES = {
    'body': [
        (1, 0), (2, 0), (3, 0), (4, 0), (5, 0),
        (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
        (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4),
        (1, 5), (2, 5), (3, 5), (4, 5), (5, 5),
    ],
    'window': [
        (2, 2), (3, 2), (4, 2),
        (2, 3), (3, 3), (4, 3),
    ],
    'flame_small': [
        (2, 6), (3, 6), (4, 6),
        (2, 7), (3, 7), (4, 7),
    ],
    'flame_big': [
        (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),
        (2, 7), (3, 7), (4, 7),
        (3, 8),
    ],
}


def add_pixel(program, x, y, color):
    program.load('A', x)
    program.load('B', y)
    program.load('C', color)
    program.ins('SETPX', 'C')


def add_sprite(program, name):
    program.label(name)
    program.ins('PUSH', 'A')
    program.ins('PUSH', 'B')
    current_x, current_y = 0, 0
    for x, y in SPRITES[name]:
        if x > current_x:
            program.ins('ADDV', 'A', x - current_x)
        elif x < current_x:
            program.ins('SUBV', 'A', current_x - x)
        if y > current_y:
            program.ins('ADDV', 'B', y - current_y)
        elif y < current_y:
            program.ins('SUBV', 'B', current_y - y)
        program.ins('SETPX', 'C')
        current_x, current_y = x, y
    program.ins('POP', 'B')
    program.ins('POP', 'A')
    program.ins('RET')


def add_sprite_call(program, name, x, y, color):
    program.load('A', x)
    program.load('B', y)
    program.load('C', color)
    program.ins('CALL', pg(name), of(name))


def build_program():
    program = Prog()
    program.load('C', 0)
    program.ins('FILL', 'C')

    # Fixed stars, moon, craters, and a launch platform.
    stars = [
        (4, 6), (11, 12), (18, 5), (26, 10), (34, 4), (43, 9),
        (52, 5), (59, 14), (7, 22), (15, 18), (24, 25), (39, 20),
        (48, 27), (57, 23), (3, 34), (14, 31), (45, 35), (55, 30),
    ]
    for x, y in stars:
        add_pixel(program, x, y, 12)
        add_pixel(program, x + 1, y, 13)

    for x, y in [
        (49, 8), (50, 7), (51, 6), (52, 6), (53, 7), (54, 8),
        (48, 9), (55, 9), (48, 10), (55, 10), (49, 11), (50, 12),
        (51, 12), (52, 12), (53, 11), (54, 10),
    ]:
        add_pixel(program, x, y, 4)
    for x, y in [(51, 8), (53, 9), (50, 10)]:
        add_pixel(program, x, y, 14)

    for x in range(8, 57):
        add_pixel(program, x, 56, 8 if x % 4 else 9)
    for x in range(18, 47):
        add_pixel(program, x, 54, 7)

    frames = [
        (10, 47, 'flame_big'), (12, 45, 'flame_small'),
        (14, 43, 'flame_big'), (16, 41, 'flame_small'),
        (18, 39, 'flame_big'), (20, 37, 'flame_small'),
        (22, 35, 'flame_big'), (24, 33, 'flame_small'),
        (26, 31, 'flame_big'), (28, 29, 'flame_small'),
        (30, 27, 'flame_big'), (32, 25, 'flame_small'),
        (34, 23, 'flame_big'), (36, 21, 'flame_small'),
        (38, 23, 'flame_big'), (40, 25, 'flame_small'),
        (42, 27, 'flame_big'), (44, 29, 'flame_small'),
        (42, 31, 'flame_big'), (40, 33, 'flame_small'),
        (38, 35, 'flame_big'), (36, 37, 'flame_small'),
        (34, 39, 'flame_big'), (32, 41, 'flame_small'),
        (30, 43, 'flame_big'), (28, 45, 'flame_small'),
        (26, 47, 'flame_big'), (24, 45, 'flame_small'),
        (22, 43, 'flame_big'), (20, 45, 'flame_small'),
    ]
    program.label('animation')
    for frame, (x, y, flame) in enumerate(frames):
        old_x, old_y, old_flame = frames[frame - 1]
        for sprite, color in [
            ('body', 0), ('window', 0), (old_flame, 0),
        ]:
            add_sprite_call(program, sprite, old_x, old_y, color)
        add_sprite_call(program, 'body', x, y, 2)
        add_sprite_call(program, 'window', x, y, 10)
        add_sprite_call(program, flame, x, y, 3 if frame % 2 else 4)
        if frame % 4 == 0:
            program.ins('SOUND', 72 + frame // 4, 3)
        program.ins('WAIT')
    program.ins('JMP', pg('animation'), of('animation'))

    for name in SPRITES:
        add_sprite(program, name)
    return program.link()


def write_memory_file(code, path='showcase_memory.txt'):
    memory = [0] * 8192
    memory[4096:4096 + len(code)] = code
    with open(path, 'w') as output:
        output.write('\n'.join(map(str, memory)))
        output.write('\n')


if __name__ == '__main__':
    code = build_program()
    print(bytes(code).hex())
    write_memory_file(code)
