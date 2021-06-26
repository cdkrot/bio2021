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

    map<pair<int, int>, vector<int>> index;
    map<int, vector<int>> er_index, el_index; // exon-right, exon-left
    for (int i = 0; i < n; ++i) {
        in[i] = readline();

        for (auto elem: in[i]) {
            index[make_pair(elem.first / (delta + 1), elem.second / (delta + 1))].push_back(i);

            er_index[elem.second / (delta + 1)].push_back(i);
            el_index[elem.first / (delta + 1)].push_back(i);
        }
    }
    vector<int> the_none;
    
    auto get_ref = [&](int a, int b) -> vector<int>& {
        auto it = index.find(make_pair(a, b));
        if (it != index.end())
            return it->second;
        return the_none;
    };

    auto er_get_ref = [&](int a) -> vector<int>& {
        auto it = er_index.find(a);
        if (it != er_index.end())
            return it->second;
        return the_none;
    };

    auto el_get_ref = [&](int a) -> vector<int>& {
        auto it = el_index.find(a);
        if (it != el_index.end())
            return it->second;
        return the_none;
    };

    
    int Q = input<int>();
    for (int q = 0; q < Q; ++q) {
        auto query = readline();

        int best_ind = -1;
        int min_size = TYPEMAX(int);

        int ER = er_get_ref(query[0].second / (delta + 1) - 1).size()
               + er_get_ref(query[0].second / (delta + 1) + 0).size()
               + er_get_ref(query[0].second / (delta + 1) + 1).size();

        int EL = el_get_ref(query.back().first / (delta + 1) - 1).size()
               + el_get_ref(query.back().first / (delta + 1) + 0).size()
               + el_get_ref(query.back().first / (delta + 1) + 1).size();
        
        for (int i = 1; i < SZ(query) - 1; ++i) {
            int A = query[i].first / (delta + 1);
            int B = query[i].second / (delta + 1);

            int sz = 0;
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy)
                    sz += get_ref(A + dx, B + dy).size();

            if (sz < min_size)
                min_size = sz, best_ind = i;
        }

        int res = -1;

        if (min({EL, ER, min_size}) == EL) {
            int A = query[0].second / (delta + 1);

            for (int dx = -1; dx <= 1 and res == -1; ++dx)
                for (int i: er_get_ref(A + dx))
                    if (matches(in[i], query)) {
                        res = i;
                        break;
                    }
        } else if (min(ER, min_size) == ER) {
            int A = query.back().first / (delta + 1);
            
            for (int dx = -1; dx <= 1 and res == -1; ++dx)
                for (int i: el_get_ref(A + dx))
                    if (matches(in[i], query)) {
                        res = i;
                        break;
                    }
        } else {
            int A = query[best_ind].first / (delta + 1);
            int B = query[best_ind].second / (delta + 1);
        
            for (int dx = -1; dx <= 1 and res == -1; ++dx)
                for (int dy = -1; dy <= 1 and res == -1; ++dy)
                    for (int i: get_ref(A + dx, B + dy))
                        if (matches(in[i], query)) {
                            res = i;
                            break;
                        }
        }

        cout << res << "\n";
    }

    return 0;
}
