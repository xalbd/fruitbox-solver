#include <cstdlib>
#include <iostream>
#include <numeric>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

long long calc_hash(array<array<int, 17>, 10> &grid) {
    long long output = 0;
    for (array<int, 17> row : grid) {
        for (int num : row) {
            output = output * 33 + num + 1;
        }
    }

    return output;
}

int explored = 0;
int last = 0;
auto start = chrono::steady_clock::now();
void dfs(array<array<int, 17>, 10> grid, int score, vector<vector<int>> &path,
         unordered_set<long long> &visit, pair<vector<vector<int>>, int> &best) {
    visit.insert(calc_hash(grid));
    if (score > best.second) {
        cout << "new solution: " << score << endl;
        best = make_pair(path, score);
    }
    explored++;
    if (explored == last + 10000) {
        cout << explored << endl;
        last = explored;
    }
    if (explored == 10000) {
        auto end = chrono::steady_clock::now();
        chrono::duration<double, std::milli> elapsed = end - start;

        cout << elapsed.count() << endl;
    }

    int prefix[10][18][2];
    for (int r = 0; r < 10; r++) {
        prefix[r][0][0] = 0;
        prefix[r][0][1] = 0;
        for (int c = 1; c <= 17; c++) {
            prefix[r][c][0] = prefix[r][c - 1][0] + grid[r][c - 1];
            prefix[r][c][1] = prefix[r][c - 1][1] + (grid[r][c - 1] != 0 ? 1 : 0);
        }
    }
    int target_apples = 2;
    int branches = 0;
    while (target_apples <= 10 && branches < 3) {
        for (int r = 0; r < 10 && branches < 3; r++) {
            for (int c = 0; c < 17 && branches < 3; c++) {
                for (int r_size = 1; r_size < 10 - r + 1 && branches < 3; r_size++) {
                    for (int c_size = 1; c_size < 17 - c + 1 && branches < 3; c_size++) {
                        int sum = 0;
                        int apples = 0;
                        for (int sub_r = 0; sub_r < r_size; sub_r++) {
                            sum += prefix[r + sub_r][c + c_size][0] - prefix[r + sub_r][c][0];
                            apples += prefix[r + sub_r][c + c_size][1] - prefix[r + sub_r][c][1];
                        }

                        if (sum > 10 || apples > target_apples)
                            break;
                        else if (sum == 10 && apples == target_apples) {
                            auto copy_grid = grid;
                            for (int sub_r = 0; sub_r < r_size; sub_r++) {
                                for (int sub_c = 0; sub_c < c_size; sub_c++) {
                                    copy_grid[r + sub_r][c + sub_c] = 0;
                                }
                            }

                            if (visit.find(calc_hash(copy_grid)) == visit.end()) {
                                branches++;
                                vector<int> action = {r, c, r_size, c_size};
                                path.push_back(action);
                                dfs(copy_grid, score + apples, path, visit, best);
                                path.pop_back();
                            }

                            break;
                        }
                    }
                }
            }
        }

        target_apples++;
    }
}

int main() {
    pair<vector<vector<int>>, int> best = make_pair(vector<vector<int>>(), 0);
    unordered_set<long long> visit;
    vector<vector<int>> path;
    array<array<int, 17>, 10> grid;
    srand(time(0));
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 17; j++) {
            grid[i][j] = (rand() % 9) + 1;
        }
    }

    // for (int r = 0; r < 10; r++)
    //     for (int c = 0; c < 17; c++) cin >> grid[r][c];

    dfs(grid, 0, path, visit, best);
}