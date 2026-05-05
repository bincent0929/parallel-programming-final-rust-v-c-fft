CC = gcc
CFLAGS = -Wall -O2
LDFLAGS = -lfftw3f -lm -fopenmp

.PHONY: clean

fft: main.c
	$(CC) $(CFLAGS) -o fft main.c $(LDFLAGS)

clean:
	rm -f fft

