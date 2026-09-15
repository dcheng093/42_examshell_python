#!/bin/bash

source functions.sh
source colors.sh
source cleanup.sh
trap cleanup_exam_files INT TERM

QUESTIONS=(
    alternate_case
    atoi
    brackets
    capitalize_words
    convert_base
    customSortString
    merge_and_sort_desc
    mirror_matrix
    mirror_matrix_vertical
    py_echo_validator
    py_pattern_tracker
    rotate_90
    sorted
    topKFrequent
    twoSum
    valid_anagram
    whisper_lipher
)

run_practice_questions() {
    local start_index=$1
    local index
    local status

    for ((index = start_index; index < ${#QUESTIONS[@]}; index++)); do
        bash rank03_base.sh "${QUESTIONS[$index]}"
        status=$?

        if [ "$status" -ne 2 ]; then
            return "$status"
        fi
    done

    bash rank03_menu.sh
}

clear

bash label.sh

printf "${BLUE}%s${RESET}\n" "┌─────────────────────────────────────────────────────────┐"
printf "${BLUE}%s${GREEN}%s${BLUE}%s${RESET}\n" "│" "          🎯 Exam 42 Rank 03 Practice 🎯                 " "│"
printf "${BLUE}%s${RESET}\n" "└─────────────────────────────────────────────────────────┘"

printf "${CYAN}%s${RESET}\n" "∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼"

printf "${YELLOW}${BOLD}%s${RESET}\n" "1. alternate_case"
printf "${YELLOW}${BOLD}%s${RESET}\n" "2. atoi"
printf "${YELLOW}${BOLD}%s${RESET}\n" "3. brackets"
printf "${YELLOW}${BOLD}%s${RESET}\n" "4. capitalize_words"
printf "${YELLOW}${BOLD}%s${RESET}\n" "5. convert_base"
printf "${YELLOW}${BOLD}%s${RESET}\n" "6. customSortString"
printf "${YELLOW}${BOLD}%s${RESET}\n" "7. merge_and_sort_desc"
printf "${YELLOW}${BOLD}%s${RESET}\n" "8. mirror_matrix"
printf "${YELLOW}${BOLD}%s${RESET}\n" "9. mirror_matrix_vertical"
printf "${YELLOW}${BOLD}%s${RESET}\n" "10. py_echo_validator"
printf "${YELLOW}${BOLD}%s${RESET}\n" "11. py_pattern_tracker"
printf "${YELLOW}${BOLD}%s${RESET}\n" "12. rotate_90"
printf "${YELLOW}${BOLD}%s${RESET}\n" "13. sorted"
printf "${YELLOW}${BOLD}%s${RESET}\n" "14. topKFrequent"
printf "${YELLOW}${BOLD}%s${RESET}\n" "15. twoSum"
printf "${YELLOW}${BOLD}%s${RESET}\n" "16. valid_anagram"
printf "${YELLOW}${BOLD}%s${RESET}\n" "17. whisper_lipher"

printf "${CYAN}%s${RESET}\n" "∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼"

printf "${GREEN}${BOLD}Enter your choice (1-17): ${RESET}"

read opt

case $opt in
    menu)
        bash rank03_menu.sh
        ;;

    1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17)
        run_practice_questions "$((opt - 1))"
        ;;

    exit)
        cleanup_exam_files
        cd ../../../../
        clear
        exit
        ;;

    *)
        echo "$(tput setaf 1)Wrong input$(tput sgr0)"
        sleep 1
        bash rank03.sh
        ;;
esac