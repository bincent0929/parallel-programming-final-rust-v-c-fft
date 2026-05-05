CC = gcc
THREAD_COUNT ?= 4
CFLAGS = -Wall -O2 -fopenmp -DTHREAD_COUNT=$(THREAD_COUNT)
LDFLAGS = -lfftw3f -lfftw3f_threads -lm -fopenmp

TARGET = fft_t$(THREAD_COUNT)

.PHONY: clean

$(TARGET): main.c
	$(CC) $(CFLAGS) -o $(TARGET) main.c $(LDFLAGS)

clean:
	rm -f fft_t*

