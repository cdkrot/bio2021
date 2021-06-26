#!/usr/bin/python3

import random
import copy
import sys
random.seed(31031999)


class TestData:
    def __init__(self, isoforms=[], delta=0, queries=[]):
        self.isoforms = copy.deepcopy(isoforms)
        self.delta = delta
        self.queries = copy.deepcopy(queries)
        self.proposed_answer = []

    def save(self, file_path, anspath=None):
        with open(file_path, "w") as fp:
            print(len(self.isoforms), self.delta, file=fp)
            for iso in self.isoforms:
                print(",".join("%d-%d" % (a, b) for (a, b) in iso), file=fp)
            
            print(len(self.queries), file=fp)
            for quer in self.queries:
                print(",".join("%d-%d" % (a, b) for (a, b) in quer), file=fp)

        if anspath:
            with open(anspath, "w") as fp:
                for ans in self.proposed_answer:
                    print(ans, file=fp)
        print(f"Saved {file_path} {', ' + anspath if anspath else ''}")

    def copy(self):
        return TestData(self,
                        isoforms=copy.deepcopy(self.isoforms),
                        delta=self.delta,
                        queries=self.queries)

    def _parse_line(self, line):
        toks = line.split(',')
        pairs = map(lambda x: tuple(map(int, x.split('-'))), toks)
        return list(pairs)

    def load_isoforms_list(self, file_path):
        res = []
        with open(file_path) as fp:
            for line in fp:
                res.append(self._parse_line(line))
        return res
    
    def load(self, file_path, load_delta=True, load_queries=True):
        with open(file_path) as fp:
            toks = fp.readline().split()

            n = int(toks[0])
            if load_delta:
                self.delta = int(toks[1])

            self.isoforms = []
            self.queries = []
            
            for i in range(n):
                self.isoforms.append(self._parse_line(fp.readline().strip()))

            if load_queries:
                q = int(fp.readline())

                for i in range(q):
                    self.queries.append(self._parse_line(fp.readline().strip()))

    def shuffle(self):
        if not self.proposed_answer:
            random.shuffle(self.isoforms)
            random.shuffle(self.queries)
        else:
            perm = list(range(len(self.isoforms)))
            random.shuffle(perm)
            invperm = [-1 for i in range(len(self.isoforms))]

            for (i, pi) in enumerate(perm):
                invperm[pi] = i

            newisoforms = [self.isoforms[pi] for pi in perm]
            self.isoforms = newisoforms

            tmp = list(zip(self.queries, self.proposed_answer))
            random.shuffle(tmp)

            self.queries = [val[0] for val in tmp]
            self.proposed_answer = [invperm[val[1]] for val in tmp]

    def add_from(self, other):
        orig_isoform_count = len(self.isoforms)
        
        for iso in other.isoforms:
            self.isoforms.append(copy.deepcopy(iso))
        for que in other.queries:
            self.queries.append(copy.deepcopy(que))

        for jans in other.proposed_answer:
            self.proposed_answer.append(orig_isoform_count + jans)

class ConstDistribution:
    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value

class UniformDistribution:
    def __init__(self, l, r):
        self.l = l
        self.r = r

    def __call__(self):
        return random.randint(self.l, self.r)

class Distribution:
    def __init__(self):
        self.cumulative_weight = [0]
        self.parts = []

    def add(self, weight, distr):
        self.cumulative_weight.append(self.cumulative_weight[-1] + weight)
        self.parts.append(distr)
        return self
        
    def add_const(self, weight, value):
        return self.add(weight, ConstDistribution(value))

    def add_uniform(self, weight, l, r):
        return self.add(weight, UniformDistribution(l, r))
    
    def __call__(self):
        weight = random.randint(0, self.cumulative_weight[-1] - 1)

        ptr = 0
        while weight >= self.cumulative_weight[ptr + 1]:
            ptr += 1

        return self.parts[ptr]()

# def bio_make_test(test_name, source):
#     print(f"Generating {test_name} from {source}")
#     test = TestData()
#     test.load('./bio/mouse.txt', load_queries=False)
#     test.queries = test.load_isoforms_list(f'./bio/examples_clean/{source}')
#     test.save('todo')

def generate_test_based_on(testbase, num_queries, delta, len_distr_func, noise_dist_dist, shrink_dist, skip_filtering=False, pdrop_segm=0):
    test = TestData(delta=delta)
    for isoform in testbase.isoforms:
        min_gap = 10 ** 1000

        if not skip_filtering:
            for (a, b) in isoform:
                min_gap = min(min_gap, b - a)
            for ((_, b), (ap, _)) in zip(isoform, isoform[1:]):
                min_gap = min(min_gap, ap - b)

            if min_gap < 2 * delta + 1:
                continue
        test.isoforms.append(isoform)

    for i in range(num_queries):
        jans = random.randint(0, len(test.isoforms) - 1)
        base = test.isoforms[jans]

        the_len = min(len(base), len_distr_func(len(base))())
        ind_start = UniformDistribution(0, len(base) - the_len)()

        noise_dist = noise_dist_dist()
        res = []
        
        min_st = 0
        for (a, b) in base[ind_start:ind_start+the_len]:
            if UniformDistribution(0, 100)() < pdrop_segm and the_len >= 3:
                the_len -= 1
            else:
                a = max(min_st, a + noise_dist())
                b = max(a + 1, b + noise_dist())
                min_st = b + 1
                res.append((a, b))

        res[0] = (min(res[0][1] - 1, res[0][0] + shrink_dist()), res[0][1])
        res[-1] = (res[-1][0], max(res[-1][0] + 1, res[-1][1] - shrink_dist()))

        test.queries.append(res)
        test.proposed_answer.append(jans)

    return test


def gen_simple(num_isoforms, num_queries, delta, start_distr, len_distr, qlen_distr_func, ingap_distr, outgap_distr, noise_dist_dist, shrink_dist, pdrop_segm=0):
    test = TestData()

    for i in range(num_isoforms):
        next_start = start_distr()

        isoform = []
        for i in range(len_distr()):
            end = next_start + ingap_distr()
            isoform.append((next_start, end))

            next_start = end + outgap_distr()

        test.isoforms.append(isoform)

    return generate_test_based_on(test, num_queries, delta, len_distr_func=qlen_distr_func,
                                                            noise_dist_dist=noise_dist_dist,
                                                            shrink_dist=shrink_dist,
                                                            skip_filtering=True, pdrop_segm=pdrop_segm)


def gen_evil_base(num_isoforms, dictionary_size, yesno_dist_func, step_distr, in_distr, minor_noise_dist_dist):
    dictionary = []

    start = 10000
    for i in range(dictionary_size):
        end = start + in_distr()
        dictionary.append((start, end))

        start = end + step_distr()

    test = TestData()
    for i in range(num_isoforms):
        isoform = []
        for (ind, seg) in enumerate(dictionary):
            minor_noise_dist = minor_noise_dist_dist()
            if yesno_dist_func(ind)():
                (a, b) = seg
                a += minor_noise_dist()
                b += minor_noise_dist()
                isoform.append((a, b))

        test.isoforms.append(isoform)

    return test


def gen_evil_base2(num_isoforms):
    test = TestData(delta=100)

    dictionary = []

    step_distr = UniformDistribution(5000, 10000)
    in_distr = UniformDistribution(700, 1200)
    
    start = 10000
    end2 = -1
    bigskip = int(1e5)
    
    for i in range(4):
        end = start + in_distr()
        dictionary.append((start, end))

        if i == 1:
            end2 = end
            start = end + bigskip
        else:
            start = end + step_distr()

    noise_dist_dist = Distribution().add_const(98, UniformDistribution(-30, +30)) \
                                    .add_const(1, UniformDistribution(-70, -40)) \
                                    .add_const(1, UniformDistribution(+40, +70))
            
    for i in range(num_isoforms):
        noise_dist = noise_dist_dist()
        iso = []
        for (a, b) in dictionary[0:2]:
            iso.append((a + noise_dist(), b + noise_dist()))

        if UniformDistribution(0, 9) == 7:
            seglen = UniformDistribution(201, bigskip - 220)()
            segst = end2 + UniformDistribution(400, bigskip - seglen - 400)()
            
            iso.append((segst, segst + seglen))
        else:
            A, B, seglen = -1, -1, int(1e9)

            while abs(A - B) <= seglen + 200:
                seglen = UniformDistribution(205, 500)()
                
                A = end2 + UniformDistribution(400, bigskip - seglen - 400)()
                B = end2 + UniformDistribution(400, bigskip - seglen - 400)()

            if A > B:
                A, B = B, A
            iso.append((A, A + seglen))
            iso.append((B, B + seglen))

        for (a, b) in dictionary[2:4]:
            iso.append((a + noise_dist(), b + noise_dist()))        

        for (a, b) in iso:
            if b - a <= 200:
                print(iso)
                raise
        for ((_, b), (a, _)) in zip(iso, iso[1:]):
            if a - b <= 200:
                print(iso)
                raise
            
        test.isoforms.append(iso)
    return test

def testgen_main():
    random.seed(31031999)
    gen_simple(4, 5,
               delta=100,
               start_distr=UniformDistribution(0, 5000),
               len_distr=UniformDistribution(3, 7),
               qlen_distr_func=lambda x: UniformDistribution(3, 7),
               ingap_distr=UniformDistribution(250, 400),
               outgap_distr=UniformDistribution(400, 800),
               noise_dist_dist=Distribution().add_const(80, UniformDistribution(-90, +90)) \
                                             .add_const(20, Distribution()\
                                                            .add_uniform(80, -90, 90) \
                                                            .add_uniform(10, -110, -101) \
                                                            .add_uniform(10, +101, +110)),
               shrink_dist=UniformDistribution(0, 150),
               ).save('tests/10-welcome.txt')

    # Mouse inexact
    mouse = TestData()
    mouse.load('bio/mouse.txt', load_delta=False, load_queries=False)
    mouse.isoforms = [isoform for isoform in mouse.isoforms if len(isoform) >= 2]
    generate_test_based_on(mouse, 14500, delta=20,
                           len_distr_func=lambda cnt: UniformDistribution(2, cnt),
                           noise_dist_dist=Distribution() \
                                           .add_const(45, UniformDistribution(-20, +20)) \
                                           .add_const(45, UniformDistribution(-10, +10)) \
                                           .add_const(10, Distribution()\
                                                          .add_uniform(80, -20, 20) \
                                                          .add_uniform(10, -25, -21) \
                                                          .add_uniform(10, +21, +25)),
                           shrink_dist=UniformDistribution(0, 10)
                           ).save('tests/35-mouse-inexact.txt')


    # Huge evil test
    prob = lambda pr: Distribution().add_const(pr, True).add_const(100 - pr, False)

    def yesno_dist_func(i):
        i = min(i, 19 - i)
        if i in [0, 1, 2, 3, 4]:
            return prob(97)
        if i in [5, 6]:
            return prob(70)
        if i in [7, 8]:
            return prob(60)
        return prob(50)
    
    evil = gen_evil_base(50000, 27, yesno_dist_func, UniformDistribution(5000, 10000),
                         UniformDistribution(700, 1200),
                         Distribution().add_const(98, UniformDistribution(-30, +30)) \
                                       .add_const(1, UniformDistribution(-70, -40))
                                       .add_const(1, UniformDistribution(+40, +70)))

    generate_test_based_on(evil, 50000, delta=100, len_distr_func=lambda x: ConstDistribution(14),
                           noise_dist_dist=Distribution().add_const(45, UniformDistribution(-23, +23)) \
                                                         .add_const(30, ConstDistribution(0)) \
                                                         .add_const(35, UniformDistribution(-10, +10)),
                           shrink_dist=UniformDistribution(0, 5)).save('tests/55-huge-inexact.txt')


    evil2 = gen_evil_base2(500000)
    evil2 = \
    generate_test_based_on(evil2, 500000, delta=100, len_distr_func=lambda x: UniformDistribution(3, 4),
                       noise_dist_dist=Distribution().add_const(45, UniformDistribution(-23, +23)) \
                                                     .add_const(30, ConstDistribution(0)) \
                                                     .add_const(35, UniformDistribution(-10, +10)),
                       shrink_dist=UniformDistribution(0, 5))

    longguys = gen_simple(4, 50000,
               delta=100,
               start_distr=UniformDistribution(0, 5000),
               len_distr=UniformDistribution(int(1e4), int(1e5)),
               qlen_distr_func=lambda x: Distribution().add_uniform(90, 2, 5) \
                                                       .add_uniform(10, 2, 50),
               ingap_distr=UniformDistribution(500, 600),
               outgap_distr=UniformDistribution(1000, 2500),
               noise_dist_dist=Distribution().add_const(80, UniformDistribution(-90, +90)) \
                                             .add_const(20, Distribution()\
                                                            .add_uniform(80, -90, 90) \
                                                            .add_uniform(10, -110, -101) \
                                                            .add_uniform(10, +101, +110)),
               shrink_dist=UniformDistribution(0, 150))

    trivia = gen_simple(100, 1000,
               delta=100,
               start_distr=UniformDistribution(0, 5000),
               len_distr=UniformDistribution(3, 10),
               qlen_distr_func=lambda x: UniformDistribution(3, min(x, 7)),
               ingap_distr=UniformDistribution(int(1e3), int(1e4)),
               outgap_distr=UniformDistribution(int(1e5), int(2e6)),
               noise_dist_dist=Distribution().add_const(80, UniformDistribution(-90, +90)) \
                                             .add_const(20, Distribution()\
                                                            .add_uniform(80, -90, 90) \
                                                            .add_uniform(10, -110, -101) \
                                                            .add_uniform(10, +101, +110)),
               shrink_dist=UniformDistribution(0, 150))

    evil2.add_from(longguys)
    evil2.add_from(trivia)
    evil2.proposed_answer = []
    evil2.shuffle()    
    evil2.save('tests/60-huge-inexact.txt')

    ##############################################

    # Begin approx part

    #############################################

    t70 = TestData()

    for (n, q, delta) in [(3000, 5000, 100), (3000, 5000, 20)]:
        t70.add_from(
            gen_simple(n, q,
                       delta=delta,
                       start_distr=UniformDistribution(0, 5000),
                       len_distr=UniformDistribution(3, 15),
                       qlen_distr_func=lambda x: UniformDistribution(3, 7),
                       ingap_distr=UniformDistribution(250, 400),
                       outgap_distr=UniformDistribution(400, 800),
                       noise_dist_dist=Distribution().add_const(80, UniformDistribution(-90, +90)) \
                       .add_const(20, Distribution()\
                                  .add_uniform(80, -90, 90) \
                                  .add_uniform(10, -110, -101) \
                                  .add_uniform(10, +101, +110)),
                       shrink_dist=UniformDistribution(0, 150),
                       )
        )
        
    t70.add_from(gen_simple(1, 30, delta=5,
                            start_distr=UniformDistribution(0, 5000),
                            len_distr=ConstDistribution(1000),
                            qlen_distr_func=lambda x: UniformDistribution(2, 10),
                            ingap_distr=UniformDistribution(int(1e5), int(1e6)),
                            outgap_distr=UniformDistribution(20, 100),
                            noise_dist_dist=ConstDistribution(UniformDistribution(-2, +2)),
                            shrink_dist=UniformDistribution(0, 100)))

    t70.shuffle()
    t70.delta = 0
    t70.save('tests/70-welcome-approx.txt', 'tests/70-welcome-approx.jans')
    
    #####

    for (n, q, testname) in [(190000, 190000, '80-big-approx'), (300000, 600000, '90-huge-approx')]:    
        evil2 = gen_evil_base2(n)
        evil2 = \
        generate_test_based_on(evil2, q, delta=0, len_distr_func=lambda x: UniformDistribution(3, 4),
                           noise_dist_dist=Distribution().add_const(45, UniformDistribution(-23, +23)) \
                                                         .add_const(30, ConstDistribution(0)) \
                                                         .add_const(35, UniformDistribution(-10, +10)),
                           shrink_dist=UniformDistribution(0, 5))

        for i in range(n//1000):
            que_ind = random.randint(0, len(evil2.queries) - 1)
            sub_ind = random.randint(0, len(evil2.queries[que_ind]) - 1)

            A = evil2.queries[que_ind][sub_ind][0]
            B = evil2.queries[que_ind][sub_ind][1]
            if B - A >= 12:
                hole = (B - A) // 10
                hole_st = random.randint(A + 1, B - hole - 1)

                evil2.queries[que_ind] = evil2.queries[que_ind][:sub_ind] + [(A, hole_st), (hole_st + hole, B)] + \
                    evil2.queries[que_ind][sub_ind+1:]

        longguys = gen_simple(4, q//10,
                   delta=100,
                   start_distr=UniformDistribution(0, 5000),
                   len_distr=UniformDistribution(int(1e4), int(1e5)),
                   qlen_distr_func=lambda x: Distribution().add_uniform(90, 2, 5) \
                                                           .add_uniform(10, 2, 50),
                   ingap_distr=UniformDistribution(500, 600),
                   outgap_distr=UniformDistribution(1000, 2500),
                   noise_dist_dist=Distribution().add_const(80, UniformDistribution(-90, +90)) \
                                                 .add_const(20, Distribution()\
                                                                .add_uniform(80, -90, 90) \
                                                                .add_uniform(10, -110, -101) \
                                                                .add_uniform(10, +101, +110)),
                    shrink_dist=UniformDistribution(0, 150), pdrop_segm=1)

        trivia = gen_simple(100, 1000,
                   delta=100,
                   start_distr=UniformDistribution(0, 5000),
                   len_distr=UniformDistribution(3, 10),
                   qlen_distr_func=lambda x: UniformDistribution(3, min(x, 7)),
                   ingap_distr=UniformDistribution(int(1e3), int(1e4)),
                   outgap_distr=UniformDistribution(int(1e5), int(2e6)),
                   noise_dist_dist=Distribution().add_const(80, UniformDistribution(-90, +90)) \
                                                 .add_const(20, Distribution()\
                                                                .add_uniform(80, -90, 90) \
                                                                .add_uniform(10, -110, -101) \
                                                                .add_uniform(10, +101, +110)),
                    shrink_dist=UniformDistribution(0, 150),
                    pdrop_segm=1)

        trivia1000 = gen_simple(50, 500,
           delta=1000,
           start_distr=UniformDistribution(0, 50000),
           len_distr=UniformDistribution(3, 20),
           qlen_distr_func=lambda x: UniformDistribution(3, min(x, 10)),
           ingap_distr=UniformDistribution(int(3e3), int(1e4)),
           outgap_distr=UniformDistribution(int(3e5), int(6e6)),
           noise_dist_dist=Distribution().add_const(80, UniformDistribution(-90, +90)) \
                                         .add_const(20, Distribution()\
                                                        .add_uniform(80, -90, 90) \
                                                        .add_uniform(10, -110, -101) \
                                                        .add_uniform(10, +101, +110)),
                                shrink_dist=UniformDistribution(0, 150),  pdrop_segm=1)

        trivia0 = gen_simple(71, 523,
           delta=0,
           start_distr=UniformDistribution(0, 5000),
           len_distr=UniformDistribution(3, 20),
           qlen_distr_func=lambda x: UniformDistribution(3, min(x, 10)),
           ingap_distr=UniformDistribution(20, 90),
           outgap_distr=UniformDistribution(int(3e5), int(6e6)),
           noise_dist_dist=ConstDistribution(UniformDistribution(-2, +2)),
                             shrink_dist=UniformDistribution(0, 150), pdrop_segm=2)

        dense = gen_simple(1, 30, delta=5,
                            len_distr=ConstDistribution(1000),
                            start_distr=UniformDistribution(0, 5000),
                            qlen_distr_func=lambda x: UniformDistribution(2, 10),
                            ingap_distr=UniformDistribution(int(1e5), int(1e6)),
                            outgap_distr=UniformDistribution(20, 100),
                            noise_dist_dist=ConstDistribution(UniformDistribution(-2, +2)),
                            shrink_dist=UniformDistribution(0, 100))

        minievil = gen_evil_base(n // 20, 27, yesno_dist_func, UniformDistribution(5000, 10000),
                                 UniformDistribution(700, 1200),
                                 Distribution().add_const(98, UniformDistribution(-30, +30)) \
                                       .add_const(1, UniformDistribution(-70, -40))
                                       .add_const(1, UniformDistribution(+40, +70)))

        minievil = generate_test_based_on(minievil, n // 20, delta=200, len_distr_func=lambda x: UniformDistribution(3, 4),
                       noise_dist_dist=Distribution().add_const(45, UniformDistribution(-23, +23)) \
                                                     .add_const(30, ConstDistribution(0)) \
                                                     .add_const(35, UniformDistribution(-10, +10)),
                                          shrink_dist=UniformDistribution(0, 5), pdrop_segm=1)
        
        
        evil2.add_from(longguys)
        evil2.add_from(trivia)
        evil2.add_from(trivia1000)
        evil2.add_from(trivia0)
        evil2.add_from(dense)
        evil2.add_from(minievil)
        evil2.shuffle()
        evil2.delta = 0
        evil2.save(f'tests/{testname}.txt', f'tests/{testname}.jans')
    
def teststat_main(testlist):
    for path in testlist:
        bytecount = 0
        
        with open(f'{path}') as fp:
            bytecount = len(fp.read())

        bytecount_str = ('%.1fKB' % (bytecount / 1000)
                         if bytecount <= 100 * 1000
                         else '%.1fMB' % (bytecount / 1e6))
        
        test = TestData()
        test.load(f'{path}')

        print(f"{path}: {len(test.isoforms)} {test.delta} {len(test.queries)} {bytecount_str}")
        

if __name__ == '__main__':
    if sys.argv[1:] == ['tests']:
        testgen_main()
    elif sys.argv[1] == 'stat':
        teststat_main(sys.argv[2:])
