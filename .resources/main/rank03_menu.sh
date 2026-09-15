#!/bin/bash

source colors.sh

clear

printf "${CYAN}%s${RESET}\n" "╔═══════════════════════════════════════════════════════════╗"
printf "${BLUE}%s${GREEN}%s${BLUE}%s${RESET}\n" "║" "              📄 EXAM RANK 03                              " "║"
printf "${CYAN}%s${RESET}\n" "╚═══════════════════════════════════════════════════════════╝"

printf "${YELLOW}${BOLD}%s${RESET}\n" "1. Practice Mode"
printf "${YELLOW}${BOLD}%s${RESET}\n" "2. Real Exam Mode"
printf "${YELLOW}${BOLD}%s${RESET}\n" "3. Back to Main Menu"

printf "${GREEN}${BOLD}Enter your choice (1-2): ${RESET}"

read rank03_opt

case $rank03_opt in
    1)
        bash rank03.sh
        ;;
    2)
        bash rank03_real_mode.sh
        ;;
    3)
        bash intro.sh
        ;;
    *)
        echo "Invalid choice. Please enter 1 or 2."
        sleep 1
        bash rank03_menu.sh
        ;;
esac