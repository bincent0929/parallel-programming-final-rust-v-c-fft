CC = gcc
THREAD_COUNT ?= 4
CFLAGS = -Wall -Ofast -fopenmp -DTHREAD_COUNT=$(THREAD_COUNT)
LDFLAGS = -lfftw3f_omp -lfftw3f -lm -fopenmp

TARGET = fft_t$(THREAD_COUNT)

.PHONY: clean

$(TARGET): main.c
	$(CC) $(CFLAGS) -o $(TARGET) main.c $(LDFLAGS)

clean:
	rm -f fft_t*

