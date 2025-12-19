#!/bin/bash

# Show MPD controls menu
echo -e "Play/Pause\nStop\nNext\nPrevious\nOpen Player" | rofi -dmenu -p "MPD Controls" | {
    read choice
    case "$choice" in
        "Play/Pause") mpc toggle ;;
        "Stop") mpc stop ;;
        "Next") mpc next ;;
        "Previous") mpc prev ;;
        "Open Player") ncmpcpp || kitty -e ncmpcpp ;;
    esac
}
