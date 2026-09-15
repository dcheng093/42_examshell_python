#!/bin/bash

cleanup_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

cleanup_exam_files() {
    rm -rf "$cleanup_root/rendu"
    find "$cleanup_root" -type d -name __pycache__ -prune -exec rm -rf {} +
    find "$cleanup_root" -type f \( -name '*.pyc' -o -name 'tester_output.log' \) -delete
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    cleanup_exam_files
fi