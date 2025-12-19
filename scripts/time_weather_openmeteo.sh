#!/bin/bash

# Toggle file
STATE_FILE="/tmp/waybar_timeweather_state"

# Boston coordinates
LAT="42.3601"
LON="-71.0589"

# API endpoint (Open-Meteo: no key required)
API_URL="https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}&current_weather=true&hourly=precipitation_probability"

# Function to show time/date
get_time() {
    date "+%A, %b %d • %I:%M %p"
}

# Function to show weather
get_weather() {
    weather_json=$(curl -sf "$API_URL")
    [ -z "$weather_json" ] && echo "N/A" && return

    # Get current temperature (°F)
    temp_c=$(echo "$weather_json" | jq '.current_weather.temperature')
    temp_f=$(awk "BEGIN {printf \"%.0f\", ($temp_c * 9/5) + 32}")

    # Get precipitation probability for current hour
    current_hour=$(date -u +"%Y-%m-%dT%H:00")
    prob=$(echo "$weather_json" | jq -r --arg t "$current_hour" '
      (.hourly.time | index($t)) as $idx |
      if $idx != null then .hourly.precipitation_probability[$idx]
      else 0 end
    ')

    echo "${temp_f}°F • ${prob}% rain"
}

# Toggle logic
if [[ "$1" == "toggle" ]]; then
    if [[ ! -f $STATE_FILE ]]; then
        echo "weather" > "$STATE_FILE"
    elif grep -q "weather" "$STATE_FILE"; then
        echo "time" > "$STATE_FILE"
    else
        echo "weather" > "$STATE_FILE"
    fi
    exit 0
fi

# Display based on state
if [[ ! -f $STATE_FILE ]] || grep -q "time" "$STATE_FILE"; then
    get_time
else
    get_weather
fi
