use std::env;
use std::fs;
use std::path::Path;

fn main() {
    /*
     * Takes the bash environment variable and saves it to
     * n as a string.
     */
    let thread_count = env::var("THREAD_COUNT").unwrap_or_else(|_| "4".to_string());
    // This is directory reference is standard for Rust compilation
    // in this case it'll be referenced during compilation of main.rs
    let out_dir = env::var("OUT_DIR").unwrap();
    // This saves the N value to a constants file that
    // the main program can reference as it's being compiled.
    let dest = Path::new(&out_dir).join("constants.rs");
    fs::write(dest, format!("const THREAD_COUNT: usize = {};\n", thread_count)).unwrap();
    println!("cargo:rerun-if-env-changed=THREAD_COUNT");
}
