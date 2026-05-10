#!/bin/bash

input=$(cat)
git_info=$(echo "$input" | bash ~/.claude/statusline-command.sh)
context_pct=$(echo "$input" | npx ccstatusline 2>/dev/null | sed 's/\x1b\[[0-9;]*m//g; s/ //g; s/%//')
pct_num=${context_pct%%.*}

if [[ $pct_num =~ ^[0-9]+$ ]] && (( pct_num >= 80 )); then
  context_display=$'\033[1;38;2;204;139;137m'"${pct_num}%"$'\033[0m'
else
  context_display="${pct_num}%"
fi

printf '%s · %s' "$git_info" "$context_display"
