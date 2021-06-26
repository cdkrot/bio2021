all: SOLUTIONS TESTS TESTS_VAL

SOLUTIONS: solutions/baseline.bin solutions/baseline-worse.bin solutions/thinice_brute.bin solutions/baseline-approx.bin

solutions/%.bin: solutions/%.cpp
	compile $< $(patsubst %.cpp, %.bin, $<)
	ocompile $< $(patsubst %.cpp, %.optbin, $<)

val: val.cpp
	compile val.cpp

util/cleanify.bin: util/cleanify.cpp
	compile $< $(patsubst %.cpp, %.bin, $<)

clean:
	rm solutions/*.bin
	rm val
	rm util/cleanify.bin

TESTS: ./util/bio_make_tests.sh bio/ util/cleanify.bin util/testgen.py
	echo "Please don't modify the tests" >/dev/null
	echo '(ignored)' ./util/bio_make_tests.sh >/dev/null >/dev/null
	echo '(ignored)' ./util/testgen.py tests >/dev/null

TESTS_VAL: TESTS val tests/*
	./util/run_test_val.sh

secret.zip: tests/*
	cd tests && zip -e -P LMQ8UrFb8fjbSD1AdutA ../secret.zip *.ans *.txt

public.7z: tests/*
	rm -f public.7z
	cd tests && 7z a ../public.7z *.txt
#	# cd tests && zip -9 ../public.zip *.txt -x 60-huge-inexact.txt
#	# cd tests && zip -9 ../public2.zip 60-huge-inexact.txt
