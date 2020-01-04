from classes import Puzzle
import random


class Database:
    files = ['easy.csv', 'intermediate.csv', 'expert.csv']
    keywords = ['puzzle', 'givens', 'singles', 'hidden_singles', 'naked_pairs', 'hidden_pairs',
                'pointing_pairs_triples', 'box_line_intersections', 'guesses', 'backtracks', 'difficulty']

    def __init__(self):
        self.all_puzzles = {}
        self.load()

    def load(self):
        for file in self.files:
            self.all_puzzles.update(self._load(file))

    def _load(self, file):
        objects = {}
        with open(file) as f:
            x = True
            for line in f:
                if x:
                    x = not x
                    continue  # Skip first line
                kwargs = {k: v for k, v in zip(self.keywords, line.split(','))}
                p = Puzzle(**kwargs)
                objects[p.uid] = p

        return objects

    @property
    def blank_puzzle(self):
        puzzle = {}
        for i in range(9):
            for j in range(9):
                puzzle[(i, j)] = None
        return puzzle

    def puzzle_by_uid(self, uid):
        return self.all_puzzles[uid]

    def random_puzzle(self, difficulty=None):
        if not difficulty:
            return random.choice(list(self.all_puzzles.values()))

        if difficulty.lower() in ['easy', 'beginner']:
            choices = self._random_puzzle('Easy')
        elif difficulty.lower() in ['medium', 'intermediate']:
            choices = self._random_puzzle('Intermediate')
        elif difficulty.lower() in ['hard', 'expert']:
            choices = self._random_puzzle('Expert')

        return random.choice(choices)

    def _random_puzzle(self, key: str):
        _choices = []
        for v in self.all_puzzles.values():
            if v.difficulty == key:
                _choices.append(v)
        return _choices
