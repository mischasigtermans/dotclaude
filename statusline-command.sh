#!/bin/bash

input=$(cat)
cwd=$(echo "$input" | sed -n 's/.*"current_dir":"\([^"]*\)".*/\1/p')
cwd_display=${cwd/#$HOME/\~}

if git -C "$cwd" rev-parse --git-dir &>/dev/null; then
  repo_name=${cwd##*/}
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null) || \
  branch=$(git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
  uncommitted=$(git -C "$cwd" --no-optional-locks status --porcelain 2>/dev/null | wc -l)

  if (( uncommitted > 0 )); then
    printf '%s · %s · %d↑' "$repo_name" "$branch" "$uncommitted"
  else
    printf '%s · %s' "$repo_name" "$branch"
  fi
else
  printf '%s' "$cwd_display"
fi
