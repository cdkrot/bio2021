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
#define len(obj) SZ(obj)

int seg_intersect(pair<int, int> seg1, pair<int, int> seg2) {
    return max(0, min(seg1.second, seg2.second) - max(seg1.first, seg2.first));
}

vector<pair<int, int>> get_dual(const vector<pair<int, int>>& isoform) {
    vector<pair<int, int>> res;

    for (int i = 0; i + 1 < SZ(isoform); ++i) {
        res.emplace_back(isoform[i].second, isoform[i + 1].first);
    }

    return res;
}

int intersection(const vector<pair<int, int>>& A, const vector<pair<int, int>>& B) {
    int p = 0;
    int q = 0;
    int res = 0;
    
    while (p != len(A) and q != len(B)) {
        res += seg_intersect(A[p], B[q]);

        if (A[p].second <= B[q].second)
            p += 1;
        else
            q += 1;
    }
    
    return res;
}

int total_len(const vector<pair<int, int>>& seglist) {
    int res = 0;
    for (auto [a, b]: seglist)
        res += b - a;
    return res;
}

double get_score(const vector<pair<int, int>>& isoform, const vector<pair<int, int>>& query) {
    int left = -1;
    int ptr = SZ(isoform);

    while (ptr - left > 1) {
        int mid = (left + ptr) / 2;
        if (isoform[mid].second < query[0].first)
            left = mid;
        else
            ptr = mid;
    }

    ptr = max(0, ptr - 1);
    
    int endptr = ptr;
    vector<pair<int, int>> iso;
    while (endptr != len(isoform) and isoform[endptr].first <= query[SZ(query) - 1].second) {
        iso.push_back(isoform[endptr]);
        endptr += 1;
    }

    if (endptr != len(isoform)) {
        iso.push_back(isoform[endptr]);
        endptr += 1;
    }

    auto seg_coverage = intersection(iso, query);
    auto outseg_coverage = intersection(get_dual(iso), get_dual(query));

    return (2.0/3) * (seg_coverage / (double) total_len(query))
        +  (1.0/3) * (outseg_coverage / (double) total_len(get_dual(query)));
}

int main(int argc, char** argv) {
    std::iostream::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);

    // code here
    int n = input<int>();
    input<int>(); // delta

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

    vector<vector<pair<int, int>>> queries(Q);
    for (int q = 0; q < Q; ++q)
        queries[q] = readline();

    int BLOCK, START;

    if (argc == 1)
        BLOCK = Q, START = 0;
    else {
        int cnt = atoi(argv[1]);
        int id = atoi(argv[2]);

        BLOCK = (Q + cnt - 1) / cnt;
        START = BLOCK * id;
    }
    
    cerr << std::fixed;
    cerr.precision(7);
    for (int q = START; q < min(Q, START+BLOCK); ++q) {
        auto query = queries[q];
                
        // int i;
        // for (i = 0; i < n and not matches(in[i], query); ++i) {}

        // cout << (i == n ? -1 : i) << "\n";

        double best_score = -1;
        int ans_id = -1;
        for (int i = 0; i < n; ++i) {
            auto sc = get_score(in[i], query);

            if (sc > best_score)
                ans_id = i, best_score = sc;
        }

        cout << ans_id << "\n";
	cerr << "Progress " << double(q - START) / BLOCK << "\n";
    }
    

    return 0;
}
