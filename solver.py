import numpy as np


def find_solution(grid: np.array):
    visit = set()
    best = [[], 0]

    def dfs(grid: np.array, path: list, score: int):
        nonlocal visit, best

        visit.add(grid.tobytes())
        if score > best[1]:
            print(best)
            best = [path, score]

        for r in range(10):
            for c in range(17):
                for r_size in range(1, 10 - r + 1):
                    for c_size in range(1, 17 - c + 1):
                        section = grid[r : r + r_size, c : c + c_size]

                        if np.sum(section) > 10:
                            break

                        elif np.sum(section) == 10:
                            old_section = section.copy()
                            section.fill(0)
                            if grid.tobytes() not in visit:
                                path.append((r, c, r_size, c_size))
                                dfs(
                                    grid=grid,
                                    path=path,
                                    score=score + np.count_nonzero(old_section),
                                )
                                path.pop()
                            section = old_section
                            break

    dfs(grid, [], 0)

    return best


# test_grid = np.random.randint(1, 10, size=(10, 17))
# print(find_solution(test_grid))
