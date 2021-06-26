import requests, zipfile, io
from requests.adapters import HTTPAdapter
import os


CONFIG = {
    'use_network': True,
    'url': 'https://stepik.org/media/attachments/lesson/541857/secret.zip',
    'zip_password': 'LMQ8UrFb8fjbSD1AdutA',
    'test_name': '00-sample'
}


def filestream(name):
    s = requests.Session()
    s.mount(CONFIG['url'], HTTPAdapter(max_retries=6))
    request = s.get(CONFIG['url'])

    zfile = zipfile.ZipFile(io.BytesIO(request.content))
    fp = zfile.open(name, 'r', bytes(CONFIG['zip_password'], encoding='utf8'))

    return io.TextIOWrapper(fp, encoding='utf8')


def test_file():
    if CONFIG['use_network']:
        return filestream(CONFIG['test_name'] + '.txt')
    else:
        return open(os.environ['test'])


def jury_ans_file():
    if CONFIG['use_network']:
        return filestream(CONFIG['test_name'] + '.ans')
    return open(os.environ['test_ans'])


def parse_line(line):
    toks = line.split(',')
    pairs = map(lambda x: tuple(map(int, x.split('-'))), toks)
    return list(pairs)


def is_equal(a, b, delta):
    return abs(a - b) <= delta


def is_le(a, b, delta):
    return is_equal(a, b, delta) or a < b


def is_ge(a, b, delta):
    return is_le(b, a, delta)


def is_same(pairA, pairB, delta):
    return is_equal(pairA[0], pairB[0], delta) and is_equal(pairA[1], pairB[1], delta)


def is_matched(isoform, query, delta):
    left = -1
    ptr = len(isoform)

    while ptr - left > 1:
        mid = (left + ptr) // 2
        if is_ge(isoform[mid][1], query[0][1], delta):
            ptr = mid
        else:
            left = mid

    if ptr + len(query) - 1 >= len(isoform):
        return False
    
    if not is_le(isoform[ptr][0], query[0][0], delta) or \
       not is_equal(isoform[ptr][1], query[0][1], delta):
        return False
    
    for t in range(1, len(query) - 1):
        if not is_same(isoform[ptr + t], query[t], delta):
            return False

    if not is_equal(isoform[ptr + len(query) - 1][0], query[-1][0], delta) or \
       not is_ge(isoform[ptr + len(query) - 1][1], query[-1][1], delta):
        return False

    return True


def check(reply_txt):
    reply = [int(tok) for tok in reply_txt.strip().split('\n')]
    
    with test_file() as inp, jury_ans_file() as ans:
        n, delta = map(int, inp.readline().split())

        isoforms = []
        for i in range(n):
            isoforms.append(parse_line(inp.readline()))

        q = int(inp.readline())
        if len(reply) != q:
            return 0.0, "Expected %d lines, your answer has %d" % (q, len(reply))

        fails = 0
        jerror = None

        for i in range(q):
            query = parse_line(inp.readline())
            jury_reply = int(ans.readline())
            
            if reply[i] < -1 or reply[i] >= n:
                return 0.0, "Format error, all numbers should be in range [%d, %d], but on line %d your output is %d" \
                    % (-1, n - 1, i + 1, reply[i])

            if jury_reply != -1:
                if not is_matched(isoforms[jury_reply], query, delta):
                    raise RuntimeError("Jury fail on line %d" % (i + 1))
            
            if reply[i] != -1 and not is_matched(isoforms[reply[i]], query, delta):
                fails += 1
            elif (jury_reply == -1) != (reply[i] == -1):
                if jury_reply == -1:
                    if jerror is None:
                        jerror = ("Please report to us: Jury fail on line %d (proposed answer is %d)" % (i + 1, reply[i]))
                else:
                    fails += 1

        if jerror is not None:
            return 0.5, jerror
        if fails == 0: 
            return 1, "Correct answer"
        else:
            return 0, "Incorrect answer"
    

def solve():
    with jury_ans_file() as fp:
        return fp.read()


if __name__ == '__main__':
    import sys
    print(*check(sys.stdin.read()))
