// Dmitry [cdkrot.me] Sayutin (2021)

#include <bits/stdc++.h>

using std::cin;
using std::cout;
using std::cerr;

using std::vector;
using std::map;
using std::array;
using std::set;
using std::string;
using std::queue;

using std::pair;
using std::make_pair;

using std::tuple;
using std::make_tuple;
using std::get;

using std::min;
using std::abs;
using std::max;
using std::swap;

using std::unique;
using std::sort;
using std::generate;
using std::reverse;
using std::min_element;
using std::max_element;

#ifdef LOCAL
#define LASSERT(X) assert(X)
#else
#define LASSERT(X) {}
#endif

template <typename T>
T input() {
    T res;
    cin >> res;
    LASSERT(cin);
    return res;
}

template <typename IT>
void input_seq(IT b, IT e) {
    std::generate(b, e, input<typename std::remove_reference<decltype(*b)>::type>);
}

#define SZ(vec)         int((vec).size())
#define ALL(data)       data.begin(),data.end()
#define RALL(data)      data.rbegin(),data.rend()
#define TYPEMAX(type)   std::numeric_limits<type>::max()
#define TYPEMIN(type)   std::numeric_limits<type>::min()

int delta;

int is_equal(int a, int b) {
    return abs(a - b) <= delta;
}

int is_le(int a, int b) {
    return is_equal(a, b) or a < b;
}

int is_ge(int a, int b) {
    return is_le(b, a);
}

bool is_same(pair<int, int> a, pair<int, int> b) {
    return is_equal(a.first, b.first) and is_equal(a.second, b.second);
}

bool matches(const vector<pair<int, int>>& isoform, const vector<pair<int, int>>& query) {
    int left = -1;
    int ptr = SZ(isoform);

    while (ptr - left > 1) {
        int mid = (left + ptr) / 2;
        if (is_ge(isoform[mid].second, query[0].second))
            ptr = mid;
        else
            left = mid;
    }

    if (ptr + SZ(query) - 1 >= SZ(isoform))
        return false;

    if (not is_le(isoform[ptr].first, query[0].first) or 
        not is_equal(isoform[ptr].second, query[0].second))
        return false;
    
    for (int t = 1; t < SZ(query) - 1; ++t)
        if (not is_same(isoform[ptr + t], query[t]))
            return false;

    if (not is_equal(isoform[ptr + SZ(query) - 1].first, query.back().first) or
        not is_ge(isoform[ptr + SZ(query) - 1].second, query.back().second))
        return false;

    return true;
}

int main() {
    std::iostream::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);

    // code here
    int n = input<int>();
    delta = input<int>();

    assert(cin.get() == '\n');
    vector<vector<pair<int, int>>> in(n);

    auto readline = []() {
        vector<pair<int, int>> res;

        while (true) {
            int a;
            char t;
            int b;
            cin >> a >> t >> b;
            assert(t == '-');
            res.emplace_back(a, b);

            char c = cin.get();
            if (c == '\n')
                break;
            assert(c == ',');
        }

        return res;
    };
    
    for (int i = 0; i < n; ++i)
        in[i] = readline();

    int Q = input<int>();
    for (int q = 0; q < Q; ++q) {
        auto query = readline();
                
        // int i;
        // for (i = 0; i < n and not matches(in[i], query); ++i) {}

        // cout << (i == n ? -1 : i) << "\n";

        int total = 0;
        int ans_id = -1;
        for (int i = n - 1; i >= 0; --i)
            if (matches(in[i], query))
                ans_id = i, total += 1;

        cout << ans_id << " " << total << "\n";
    }
    

    return 0;
}
