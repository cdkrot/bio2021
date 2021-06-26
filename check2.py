import requests, zipfile, lzma, io
from requests.adapters import HTTPAdapter
import os
from fractions import Fraction

CONFIG = {
    'use_network': True,
    'use_score_file': True,
    'url': 'https://stepik.org/media/attachments/lesson/541857/',
    'test_name': '90-huge-approx',
    'secret': 'AoVEBt7FSc304ci'
}
PRINT_SCORE_MODE = False

def filestream(name):
    s = requests.Session()
    url = CONFIG['url'] + name + '.lzma'
    
    s.mount(url, HTTPAdapter(max_retries=6))
    request = s.get(url)
    
    return lzma.open(io.BytesIO(request.content), mode='rt', encoding='utf8')


def test_file():
    if CONFIG['use_network']:
        return filestream(CONFIG['test_name'] + '.txt')
    else:
        return open(os.environ['test'])


def jury_ans_file():
    if CONFIG['use_network']:
        if CONFIG['use_score_file']:
            return filestream(CONFIG['test_name'] + '.jury_score')
        else:
            return filestream(CONFIG['test_name'] + '.ans')
    return open(os.environ['test_ans'])


def parse_line(line):
    toks = line.split(',')
    pairs = map(lambda x: tuple(map(int, x.split('-'))), toks)
    return list(pairs)


def seg_intersect(seg1, seg2):
    (a, b) = seg1
    (c, d) = seg2
    return max(0, min(b, d) - max(a, c))


def get_dual(isoform):
    return [(b, a) for ((_, b), (a, _)) in zip(isoform, isoform[1:])]


def intersection(A, B):
    p = 0
    q = 0
    res = 0
    
    while p != len(A) and q != len(B):
        res += seg_intersect(A[p], B[q])

        if A[p][1] <= B[q][1]:
            p += 1
        else:
            q += 1
    return res

def total_len(seglist):
    res = 0
    for (a, b) in seglist:
        res += b - a
    return res

def match_score(isoform, query):
    left = -1
    ptr = len(isoform)

    while ptr - left > 1:
        mid = (left + ptr) // 2
        if (isoform[mid][1] < query[0][0]):
            left = mid;
        else:
            ptr = mid;

    endptr = ptr
    while endptr != len(isoform) and isoform[endptr][0] <= query[-1][1]:
        endptr += 1

    isoform = isoform[ptr:endptr]
    
    seg_coverage = intersection(isoform, query)
    outseg_coverage = intersection(get_dual(isoform), get_dual(query))

    return Fraction(2, 3) * Fraction(seg_coverage, total_len(query)) \
        +  Fraction(1, 3) * Fraction(outseg_coverage, total_len(get_dual(query)))


def check(reply_txt):
    if reply_txt == CONFIG['secret']:
        return 1.0, "you dirty hacker"

    reply = [int(tok) for tok in reply_txt.strip().split('\n')]

    with test_file() as inp, jury_ans_file() as ans:
        n, delta = map(int, inp.readline().split())

        isoforms = []
        for i in range(n):
            isoforms.append(parse_line(inp.readline()))
        q = int(inp.readline())
        if len(reply) != q:
            return 0.0, "Expected %d lines, your answer has %d" % (q, len(reply))

        total = 0.
        num_better = 0
        num_same = 0
        num_worse = 0
        for i in range(q):
            query = parse_line(inp.readline())
            
            if reply[i] < 0 or reply[i] >= n:
                return 0.0, "Format error, all numbers should be in range [%d, %d], but on line %d your output is %d" \
                    % (0, n - 1, i + 1, reply[i])

            if CONFIG['use_score_file']:
                jury_score = Fraction(ans.readline().strip())
            else:
                jury_reply = int(ans.readline())
                jury_score = match_score(isoforms[jury_reply], query)
            part_score = match_score(isoforms[reply[i]], query)

            if PRINT_SCORE_MODE:
                print(str(part_score), file=sys.stderr)
            
            total += min(float(part_score / jury_score), 1.0)
            if part_score < jury_score:
                num_worse += 1
            elif part_score == jury_score:
                num_same += 1
            else:
                num_better += 1

        msg_parts = []
        if num_worse:
            msg_parts.append("worse than jury's in %d reads" % num_worse)
        if num_same:
            msg_parts.append("equivalent to jury's in %d reads" % num_same)
        if num_better:
            msg_parts.append("better than jury's in %d reads" % num_better)
        
        return total/q, f"partial scoring used, your score is {'%.5f' % (total/q)}; your solution is {', '.join(msg_parts)}"


def solve():
    if CONFIG['use_score_file']:
        return CONFIG['secret']
    
    with jury_ans_file() as fp:
        return fp.read()


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['print_score']:
        PRINT_SCORE_MODE = True
    
    print(*check(sys.stdin.read()))
