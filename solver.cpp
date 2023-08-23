#include <cstdlib>
#include <iostream>
#include <numeric>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

string calc_hash(vector<vector<int>> &grid) {
    string output = "";
    for (vector<int> row : grid) {
        for (int num : row) {
            output += to_string(num);
        }
    }

    return output;
}

int explored = 0;
int last = 0;
auto start = chrono::steady_clock::now();
void dfs(pair<vector<vector<int>>, int> &best, vector<vector<int>> &grid, int score,
         vector<vector<int>> &path, unordered_set<string> &visit) {
    visit.insert(calc_hash(grid));
    if (score > best.second) {
        cout << "new solution: " << score << endl;
        best = make_pair(path, score);
    }
    explored++;
    if (explored == last + 1000) {
        cout << explored << endl;
        last = explored;
    }
    if (explored == 10000) {
        auto end = chrono::steady_clock::now();
        chrono::duration<double, std::milli> elapsed = end - start;

        cout << elapsed.count() << endl;
    }
    int sum = 0;
    int apples = 0;
    for (int r = 0; r < 10; r++) {
        for (int c = 0; c < 17 && count(grid[r].begin(), grid[r].end(), 0) != 17; c++) {
            for (int r_size = 1; r_size < 10 - r + 1; r_size++) {
                for (int c_size = 1; c_size < 17 - c + 1; c_size++) {
                    // Build submatrix of interest
                    vector<vector<int>> submatrix;
                    sum = 0;
                    apples = 0;
                    for (int sub_r = 0; sub_r < r_size; sub_r++) {
                        submatrix.push_back(vector<int>(grid[r + sub_r].begin() + c,
                                                        grid[r + sub_r].begin() + c + c_size));
                        sum += accumulate(submatrix[sub_r].begin(), submatrix[sub_r].end(), 0);
                        apples +=
                            c_size - count(submatrix[sub_r].begin(), submatrix[sub_r].end(), 0);
                        if (sum == 0 || sum > 10) {
                            break;
                        }
                    }

                    if (sum > 10 || (score < 20 && apples > 2))
                        break;
                    else if (sum == 10) {
                        for (int sub_r = 0; sub_r < r_size; sub_r++) {
                            for (int sub_c = 0; sub_c < c_size; sub_c++) {
                                grid[r + sub_r][c + sub_c] = 0;
                            }
                        }

                        if (visit.find(calc_hash(grid)) == visit.end()) {
                            vector<int> action = {r, c, r_size, c_size};
                            path.push_back(action);
                            dfs(best, grid, score + apples, path, visit);
                            path.pop_back();
                        }

                        for (int sub_r = 0; sub_r < r_size; sub_r++) {
                            for (int sub_c = 0; sub_c < c_size; sub_c++) {
                                grid[r + sub_r][c + sub_c] = submatrix[sub_r][sub_c];
                            }
                        }

                        break;
                    }
                }
            }
        }
    }
}

int main() {
    pair<vector<vector<int>>, int> best = make_pair(vector<vector<int>>(), 0);
    unordered_set<string> visit;
    vector<vector<int>> path;
    vector<vector<int>> grid;

    srand(time(0));
    for (int i = 0; i < 10; i++) {
        vector<int> a;
        for (int j = 0; j < 17; j++) {
            a.push_back((rand() % 9) + 1);
        }
        grid.push_back(a);
    }

    dfs(best, grid, 0, path, visit);
}