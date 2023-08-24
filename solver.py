import numpy as np


def find_solution(grid: np.array):
    visit = set()
    best = [[], 0]
    path = []
    explore = 0
    last = 0

    def dfs(grid: np.array, score: int):
        nonlocal visit, best, path, explore, last

        explore += 1
        if explore == last + 100:
            print(explore)
            last = explore

        # Mark current grid as having been visited and check for new high score
        visit.add(grid.tobytes())
        if score > best[1]:
            print(f"new solution: {score}")
            best = [path[:], score]

        target_apples = 2
        discovered = False
        branches = 0
        while not discovered and target_apples <= 10:
            for r in range(10):
                for c in range(17):
                    for r_size in range(1, 10 - r + 1):
                        for c_size in range(1, 17 - c + 1):
                            if branches < 4:
                                section = grid[r : r + r_size, c : c + c_size]

                                if (
                                    np.count_nonzero(section) > target_apples
                                    or np.sum(section) > 10
                                ):
                                    break
                                elif np.sum(section) == 10:
                                    old_section = section.copy()
                                    section.fill(0)
                                    if grid.tobytes() not in visit:
                                        discovered = True
                                        branches += 1
                                        path.append((r, c, r_size, c_size))
                                        dfs(
                                            grid=grid,
                                            score=score + np.count_nonzero(old_section),
                                        )
                                        path.pop()
                                    grid[r : r + r_size, c : c + c_size] = old_section
                                    break
            if not discovered:
                target_apples += 1

    dfs(grid, 0)
    print(f"calculated optimal score: {best[1]}")
    return best[0]


test_grid = np.random.randint(1, 10, (10, 17))
print(find_solution(test_grid))
