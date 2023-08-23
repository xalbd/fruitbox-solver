import numpy as np


def find_solution(grid: np.array):
    visit = set()
    best = [[], 0]
    path = []

    def dfs(grid: np.array, score: int):
        nonlocal visit, best, path

        # Mark current grid as having been visited and check for new high score
        visit.add(grid.tobytes())
        if score > best[1]:
            print(f"new solution: {score}")
            best = [path[:], score]

        for r in range(10):
            for c in range(17):
                for r_size in range(1, 10 - r + 1):
                    for c_size in range(1, 17 - c + 1):
                        section = grid[r : r + r_size, c : c + c_size]

                        if np.count_nonzero(section) > 10 or np.sum(section) > 10:
                            break
                        elif np.sum(section) == 10:
                            old_section = section.copy()
                            section.fill(0)
                            if grid.tobytes() not in visit:
                                path.append((r, c, r_size, c_size))
                                dfs(
                                    grid=grid,
                                    score=score + np.count_nonzero(old_section),
                                )
                                path.pop()
                            grid[r : r + r_size, c : c + c_size] = old_section
                            break

    dfs(grid, 0)
    print(f"calculated optimal score: {best[1]}")
    return best[0]


# test_grid = np.resize([1, 9], 170).reshape((10, 17))
# print(find_solution(test_grid))
