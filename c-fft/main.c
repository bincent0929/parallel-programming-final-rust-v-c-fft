#include <fftw3.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define PI 3.14159265358979323846

int main(void) {
    double sample_rate = 44100.0;
    double freq = 440.0;
    size_t fft_size = 1 << 26;

    /* generate sine wave */
    float *samples = malloc(fft_size * sizeof(float));
    if (!samples) {
        fprintf(stderr, "malloc failed\n");
        return 1;
    }
    for (size_t i = 0; i < fft_size; i++) {
        samples[i] = sinf(2.0f * (float)PI * (float)freq * (float)i / (float)sample_rate);
    }

    /* pack into complex buffer */
    fftwf_complex *buf = fftwf_malloc(fft_size * sizeof(fftwf_complex));
    if (!buf) {
        fprintf(stderr, "fftwf_malloc failed\n");
        free(samples);
        return 1;
    }
    for (size_t i = 0; i < fft_size; i++) {
        buf[i][0] = samples[i];
        buf[i][1] = 0.0f;
    }
    free(samples);

    /* FFT */
    fftwf_plan plan = fftwf_plan_dft_1d((int)fft_size, buf, buf,
                                         FFTW_FORWARD, FFTW_ESTIMATE);
    fftwf_execute(plan);

    /* magnitudes (first half only) */
    size_t num_bins = fft_size / 2 + 1;
    float *magnitudes = malloc(num_bins * sizeof(float));
    if (!magnitudes) {
        fprintf(stderr, "malloc failed\n");
        fftwf_destroy_plan(plan);
        fftwf_free(buf);
        return 1;
    }
    for (size_t i = 0; i < num_bins; i++) {
        float re = buf[i][0];
        float im = buf[i][1];
        magnitudes[i] = sqrtf(re * re + im * im);
    }

    /* find peak */
    size_t peak_bin = 0;
    float peak_mag = 0.0f;
    for (size_t i = 0; i < num_bins; i++) {
        if (magnitudes[i] > peak_mag) {
            peak_mag = magnitudes[i];
            peak_bin = i;
        }
    }

    float bin_width = (float)sample_rate / (float)fft_size;
    printf("Bin width: %.2f Hz\n", bin_width);
    printf("Peak at bin %zu = %.2f Hz\n", peak_bin, (float)peak_bin * bin_width);
    printf("Expected:    %.2f Hz\n", (float)freq);
    printf("Magnitude:   %.4f\n", peak_mag);

    fftwf_destroy_plan(plan);
    fftwf_free(buf);
    free(magnitudes);
    return 0;
}
