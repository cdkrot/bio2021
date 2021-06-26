import requests, zipfile, io
from requests.adapters import HTTPAdapter
import os


CONFIG = {
    'use_network': True,
    'url': 'https://stepik.org/media/attachments/lesson/541857/secret.zip',
    'zip_password': 'LMQ8UrFb8fjbSD1AdutA',
    'test_name': '10-welcome'
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


def check(reply_txt):
    reply = [list(map(int, tok.split())) for tok in reply_txt.strip().split('\n')]
    jury_reply = []
    
    with jury_ans_file() as ans:
        for line in ans:
            jury_reply.append(list(map(int, line.split())))

    if len(jury_reply) != len(reply):
        return 0.0, "Expected %d lines, your answer has %d" % (len(jury_reply), len(reply))

    if jury_reply == reply:
        return 1.0, "Correct"
    else:
        return 0.0, "Incorrect"
    

def solve():
    with jury_ans_file() as fp:
        return fp.read()


if __name__ == '__main__':
    import sys
    print(*check(sys.stdin.read()))
