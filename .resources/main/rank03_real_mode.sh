#!/bin/bash

source functions.sh
source colors.sh
source cleanup.sh
trap cleanup_exam_files INT TERM

base_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

TOTAL_QUESTIONS=6
score=0

prepare_subject() {
    question=$1

    question_dir="$base_dir/../rank03/$question"
    rendu_dir="$base_dir/../../rendu/$question"

    if [ ! -d "$question_dir" ]; then
        echo -e "${RED}Question folder not found: $question_dir${RESET}"
        return 1
    fi

    mkdir -p "$rendu_dir"

    touch "$rendu_dir/$question.py"

    cd "$question_dir" || return 1

    clear

    echo -e "${CYAN}${BOLD}Your subject: $question${RESET}"
    echo "=================================================="
    cat sub.txt
    echo
    echo "=================================================="
    echo -e "${YELLOW}Type 'test' to test your code, 'next' to get a new question, or 'exit' to quit.${RESET}"

    return 0
}

run_question() {
    question=$1

    clear

    echo "$(tput setaf 2)$(tput bold)Question: $question is being prepared...$(tput sgr0)"
    display_animation

    prepare_subject "$question"

    if [ $? -ne 0 ]; then
        return 1
    fi

    while true; do
        read -rp "/> " input

        case "$input" in
            test)
                clear
                echo -e "${GREEN}Running tester.sh...${RESET}"

                output=$(./tester.sh 2>&1)
                echo "$output" | tee tester_output.log

                if echo "$output" | grep -q -E "PASSED|SUCCESS"; then
                    echo
                    echo -e "${GREEN}${BOLD}✔️ Passed!${RESET}"
                    sleep 1
                    return 0
                else
                    echo
                    echo -e "${RED}${BOLD}❌ Failed.${RESET}"
                    echo
                    echo -e "${YELLOW}Your question is still active. Fix your code and try again.${RESET}"
                    echo

                    read -rp "Press Enter to continue..."

                    clear
                    echo -e "${CYAN}${BOLD}Your subject: $question${RESET}"
                    echo "=================================================="
                    cat sub.txt
                    echo
                    echo "=================================================="
                    echo -e "${YELLOW}Type 'test' to test your code, 'next' to get a new question, or 'exit' to quit.${RESET}"
                fi
                ;;

            next)
                echo -e "${BLUE}🔄 Skipping this question...${RESET}"
                sleep 1
                return 2
                ;;

            exit)
                echo "Exiting..."
                cleanup_exam_files
                exit 255
                ;;

            *)
                echo "Please type 'test' to test your code, 'next' to skip, or 'exit' to quit."
                ;;
        esac
    done
}

start_exam() {
    clear
    bash label.sh

    echo "$(tput setaf 2)$(tput bold)🧪 Welcome to the Rank 03 Real Exam!$(tput sgr0)"
    echo "=================================================="
    echo
    echo "You must pass 6 randomly selected questions."
    echo "Questions will not repeat."
    echo
    echo "Questions available: ${#QUESTIONS[@]}"
    echo "Questions required to pass: $TOTAL_QUESTIONS"
    echo

    read -rp "Press Enter to start the exam..."

    remaining=("${QUESTIONS[@]}")

    while [ $score -lt $TOTAL_QUESTIONS ] && [ ${#remaining[@]} -gt 0 ]; do

        random_index=$((RANDOM % ${#remaining[@]}))
        question="${remaining[$random_index]}"

        unset 'remaining[random_index]'
        remaining=("${remaining[@]}")

        result=0

        run_question "$question"
        result=$?

        if [ $result -eq 0 ]; then
            score=$((score + 1))

            echo
            echo "$(tput setaf 2)$(tput bold)✔ Question passed!$(tput sgr0)"
            echo "Current score: $score/$TOTAL_QUESTIONS"

        elif [ $result -eq 2 ]; then
            echo
            echo "$(tput setaf 3)Question skipped.$(tput sgr0)"
            echo "Current score: $score/$TOTAL_QUESTIONS"
        fi

        if [ $result -eq 0 ] && [ $score -lt $TOTAL_QUESTIONS ] && [ ${#remaining[@]} -gt 0 ]; then
            read -rp "Press Enter to continue to the next question..."
        fi
    done

    clear

    if [ $score -ge $TOTAL_QUESTIONS ]; then
        echo "$(tput setaf 2)$(tput bold)🎉 Congratulations! You've passed Rank 03!$(tput sgr0)"
        echo "=================================================="
        echo "Score: $score/$TOTAL_QUESTIONS"
    else
        echo "$(tput setaf 1)$(tput bold)❌ Rank 03 Exam Failed$(tput sgr0)"
        echo "=================================================="
        echo "Score: $score/$TOTAL_QUESTIONS"
        echo
        echo "There are no more questions available."
    fi

    echo
    read -rp "Press Enter to return to the menu..."

    cd "$base_dir" || exit 1
    bash menu.sh
}

start_exam
