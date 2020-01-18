class Container:

    def __init__(self, identifier):
        self.identifier = identifier
        self.members = set()
        self.matched_tiles = set()
        self.matched_values = set()

    @property
    def accounted_values(self):
        return self.matched_tiles, self.matched_values

    @property
    def values(self):
        return {v for v, t in self.accounted_values} | {tile.value for tile in self.members if tile.value is not None}


class Row(Container):
    ...


class Column(Container):
    ...


class Box(Container):
    ...


class Grid:
    ...

