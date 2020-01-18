class Hint:

    def __init__(self, board):

        self.board = board
        self.hint = self.get_hint()

    def get_hint(self):
        tiles = {tile for tile in self.board.tiles.values() if tile.value is None}
        for cb in [self.single,
                   self.hidden_single,
                   self.naked_single,
                   # self.naked_neighbors,
                   # self.hidden_pair,
                   # self.pointing,
                   # self.box_line_intersect,
                   ]:
            # print(cb)
            for tile in tiles:
                x = cb(tile)  # Walrus operator if this was on python 3.8
                if x:
                    return x

    @staticmethod
    def single(tile):
        for attr in ['row', 'col', 'box']:
            tile_values = {t.value for t in getattr(tile, f'{attr}_neighbors')}
            if len(tile_values) == 9:  # 8 numbers plus None
                val = {x for x in range(1, 10) if x not in tile_values}
                print(f'Single {tile.position}, value {val}')
                return tile.position, val

    def hidden_single(self, tile):
        for attr in ['row', 'col', 'box']:
            known = {t.value for t in getattr(tile, f'{attr}_neighbors') if t.value}
            remaining = set(range(1, 10)) - known
            unknown = {t for t in getattr(tile, f'{attr}_neighbors') if not t.value}

            for val in remaining:
                if self.board.validate(tile, val):
                    continue
                invalid = 0
                for _tile in unknown:
                    if self.board.validate(_tile, value=val):
                        invalid += 1
                    else:
                        possible = val

                if invalid == len(unknown) - 1:
                    print(f'Hidden single {tile.position}, value {possible}')
                    return tile.position, possible

    def naked_single(self, tile):
        possible = self.do_validations(tile)
        if len(possible) == 1:
            print(f'Naked single {tile.position}, value {possible}')
            # noinspection PyUnboundLocalVariable
            return tile.position, possible[0]

    def find_neighboring_values(self, tile):
        missing_values = self.do_validations(tile)
        for attr in ['row', 'col', 'box']:
            neighbors = getattr(tile, f'{attr}_neighbors')
            missing = {n: self.do_validations(n) for n in neighbors
                       if n.value is None}
            missing[tile] = missing_values
            missing_list = list(missing.keys())
            if missing_list.count(missing_values) == len(missing_values):
                ...

    def do_validations(self, tile):
        validated = set()
        for n in range(1, 10):
            if not self.board.validate(tile, value=n):
                validated.add(n)
        return validated

    def hidden_pair(self):
        ...

    def pointing(self):
        ...

    def box_line_intersect(self):
        ...
