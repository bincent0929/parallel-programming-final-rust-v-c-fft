#!/bin/bash

LANG_ARG="$1"
MACH_DIR_ARG="$2" # for different hardware
RUN_COUNT_ARG="${3:-5}"
FULL_DIR="./test-output/${MACH_DIR_ARG}"
mkdir -p "${FULL_DIR}"
mkdir -p "${FULL_DIR}/rust_lang"
mkdir -p "${FULL_DIR}/C_lang"

THREAD_COUNT_VALUES=("1" "4" "8")

for N in "${THREAD_COUNT_VALUES[@]}"; do
    if [ "$LANG_ARG" = "rust" ]; then
        THREAD_COUNT=$N cargo run --release -p rust-fft
        OUTPUT="${FULL_DIR}/rust_lang/rust_benchmark_results_t${N}.txt"
        > "$OUTPUT"
    elif [ "$LANG_ARG" = "C" ]; then
        cd c-fft/
        make clean
        make THREAD_COUNT=$N
        CMD="./fft_t$N"
        cd ..
        OUTPUT="${FULL_DIR}/C_lang/C_benchmark_results_t${N}.txt"
        > "$OUTPUT"
    fi

    echo "thread_count = $N" >> "$OUTPUT"
    echo "" >> "$OUTPUT"

    for j in $(seq 1 "$RUN_COUNT_ARG"); do
        echo "Run $j:" >> "$OUTPUT"
        { time "$CMD"; } >> "$OUTPUT" 2>&1
        echo "" >> "$OUTPUT"
    done
done
