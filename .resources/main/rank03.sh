#!/bin/bash

source functions.sh
source colors.sh
source cleanup.sh
trap cleanup_exam_files INT TERM

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

    1)
        bash rank03_base.sh alternate_case
        ;;
    2)
        bash rank03_base.sh atoi
        ;;
    3)
        bash rank03_base.sh brackets
        ;;
    4)
        bash rank03_base.sh capitalize_words
        ;;
    5)
        bash rank03_base.sh convert_base
        ;;
    6)
        bash rank03_base.sh customSortString
        ;;
    7)
        bash rank03_base.sh merge_and_sort_desc
        ;;
    8)
        bash rank03_base.sh mirror_matrix
        ;;
    9)
        bash rank03_base.sh mirror_matrix_vertical
        ;;
    10)
        bash rank03_base.sh py_echo_validator
        ;;
    11)
        bash rank03_base.sh py_pattern_tracker
        ;;
    12)
        bash rank03_base.sh rotate_90
        ;;
    13)
        bash rank03_base.sh sorted
        ;;
    14)
        bash rank03_base.sh topKFrequent
        ;;
    15)
        bash rank03_base.sh twoSum
        ;;
    16)
        bash rank03_base.sh valid_anagram
        ;;
    17)
        bash rank03_base.sh whisper_lipher
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