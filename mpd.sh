#!/bin/bash

if ! mpc status &>/dev/null; then
    echo '{"text":"<span foreground=\"#5c6370\">🔇 MPD Off</span>","class":"stopped"}'
    exit 0
fi

state=$(mpc status | awk 'NR==2 {print $1}' | tr -d '[]')
artist=$(mpc current -f "%artist%" 2>/dev/null | head -1)
title=$(mpc current -f "%title%" 2>/dev/null | head -1)
album=$(mpc current -f "%album%" 2>/dev/null | head -1)
elapsed=$(mpc status | grep -oP '\d+:\d+/\d+:\d+' | cut -d'/' -f1)

if [ -z "$artist" ]; then
    file=$(mpc current -f "%file%" 2>/dev/null | head -1)
    artist=$(basename "$file" | sed 's/\..*$//')
fi

# Colors (you can customize these)
state_color="#ff6b6b"
artist_color="#51afef"
title_color="#c678dd"
album_color="#98c379"
time_color="#abb2bf"
paused_color="#f2392cb"

case "$state" in
    "playing")
        state_icon="▶"
        class="playing"
        text="<span foreground='$state_color'>$state_icon</span> <span foreground='$artist_color'>${artist:0:15}</span> - <span foreground='$title_color'>${title:0:20}</span> | <span foreground='$time_color'>${elapsed:-0:00}</span>"
        ;;
    "paused")
        state_icon="⏸"
        class="paused"
        text="<span foreground='$paused_color'>$state_icon</span> <span foreground='$artist_color'>${artist:0:15}</span> - <span foreground='$title_color'>${title:0:20}</span> | <span foreground='$time_color'>${elapsed:-0:00}</span>"
        ;;
    *)
        state_icon="⏹"
        class="stopped"
        text="<span foreground='#e06c75'>$state_icon Stopped</span>"
        ;;
esac

# Create colored tooltip
tooltip="<b>MPD</b>
<span foreground='$artist_color'><b>Artist:</b></span> ${artist:-Unknown}
<span foreground='$title_color'><b>Title:</b></span> ${title:-Unknown}
<span foreground='$album_color'><b>Album:</b></span> ${album:-Unknown}
<span foreground='$time_color'><b>Time:</b></span> ${elapsed:-0:00}"

echo "{\"text\":\"$text\", \"class\":\"$class\", \"tooltip\":\"$tooltip\", \"escape\": false}"

