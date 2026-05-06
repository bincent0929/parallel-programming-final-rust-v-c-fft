#!/bin/bash

LANG_ARG="$1"
DIR_ARG="$2"
FULL_DIR="./test-output/${DIR_ARG}"
mkdir -p ${FULL_DIR}
mkdir -p ${FULL_DIR}/rust_lang
mkdir -p ${FULL_DIR}/C_lang

N_VALUES=("1000000000" "10000000000" "100000000000")
TEST_NUMBERS=("1" "2" "3")

for i in "${!N_VALUES[@]}"; do
    N="${N_VALUES[$i]}"
    TEST_NUMBER="${TEST_NUMBERS[$i]}"

    if [ "$LANG_ARG" = "rust" ]; then
        N_VALUE=$N cargo build --release
        CMD="./target/release/final-project-main"
        OUTPUT="${FULL_DIR}/rust_lang/rust_benchmark_results${TEST_NUMBER}.txt"
        > "$OUTPUT"
    elif [ "$LANG_ARG" = "C" ]; then
        make clean
        make N_VALUE=$N
        CMD="./trap"
        OUTPUT="${FULL_DIR}/C_lang/C_benchmark_results${TEST_NUMBER}.txt"
        > "$OUTPUT"
    fi

    echo "n = $N" >> "$OUTPUT"
    echo "" >> "$OUTPUT"

    for j in $(seq 1 5); do
        echo "Run $j:" >> "$OUTPUT"
        { time $CMD; } >> "$OUTPUT" 2>&1
        echo "" >> "$OUTPUT"
    done
done
