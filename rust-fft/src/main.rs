use rustfft::{num_complex::Complex, FftPlanner};
use std::f32::consts::PI;
use std::thread;

include!(concat!(env!("OUT_DIR"), "/constants.rs"));

fn main() {
    //let sample_rate = 44100.0; // CD quality sampling
    let sample_rate = 192000.0; // Studio master quality sampling
    let freq = 440.0; // A4
    let fft_size = 1 << 26;
    let chunk_size = (fft_size + THREAD_COUNT - 1) / THREAD_COUNT;

    // Generate samples — parallel
    let mut samples = vec![0.0f32; fft_size];
    thread::scope(|s| {
        let mut handles = vec![];
        for (t, slice) in samples.chunks_mut(chunk_size).enumerate() {
            let start = t * chunk_size;
            handles.push(s.spawn(move || {
                for (i, sample) in slice.iter_mut().enumerate() {
                    *sample = (2.0 * PI * freq * (start + i) as f32 / sample_rate).sin();
                }
            }));
        }
        for h in handles {
            h.join().unwrap();
        }
    });

    // Pack into complex buffer — parallel
    let mut buffer: Vec<Complex<f32>> = vec![Complex::new(0.0, 0.0); fft_size];
    thread::scope(|s| {
        let mut handles = vec![];
        for (buf_slice, samp_slice) in
            buffer.chunks_mut(chunk_size).zip(samples.chunks(chunk_size))
        {
            handles.push(s.spawn(move || {
                for (b, &s_val) in buf_slice.iter_mut().zip(samp_slice.iter()) {
                    *b = Complex::new(s_val, 0.0);
                }
            }));
        }
        for h in handles {
            h.join().unwrap();
        }
    });

    // FFT — plan once, each thread FFTs its chunk using the same plan
    let mut planner = FftPlanner::new();
    let fft = planner.plan_fft_forward(chunk_size);
    let bin_width = sample_rate / chunk_size as f32;

    let (peak_bin, peak_mag) = thread::scope(|s| {
        let mut handles = vec![];
        for chunk in buffer.chunks_mut(chunk_size) {
            let fft = fft.clone();
            handles.push(s.spawn(move || {
                fft.process(chunk);
                chunk[..chunk.len() / 2 + 1]
                    .iter()
                    .enumerate()
                    .max_by(|(_, a), (_, b)| a.norm().partial_cmp(&b.norm()).unwrap())
                    .map(|(i, c)| (i, c.norm()))
                    .unwrap()
            }));
        }
        handles
            .into_iter()
            .map(|h| h.join().unwrap())
            .max_by(|(_, a), (_, b)| a.partial_cmp(b).unwrap())
            .unwrap()
    });

    println!("Bin width: {:.2} Hz", bin_width);
    println!("Peak at bin {} = {:.2} Hz", peak_bin, peak_bin as f32 * bin_width);
    println!("Expected:    {:.2} Hz", freq);
    println!("Magnitude:   {:.4}", peak_mag);
}
