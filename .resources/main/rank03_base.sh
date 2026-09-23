#!/bin/bash

source colors.sh
source cleanup.sh
trap cleanup_exam_files INT TERM

base_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rank_dir="$base_dir/../rank03"
question="$1"

if [ -z "$question" ] || [ ! -d "$rank_dir/$question" ]; then
    echo "Unknown Rank 03 question: $question"
    exit 1
fi

rendu_dir="$base_dir/../../rendu/$question"
candidate="$rendu_dir/$question.py"
mkdir -p "$rendu_dir"
touch "$candidate"

cd "$rank_dir/$question" || exit 1
subject=$(cat sub.txt)

while true; do
    clear
    printf "%s\n\n" "$subject"
    printf "Type 'test' to run all tests, 'next' to skip, or 'exit' to quit.\n\n"
    read -r -p "/> " input

    case "$input" in
        test)
            clear
            timeout 5s ./tester.sh
            status=$?
            echo
            if [ "$status" -eq 0 ]; then
                printf "${GREEN}${BOLD}✔️  Passed!${RESET}\n"
            elif [ "$status" -eq 124 ]; then
                printf "${RED}${BOLD}Timed out. It can be because of infinite loop ∞${RESET}\n"
            else
                printf "${RED}${BOLD}Failed.${RESET}\n"
            fi
            read -r -p "Press Enter to continue." enter
            ;;
        next)
            exit 2
            ;;
        menu)
            cd "$base_dir/../../" || exit 1
            bash .resources/main/rank03_menu.sh
            exit $?
            ;;
        exit)
            cleanup_exam_files
            exit 0
            ;;
        *)
            echo "Please type 'test', 'next', 'menu', or 'exit'."
            ;;
    esac
done