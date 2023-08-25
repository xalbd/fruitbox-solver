#include <chrono>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <queue>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

struct Selection {
    int apples;
    vector<int> coors;
    array<array<int, 17>, 10> grid;

    Selection(int apples, int r, int c, int r_size, int c_size, array<array<int, 17>, 10> grid)
        : apples(apples), coors{{r, c, r_size, c_size}}, grid(grid){};
};

class Comp {
   public:
    bool operator()(Selection a, Selection b) { return a.apples > b.apples; }
};

string calc_hash(array<array<int, 17>, 10> &grid) {
    string output = "";
    for (array<int, 17> row : grid) {
        for (int num : row) {
            output += to_string(num);
        }
    }

    return output;
}

auto start = chrono::steady_clock::now();
void dfs(array<array<int, 17>, 10> grid, int score, vector<vector<int>> &path,
         unordered_set<string> &visit, pair<vector<vector<int>>, int> &best) {
    if (visit.find(calc_hash(grid)) != visit.end()) return;
    visit.insert(calc_hash(grid));
    if (score > best.second) {
        chrono::duration<double, std::milli> ms = chrono::steady_clock::now() - start;
        cout << "new solution: " << score << " at time: " << ms.count() / 1000 << "s" << endl;
        best = make_pair(path, score);
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
    priority_queue<Selection, vector<Selection>, Comp> selections;
    for (int r = 0; r < 10; r++) {
        for (int c = 0; c < 17; c++) {
            for (int r_size = 1; r_size < 10 - r + 1; r_size++) {
                for (int c_size = 1; c_size < 17 - c + 1; c_size++) {
                    int sum = 0;
                    int apples = 0;
                    for (int sub_r = 0; sub_r < r_size; sub_r++) {
                        sum += prefix[r + sub_r][c + c_size][0] - prefix[r + sub_r][c][0];
                        apples += prefix[r + sub_r][c + c_size][1] - prefix[r + sub_r][c][1];
                    }

                    if (sum > 10 || apples == 0)
                        break;
                    else if (sum == 10) {
                        auto copy_grid = grid;
                        for (int sub_r = 0; sub_r < r_size; sub_r++) {
                            for (int sub_c = 0; sub_c < c_size; sub_c++) {
                                copy_grid[r + sub_r][c + sub_c] = 0;
                            }
                        }

                        selections.push(Selection(apples, r, c, r_size, c_size, copy_grid));
                        break;
                    }
                }
            }
        }
    }

    for (int i = 0; i < int(selections.size()); i++) {
        path.push_back(selections.top().coors);
        dfs(selections.top().grid, score + selections.top().apples, path, visit, best);
        selections.pop();
        path.pop_back();
    }
}

int main() {
    pair<vector<vector<int>>, int> best = make_pair(vector<vector<int>>(), 0);
    unordered_set<string> visit;
    vector<vector<int>> path;
    array<array<int, 17>, 10> grid;
    srand(time(0));
    // for (int i = 0; i < 10; i++) {
    //     for (int j = 0; j < 17; j++) {
    //         grid[i][j] = (rand() % 9) + 1;
    //     }
    // }

    for (int r = 0; r < 10; r++)
        for (int c = 0; c < 17; c++) cin >> grid[r][c];

    dfs(grid, 0, path, visit, best);
}