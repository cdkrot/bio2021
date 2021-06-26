#!/usr/bin/python3

import sys, subprocess

count = int(sys.argv[1])
stdin = sys.argv[2]

file_names = ['out_%02d' % i for i in range(count)]
files = [open(file_names[i], 'w') for i in range(count)]

processes = [subprocess.Popen(sys.argv[3:] + [str(count), str(i)], stdin=open(stdin), stdout=files[i]) for i in range(count)]

while True:
    os.sleep(10)

    has_proc = False
    for i in range(count):
        if processed[i] is not None:
            has_proc = True

            if processes[i].poll() is not None:
                print(f"Proc {i} terminated with {processes[i].returncode}")
                processes[i] = None

    if not has_proc:
        break

with open('result', 'w') as fp:
    for f in files:
        with open(f, 'r') as src:
            fp.write(f.read())
