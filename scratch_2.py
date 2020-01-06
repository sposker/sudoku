from database import Database

from concurrent.futures import ProcessPoolExecutor
import time

db = Database()


def solve(puzzle):
    from classes import Board
    import time
    time.perf_counter()
    b = Board(puzzle=puzzle)
    uid = puzzle.uid
    b.solve()
    print(f'Solved {uid}.')
    return time.perf_counter()


def main():
    from classes import Board

    time.perf_counter()
    sub = list(db.all_puzzles.values())[:50]
    for puzzle in sub:
        b = Board(puzzle=puzzle)
        b.solve()
        print(f'Solved {puzzle.uid}.')
    print(time.perf_counter())


# def main():
#     time.perf_counter()
#     puzzles = list(db.all_puzzles.values())[:50]
#     with ProcessPoolExecutor(max_workers=15) as pool:
#         results = list(pool.map(solve, puzzles))
#
#     multi = time.perf_counter()
#
#     print('Sum=', sum(results))
#     average = sum(results) / len(results)
#
#     print(f'Total time: {multi}s for {len(results)} puzzles.\n'
#           f'Average time per puzzle per process: {average}s.\n'
#           f'Slowest solve time: {max(results)}; Fastest solve time: {min(results)}.')


traceback = 'example\ntraceback\nstring'
lines = traceback.split('\n')
lines.reverse()

parts = []
n = 0

while lines:
    while n < 2000 and lines:
        line = lines.pop()
        parts.append(line)
        n += len(line)
    message = '\n'.join(parts[:-1])
    if n < 2000:  # End of message
        message += '\n' + parts[-1]
    print(message)

    parts = parts[-1]
    n = len(parts[0])
