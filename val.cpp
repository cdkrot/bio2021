#include "testlib.h"
#include <string>
using namespace std;

const int maxn = 6e5;
const int maxq = 6e5;
const int maxdelta = 100;

const int maxcoord = int(1e9);

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
    registerValidation(argc, argv);
    
    int n = inf.readInt(1, maxn);
    inf.readSpace();
    int delta = inf.readInt(0, maxdelta);
    inf.readEoln();
    
    int totalentries = 0;

    auto readline = [&](bool do_gap_checks=true) {
        int prev_end = -2 * delta - 1;
        
        int entrieshere = 0;
        
        while (true) {
            totalentries += 1;
            entrieshere += 1;
            
            int a = readInt(prev_end + 1, maxcoord);
            inf.readChar('-');
            int b = readInt(a + 1, maxcoord);

            if (do_gap_checks) {
                ensuref(b - a >= 2 * delta + 1, "a=%d, b=%d", a, b);
                ensuref(a - prev_end >= 2 * delta + 1, "a=%d, b=%d", a, b);
            }
            
            prev_end = b;
            char ch = inf.readChar();
            if (ch == '\n')
                break;

            ensure(ch == ',');
        }

        ensure(entrieshere >= 2);
    };
    
    for (int i = 0; i < n; ++i)
        readline();

    int q = inf.readInt(1, maxq);
    inf.readEoln();

    for (int i = 0; i < q; ++i)
        readline(false);

    inf.readEof();
    ensure(totalentries <= int(1e7));
}
