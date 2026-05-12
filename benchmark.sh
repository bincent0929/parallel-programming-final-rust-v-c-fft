#!/bin/bash

LANG_ARG="$1" # rust or C
MACH_DIR_ARG="$2" # the name for the machine you're testing on
RUN_COUNT_ARG="${3:-5}" # how many runs you want to do
FULL_DIR="./test-output/${MACH_DIR_ARG}"
mkdir -p "${FULL_DIR}"

THREAD_COUNT_VALUES=("1" "4" "8")

for N in "${THREAD_COUNT_VALUES[@]}"; do
    if [ "$LANG_ARG" = "rust" ]; then
        THREAD_COUNT=$N cargo build --release -p rust-fft
        CMD="./target/release/rust-fft"
        OUTPUT="${FULL_DIR}/rust_lang/rust_benchmark_results_t${N}.txt"
        mkdir -p "$(dirname "$OUTPUT")" && > "$OUTPUT"
    elif [ "$LANG_ARG" = "C" ]; then
        make -C c-fft/ THREAD_COUNT=$N
        CMD="./c-fft/fft_t$N"
        OUTPUT="${FULL_DIR}/C_lang/C_benchmark_results_t${N}.txt"
        mkdir -p "$(dirname "$OUTPUT")" && > "$OUTPUT"
    fi

    echo "thread_count = $N" >> "$OUTPUT"
    echo "" >> "$OUTPUT"

    for j in $(seq 1 "$RUN_COUNT_ARG"); do
        echo "Run $j:" >> "$OUTPUT"
        { time "$CMD"; } >> "$OUTPUT" 2>&1
        echo "" >> "$OUTPUT"
    done
done
