#!/usr/bin/python3

import sys, subprocess, os, time

count = int(sys.argv[1])
stdin = sys.argv[2]

file_names = ['out_%02d' % i for i in range(count)]
files = [open(file_names[i], 'w') for i in range(count)]

processes = [subprocess.Popen(sys.argv[3:] + [str(count), str(i)], stdin=open(stdin), stdout=files[i]) for i in range(count)]

alarm = []

while True:
    time.sleep(3)

    has_proc = False
    for i in range(count):
        if processes[i] is not None:
            has_proc = True

            if processes[i].poll() is not None:
                print(f"Proc {i} terminated with {processes[i].returncode}")
                if processes[i].returncode:
                    alarm.append(f"Proc {i} terminated with {processes[i].returncode}")
                processes[i] = None

    if not has_proc:
        break

print(*alarm)
with open('result', 'w') as fp:
    for f in file_names:
        with open(f, 'r') as src:
            fp.write(src.read())
