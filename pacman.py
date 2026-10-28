from asm2 import Prog, of, pg


MAZE = (
    '############################',
    '#............##............#',
    '#.####.#####.##.#####.####.#',
    '#o####.#####.##.#####.####o#',
    '#.####.#####.##.#####.####.#',
    '#..........................#',
    '#.####.##.########.##.####.#',
    '#.####.##.########.##.####.#',
    '#......##....##....##......#',
    '######.##.###  ###.##.######',
    '     #.##.#      #.##.#     ',
    '     #.##.# ###  #.##.#     ',
    '     #....# #    #....#     ',
    '     ####.# #    #.####     ',
    '          . #    #.         ',
    '     ####.# #### #.####     ',
    '     #....#      #....#     ',
    '     #.##.# #### #.##.#     ',
    '     #.##.#      #.##.#     ',
    '######.##.########.##.######',
    '#............##............#',
    '#.####.#####.##.#####.####.#',
    '#.####.#####.##.#####.####.#',
    '#o..##................##..o#',
    '###.##.##.########.##.##.###',
    '#......##....##....##......#',
    '#.##########.##.##########.#',
    '#..........................#',
    '#.####.#####.##.#####.####.#',
    '#.####.#####.##.#####.####.#',
    '############################',
)


def add_set_pixel(program, x, y, color):
    program.load('A', x)
    program.load('B', y)
    program.load('C', color)
    program.ins('SETPX', 'C')


def add_line(program, x, y, length, color, vertical=False):
    program.load('A', x)
    program.load('B', y)
    program.load('C', color)
    program.load('D', length)
    target = 'line_v' if vertical else 'line_h'
    program.ins('CALL', pg(target), of(target))
    program.forget()


def add_shape(program, name, points):
    program.label(name)
    program.ins('PUSH', 'A')
    program.ins('PUSH', 'B')
    current_x, current_y = 0, 0
    for x, y in points:
        delta_x, delta_y = x - current_x, y - current_y
        if delta_x > 0:
            program.ins('ADDV', 'A', delta_x)
        elif delta_x < 0:
            program.ins('SUBV', 'A', -delta_x)
        if delta_y > 0:
            program.ins('ADDV', 'B', delta_y)
        elif delta_y < 0:
            program.ins('SUBV', 'B', -delta_y)
        program.ins('SETPX', 'C')
        current_x, current_y = x, y
    program.ins('POP', 'B')
    program.ins('POP', 'A')
    program.ins('RET')


def add_line_routines(program):
    program.label('line_h')
    program.ins('PUSH', 'C')
    program.label('line_h_loop')
    program.ins('POP', 'C')
    program.ins('SETPX', 'C')
    program.ins('PUSH', 'C')
    program.ins('ADDV', 'A', 1)
    program.ins('SUBV', 'D', 1)
    program.load('C', 0)
    program.ins('SKEQ', 'D', 'C')
    program.ins('JMP', pg('line_h_loop'), of('line_h_loop'))
    program.ins('POP', 'C')
    program.ins('RET')

    program.label('line_v')
    program.ins('PUSH', 'C')
    program.label('line_v_loop')
    program.ins('POP', 'C')
    program.ins('SETPX', 'C')
    program.ins('PUSH', 'C')
    program.ins('ADDV', 'B', 1)
    program.ins('SUBV', 'D', 1)
    program.load('C', 0)
    program.ins('SKEQ', 'D', 'C')
    program.ins('JMP', pg('line_v_loop'), of('line_v_loop'))
    program.ins('POP', 'C')
    program.ins('RET')


def route():
    y = 1 + 2 * 5
    forward = [(4 + 2 * column, y) for column in range(1, 11)]
    return forward + forward[-2:0:-1]


def build_program():
    program = Prog()
    path = route()

    # Clear the stage and draw the maze walls.
    program.load('C', 0)
    program.ins('FILL', 'C')
    wall_color = 9
    for row, tiles in enumerate(MAZE):
        column = 0
        while column < len(tiles):
            if tiles[column] != '#':
                column += 1
                continue
            start = column
            while column < len(tiles) and tiles[column] == '#':
                column += 1
            add_line(program, 4 + 2 * start, 1 + 2 * row,
                     2 * (column - start), wall_color)

    # Pellets sit on the route and disappear naturally when sprites pass over them.
    for index, (x, y) in enumerate(path):
        if index % 2 == 0:
            add_set_pixel(program, x + 1, y + 1, 4)

    program.label('animation')
    for frame, pacman in enumerate(path):
        previous_pacman = path[frame - 1]
        ghost = path[(frame - 12) % len(path)]
        previous_ghost = path[(frame - 13) % len(path)]

        # Erase old sprites, then draw the next game state.
        for x, y, shape in [
            (*previous_pacman, 'pac_closed'),
            (*previous_ghost, 'ghost'),
        ]:
            add_set_pixel(program, x, y, 0)
            program.ins('CALL', pg(shape), of(shape))

        add_set_pixel(program, *pacman, 4)
        program.ins('CALL', pg('pac_open' if frame % 2 == 0 else 'pac_closed'),
                    of('pac_open' if frame % 2 == 0 else 'pac_closed'))
        add_set_pixel(program, *ghost, 2)
        program.ins('CALL', pg('ghost'), of('ghost'))

        if frame % 6 == 0:
            program.ins('SOUND', 60 + (frame // 6) % 8, 4)
        program.ins('WAIT')

    program.ins('JMP', pg('animation'), of('animation'))

    # Pac-Man has a changing mouth; each shape preserves the caller coordinates.
    add_shape(program, 'pac_closed', [
        (0, 0), (1, 0), (2, 0),
        (2, 1), (2, 2), (1, 2), (0, 2), (0, 1),
    ])
    add_shape(program, 'pac_open', [
        (0, 0), (1, 0), (2, 0),
        (0, 1), (0, 2), (1, 2), (2, 2),
    ])
    add_shape(program, 'ghost', [
        (0, 0), (1, 0), (2, 0),
        (0, 1), (1, 1), (2, 1),
        (0, 2), (2, 2),
    ])
    add_line_routines(program)
    return program.link()


def write_memory_file(code, path='pacman_memory.txt'):
    memory = [0] * 8192
    memory[4096:4096 + len(code)] = code
    with open(path, 'w') as output:
        output.write('\n'.join(map(str, memory)))
        output.write('\n')


if __name__ == '__main__':
    code = build_program()
    print(bytes(code).hex())
    write_memory_file(code)