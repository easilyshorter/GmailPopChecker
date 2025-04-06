#!/bin/bash

cd "$(dirname "$0")"
DATE=$(date +%Y%m%d)
LOG_DIR="./log/$DATE"
mkdir -p "$LOG_DIR"

FILES=("check.log" "geckodriver.log" "service_error.log")
for file in "${FILES[@]}"; do
    SRC="./log/$file"
    if [ -f "$SRC" ]; then
        mv "$SRC" "$LOG_DIR/"
        touch "$SRC"
    fi
done

find ./log -maxdepth 1 -type d -name "20*" -mtime +30 -exec rm -rf {} \;
