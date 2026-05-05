CC = gcc
THREAD_COUNT ?= 4
CFLAGS = -Wall -O2 -fopenmp -DTHREAD_COUNT=$(THREAD_COUNT)
LDFLAGS = -lfftw3f -lfftw3f_threads -lm -fopenmp

.PHONY: clean

fft: main.c
	$(CC) $(CFLAGS) -o fft main.c $(LDFLAGS)

clean:
	rm -f fft

