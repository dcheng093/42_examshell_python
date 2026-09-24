source colors.sh
source cleanup.sh
trap cleanup_exam_files EXIT INT TERM
mkdir ../../rendu
clear
bash label.sh
printf "${CYAN}%s${RESET}\n" "╔═══════════════════════════════════════════════════════════╗"
printf "${BLUE}%s${GREEN}%s${BLUE}%s${RESET}\n" "║" "    ⚡ EXAM 42 PRACTICE TEST - MAIN MENU ⚡                " "║"
printf "${CYAN}%s${RESET}\n" "╠═══════════════════════════════════════════════════════════╣"
printf "${BLUE}%s${RESET}\n" " ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
printf "${GREEN}%s${RESET}\n"  "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆"
printf "${YELLOW}${BOLD}%s${RESET}\n" "🔄 1. Commands"
printf "${YELLOW}${BOLD}%s${RESET}\n" "🚀 2. Exam Rank 02"
printf "${YELLOW}${BOLD}%s${RESET}\n" "📋 3. Exam Rank 03"
printf "${YELLOW}${BOLD}%s${RESET}\n" "📁 4. Open Rendu Folder"
printf "${YELLOW}${BOLD}%s${RESET}\n" "5. Update ExamShell"
printf "${GREEN}%s${RESET}\n"  "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆"
printf "${BLUE}%s${RESET}\n" " ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
printf "${CYAN}%s${RESET}\n" "╚═══════════════════════════════════════════════════════════╝"
printf "${GREEN}${BOLD}Enter your choice (1-5): ${RESET}"
read opt
case $opt in
    1)
        bash help.sh
        ;;
    2)
        bash rank02_menu.sh
        ;;
    3)
        bash rank03_menu.sh
        ;;
    4)
        cd ../../rendu
        open .
        cd ../.resources/main
        bash menu.sh
        exit 1
        ;;
    5)
        cd ../../
        bash update.sh
        ;;
    
    exit)
        cd ../../../../
        rm -rf rendu
        clear
        exit 0
        ;;
    
    *)
        echo "Invalid choice. Please enter a number from 1 to 5."
        sleep 1
        clear
        bash menu.sh
esac
