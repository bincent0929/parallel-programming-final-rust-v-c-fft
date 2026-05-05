use rustfft::{num_complex::Complex, FftPlanner};
use std::f32::consts::PI;
use std::thread;

fn main() {
    let sample_rate = 44100.0;
    let freq = 440.0;           // A4 note
    let fft_size = 1 << 24; // increase these to decrease bin size and thereby precision

    // Generate 4096 samples of a 440 Hz sine wave
    let samples: Vec<f32> = (0..fft_size)
        .map(|i| (2.0 * PI * freq * i as f32 / sample_rate).sin())
        .collect();

    // Pack into complex buffer
    let mut buffer: Vec<Complex<f32>> = samples
        .iter()
        .map(|&s| Complex::new(s, 0.0))
        .collect();

    // FFT
    let mut planner = FftPlanner::new();
    let fft = planner.plan_fft_forward(fft_size);
    fft.process(&mut buffer);

    // Magnitudes (first half only — rest is mirror)
    let bin_width = sample_rate / fft_size as f32;
    let num_bins = fft_size / 2 + 1;
    let magnitudes: Vec<f32> = buffer[..num_bins]
        .iter()
        .map(|c| c.norm())
        .collect();

    // Find peak
    // the magnitudes are based on the magnitude of sin()
    // which in this case is 1.0 and the fft_size / 2
    // so for fft_size = 4096 then the peak should be around
    // 2048
    let (peak_bin, peak_mag) = magnitudes
        .iter()
        .enumerate()
        .max_by(|(_, a), (_, b)| a.partial_cmp(b).unwrap())
        .unwrap();

    println!("Bin width: {:.2} Hz", bin_width);
    println!("Peak at bin {} = {:.2} Hz", peak_bin, peak_bin as f32 * bin_width);
    println!("Expected:    {:.2} Hz", freq);
    println!("Magnitude:   {:.4}", peak_mag);
}
