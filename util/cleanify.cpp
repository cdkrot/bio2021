#include "testlib.h"
#include <bits/stdc++.h>

using namespace std;

const int maxn = 5e5;
const int maxq = 5e5;
const int maxdelta = 100;

const int maxcoord = int(1e9);

#define SZ(A) int((A).size())
#define ALL(A) (A).begin(), (A).end()

bool isdigit(char ch) {
    return '0' <= ch and ch <= '9';
}

int readInt(int a, int b) {
    inf.ensure(isdigit(inf.curChar()));

    int64_t res = inf.nextChar() - '0';
    while (res <= INT_MAX and isdigit(inf.curChar())) {
        res = 10 * res + inf.nextChar() - '0';
    }

    inf.ensure(a <= res and res <= b);
    return res;
}

int main(int argc, char *argv[]) {
    std::mt19937 rnd(3103199);

    registerValidation(argc, argv);
    
    int n = inf.readInt(1, maxn);
    inf.readSpace();
    int delta = inf.readInt(0, maxdelta);
    inf.readEoln();

    vector<vector<pair<int, int>>> data;
    
    int totalentries = 0;

    auto readline = [&]() {
        int begin = 0;

        vector<pair<int, int>> res;
        bool fail = false;
        
        while (true) {
            totalentries += 1;
            
            int a = readInt(begin, maxcoord);
            inf.readChar('-');
            int b = readInt(a + 1, maxcoord);

            if (not (b - a > 2 * delta) or not (a - begin > 2 * delta))
                fail = true;
            
            begin = b + 1;
            char ch = inf.readChar();
            if (ch == '\n')
                break;

            ensure(ch == ',');

            res.emplace_back(a, b);
        }

        if (SZ(res) < 2)
            fail = 1;
        
        return make_pair(fail, res);
    };
    
    for (int i = 0; i < n; ++i) {
        auto rs = readline();
        if (not rs.first)
            data.emplace_back(rs.second);
    }

    std::shuffle(ALL(data), rnd);
    cout << SZ(data) << " " << delta << "\n";
    for (auto elem: data) {
        for (int i = 0; i < SZ(elem); ++i) {
            cout << elem[i].first << "-" << elem[i].second << ",\n"[i + 1 == SZ(elem)];
        }
    }

    int q = inf.readInt(1, maxq);
    inf.readEoln();

    vector<vector<pair<int, int>>> queries;
    
    for (int i = 0; i < q; ++i) {
        auto rs = readline();
        if (not rs.first)
            queries.emplace_back(rs.second);
    }

    cout << SZ(queries) << "\n";
    std::shuffle(ALL(queries), rnd);
    for (auto elem: queries) {
        for (int i = 0; i < SZ(elem); ++i) {
            cout << elem[i].first << "-" << elem[i].second << ",\n"[i + 1 == SZ(elem)];
        }
    }

    inf.readEof();
    
    fprintf(stderr, "Cleanify results: n (%d -> %d), q (%d -> %d)\n", n, SZ(data),
            q, SZ(queries));
}
