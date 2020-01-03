class Puzzle:
    grid = []

    for col in range(9):
        for row in range(9):
            grid.append((col, row))

    def __init__(self, definition, rating):

        self.rating = rating
        self.values = {}
        for k, v in enumerate(definition):
            location = self.grid[k]
            try:
                value = int(v)
            except TypeError:
                value = None
            if value:
                self.values[location] = value

    def __getitem__(self, item):
        return self.values[item]


class PuzzleTile:

    def __init__(self, position, value=None, locked=False):
        self.position = position
        self.value = value
        self.locked = locked
        self.possibles = []


class Board:
    """Container for logical representation of sudoku grid"""

    vert = {'top': (1, 2, 0),
            'mid': (4, 5, 3),
            'bot': (7, 8, 6),
            }
    horiz = {'left': (1, 2, 0),
             'center': (4, 5, 3),
             'right': (7, 8, 6),
             }

    sections = {}

    for vert_key, vert_value in vert.items():
        for horiz_key, horiz_value in horiz.items():
            coords = []

            for _vert_value in vert_value:
                for _horiz_value in horiz_value:
                    coords.append((_vert_value, _horiz_value))

            sections['-'.join([vert_key, horiz_key])] = coords

    def __init__(self, puzzle=None):
        self.tiles = {}
        for col in range(9):
            for row in range(9):
                self.tiles[(col, row)] = PuzzleTile((col, row))

        if puzzle:
            for k, v in puzzle.items():
                tile = self.tiles[k]
                tile.value = v
                if v:
                    tile.locked = True
        else:
            puzzle = self._generate_puzzle()

        self.puzzle = puzzle

    def __getitem__(self, item):
        return self.tiles[item].value

    def __str__(self):
        base = [None for _ in range(9)]
        matrix = [base.copy() for _ in range(9)]

        for key, value in self.tiles.items():
            col, row = key
            matrix[row - 1][col - 1] = str(value.value) if value.value else '\u2022'

        return '\n'.join([' '.join(sublist) for sublist in matrix])

    def solve(self):
        tiles = self.reset()
        self._solve_iteration(tiles)

    def _solve_iteration(self, tiles):
        tile = tiles.pop()
        for i in range(9):
            tile.value = i
            if self.validate(tile):
                try:
                    x = self._solve_iteration(tiles)
                except IndexError:  # Empty list
                    return True
                else:
                    if x:
                        return x

        else:
            tile.value = None
            tiles.append(tile)

    def reset(self):
        none_values = []
        for tile in self.tiles.values():
            if not tile.locked:
                tile.value = None
                none_values.append(tile)
        return none_values

    def build(self):
        ...

    def validate(self, tile) -> set:
        conflicts = set()
        for result in (self._check_col(tile), self._check_row(tile), self._check_box(tile)):
            conflicts = conflicts | result
        return conflicts

    def _generate_puzzle(self):
        self.reset()
        return ...

    def _check_col(self, tile):
        if tile.value is None:
            return set()
        col, row = tile.position
        others = [self.tiles[(_col, row)] for _col in range(9) if _col != col]
        matches = set()
        for other in others:
            if tile.value == other.value:
                matches.add(tile.position)
                matches.add(other.position)
        return matches

    def _check_row(self, tile):
        if tile.value is None:
            return set()
        col, row = tile.position
        others = [self.tiles[(col, _row)] for _row in range(9) if _row != row]
        matches = set()
        for other in others:
            if tile.value == other.value:
                matches.add(tile.position)
                matches.add(other.position)
        return matches

    # noinspection PyUnboundLocalVariable
    def _check_box(self, tile):
        if tile.value is None:
            return set()
        pos = tile.position
        for positions in self.sections.values():
            if pos in positions:
                others = [self.tiles[_pos] for _pos in positions if _pos != pos]
        matches = set()
        for other in others:
            if tile.value == other.value:
                matches.add(tile.position)
                matches.add(other.position)
        return matches


with open('expert.csv') as f:
    for line in f:
        _puzzle, _ = line.split(',', maxsplit=1)

tuples = []
for i in range(9):
    for j in range(9):
        tuples.append((i, j))

chars = []
for ch in _puzzle:
    if ch != '.':
        chars.append(int(ch))
    else:
        chars.append(None)

puzzle = {k: v for k, v in zip(tuples, chars)}

# puzzle = {(1, 5): 6,
#           (6, 1): 6,
#           (3, 7): 6,
#           (7, 7): 1,
#           (9, 9): 3,
#           (4, 3): 4,
#           (8, 8): 9,
#           (9, 4): 8,
#           (9, 1): 2}

b = Board(puzzle=puzzle)
print(b, end='\n\n')
# b.solve()
# print(b)
