class Puzzle:

    grid = []
    count = 0

    for col in range(9):
        for row in range(9):
            grid.append((col, row))

    def __init__(self, **kwargs):
        self.uid = Puzzle.count
        self.__dict__.update(**kwargs)
        self.values = {}
        puzzle = kwargs['puzzle']

        for k, v in zip(self.grid, list(puzzle)):
            try:
                self.values[k] = int(v)
            except ValueError:
                self.values[k] = None

        Puzzle.count += 1

    def __repr__(self):
        return ', '.join([f'{k}={v}' for k, v in self.__dict__.items() if k != 'values'])

    def __getitem__(self, item):
        return self.values[item]

    def __hash__(self):
        return hash(self.__repr__())

    def items(self):
        yield from ((k, v) for k, v in self.values.items())


class BoardTile:

    def __init__(self, position, board, value=None, locked=False):
        self.position = position
        self.board = board
        self.value = value
        self.locked = locked
        self._neighbors = None
        self._group = None

    @property
    def row(self):
        return self.position[1]

    @property
    def col(self):
        return self.position[0]

    @property
    def group(self):
        if self._group is None:
            for name, members in Board.sections.items():
                if self.position in members:
                    self._group = name
                    break
        return self._group

    @property
    def neighbors(self):
        if self._neighbors is None:
            self._neighbors = {self.find_neighbors(tile) for tile in self.board.tiles.values()}
            self._neighbors.remove(None)
            self._neighbors.remove(self)
        return self._neighbors

    def find_neighbors(self, tile):

        if self.row == tile.row or \
                self.col == tile.col or \
                self.group == tile.group:
            return tile


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
                self.tiles[(col, row)] = BoardTile((col, row), self)

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
        for i in range(1, 10):
            tile.value = i
            if not self.validate(tile):
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

    def build(self):  # TODO
        ...

    @staticmethod
    def validate(tile) -> set:
        conflicts = set()
        if tile.value is None:
            return conflicts

        for n in tile.neighbors:
            if n.value == tile.value and tile.value is not None:
                conflicts.add(n.position)

        if conflicts:
            conflicts.add(tile.position)

        return conflicts

    def _generate_puzzle(self):
        self.reset()
        return ...

    # def _check_linear(self, tile):
    #     if tile.value is None:
    #         return set()
    #     col, row = tile.position
    #     others = [self.tiles[(_col, row)] for _col in range(9) if _col != col] + \
    #              [self.tiles[(col, _row)] for _row in range(9) if _row != row]
    #     matches = set()
    #     for other in others:
    #         if tile.value == other.value:
    #             matches.add(tile.position)
    #             matches.add(other.position)
    #     return matches
    #
    # # noinspection PyUnboundLocalVariable
    # def _check_box(self, tile):
    #     if tile.value is None:
    #         return set()
    #     pos = tile.position
    #     for positions in self.sections.values():
    #         if pos in positions:
    #             others = [self.tiles[_pos] for _pos in positions if _pos != pos]
    #     matches = set()
    #     for other in others:
    #         if tile.value == other.value:
    #             matches.add(tile.position)
    #             matches.add(other.position)
    #     return matches

    def generate_hint(self):
        empties = {tile for tile in self.tiles.values() if tile.value is None}
        for tile in empties:
            results = []
            for val in range(1, 10):
                tile.value = val
                results.append(self.validate(tile))

            if results.count(set()) == 1:
                tile.value = results.index(set())
                break
            else:
                tile.value = None
        else:
            print("no hint found")
            return
        return tile.grid_position



# tuples = []
# for i in range(9):
#     for j in range(9):
#         tuples.append((i, j))
#
# chars = []
# for ch in _puzzle:
#     if ch != '.':
#         chars.append(int(ch))
#     else:
#         chars.append(None)
#
# _puzzle = {k: v for k, v in zip(tuples, chars)}

# puzzle = {(1, 5): 6,
#           (6, 1): 6,
#           (3, 7): 6,
#           (7, 7): 1,
#           (9, 9): 3,
#           (4, 3): 4,
#           (8, 8): 9,
#           (9, 4): 8,
#           (9, 1): 2}

# b = Board(puzzle=_puzzle)
# print(b, end='\n\n')
# b.solve()
# print(b)
