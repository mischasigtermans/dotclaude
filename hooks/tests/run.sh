#!/usr/bin/env bash
# Feeds fake hook payloads through each hook and asserts on the JSON it prints.
set -u
HOOKS="$(cd "$(dirname "$0")/.." && pwd)"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
fail=0

check() {
  local name=$1 hook=$2 payload=$3 expect=$4
  local out
  out=$(printf '%s' "$payload" | $hook 2>/dev/null)
  if [ "$expect" = "silent" ]; then
    [ -z "$out" ] && echo "ok   $name" || { echo "FAIL $name: expected no output, got $out"; fail=1; }
  else
    grep -q -- "$expect" <<<"$out" && echo "ok   $name" || { echo "FAIL $name: expected '$expect', got '$out'"; fail=1; }
  fi
}

bash_payload() { jq -cn --arg c "$1" '{tool_name:"Bash",tool_input:{command:$c}}'; }
file_payload() { jq -cn --arg p "$1" --arg t "$2" '{session_id:"test",transcript_path:"'"$TMP"'/t.jsonl",tool_name:"Write",tool_input:{file_path:$p,content:$t}}'; }

G="python3 $HOOKS/bash-guard.py"
check "guard: add -A"            "$G" "$(bash_payload 'git add -A')" '"deny"'
check "guard: add ."             "$G" "$(bash_payload 'cd x && git add . && git commit -m wip')" '"deny"'
check "guard: add pathspec"      "$G" "$(bash_payload 'git add app/Models/User.php')" silent
check "guard: commit -am"        "$G" "$(bash_payload 'git commit -am "fix"')" '"deny"'
check "guard: commit pathspec"   "$G" "$(bash_payload 'git commit -m "Fix login" -- app/Http')" silent
check "guard: trailer"           "$G" "$(bash_payload $'git commit -m "Fix\n\nCo-Authored-By: Claude"')" 'trailer'
check "guard: signoff"           "$G" "$(bash_payload 'git commit -s -m x -- a')" 'trailer'
check "guard: no-verify"         "$G" "$(bash_payload 'git commit --no-verify -m x -- a')" 'no-verify'
check "guard: hooksPath"         "$G" "$(bash_payload 'git -c core.hooksPath=/dev/null commit -m x -- a')" 'hooksPath'
check "guard: tag create"        "$G" "$(bash_payload 'git tag v1.2.0')" '"deny"'
check "guard: tag list"          "$G" "$(bash_payload 'git tag -l')" silent
check "guard: tag bare"          "$G" "$(bash_payload 'git tag')" silent
check "guard: pint dirty"        "$G" "$(bash_payload 'vendor/bin/pint --dirty --format agent')" '"deny"'
check "guard: pint blade"         "$G" "$(bash_payload 'vendor/bin/pint --blade resources/views/a.blade.php')" '"deny"'
check "guard: pint files"        "$G" "$(bash_payload 'vendor/bin/pint app/Models/User.php')" silent
check "guard: unrelated"         "$G" "$(bash_payload 'ls -la && echo "git add -A"')" silent

C="python3 $HOOKS/config-protect.py"
check "config: pint.json"        "$C" "$(file_payload /p/pint.json '{}')" '"deny"'
check "config: phpstan.neon.dist" "$C" "$(file_payload /p/phpstan.neon.dist x)" '"deny"'
check "config: eslint"           "$C" "$(file_payload /p/eslint.config.js x)" '"deny"'
check "config: model"            "$C" "$(file_payload /p/app/Models/User.php x)" silent

D="python3 $HOOKS/dash-lint.py"
check "dash: blade em dash"      "$D" "$(file_payload /p/resources/views/a.blade.php $'<p>Fast — and cheap</p>')" '"block"'
check "dash: md en dash"         "$D" "$(file_payload /p/README.md $'2019–2021')" '"block"'
check "dash: clean md"           "$D" "$(file_payload /p/README.md 'Fast, and cheap.')" silent
check "dash: php code"           "$D" "$(file_payload /p/app/X.php $'// a — b')" silent
check "dash: memory file"        "$D" "$(file_payload "$HOME/.claude/projects/x/memory/a.md" $'a — b')" silent
check "dot: md middle dot"       "$D" "$(file_payload /p/README.md $'Fast · cheap')" '"block"'
check "dot: lang middle dot"     "$D" "$(file_payload /p/lang/en/app.php $'Fast · cheap')" '"block"'
check "dot: formula in code"     "$D" "$(file_payload /p/README.md 'The formula `v²/(2·decel)` holds.')" silent
check "dot: outside code"        "$D" "$(file_payload /p/README.md 'The formula `v²` holds · always.')" '"block"'
check "dot: blade separator"     "$D" "$(file_payload /p/resources/views/a.blade.php $'<span>·</span>')" silent

# Transcripts: one prompt, then the assistant tool calls given as JSON lines.
transcript() {
  printf '%s\n' '{"type":"user","message":{"content":"do it"}}' > "$TMP/t.jsonl"
  for call in "$@"; do
    printf '{"type":"assistant","message":{"content":[%s]}}\n' "$call" >> "$TMP/t.jsonl"
  done
}
stop_payload() { jq -cn --argjson a "${1:-false}" '{session_id:"test",transcript_path:"'"$TMP"'/t.jsonl",hook_event_name:"Stop",stop_hook_active:$a}'; }
words() { python3 -c "print(' '.join(['word']*$1))"; }

S="python3 $HOOKS/sharpen-gate.py"
transcript "$(jq -cn --arg t "$(words 200)" '{type:"tool_use",name:"Write",input:{file_path:"/p/README.md",content:$t}}')"
check "sharpen: long README"     "$S" "$(stop_payload)" '"block"'
check "sharpen: already active"  "$S" "$(stop_payload true)" silent
transcript "$(jq -cn --arg t "$(words 200)" '{type:"tool_use",name:"Write",input:{file_path:"/p/README.md",content:$t}}')" '{"type":"tool_use","name":"Skill","input":{"skill":"sharpen"}}'
check "sharpen: ran already"     "$S" "$(stop_payload)" silent
transcript "$(jq -cn --arg t "$(words 60)" '{type:"tool_use",name:"Write",input:{file_path:"/p/README.md",content:$t}}')"
check "sharpen: short"           "$S" "$(stop_payload)" silent
transcript "$(jq -cn --arg t "$(words 200)" '{type:"tool_use",name:"Write",input:{file_path:"/p/skills/x/SKILL.md",content:$t}}')"
check "sharpen: SKILL.md"        "$S" "$(stop_payload)" silent
transcript "$(jq -cn --arg t "$(words 200)" '{type:"tool_use",name:"mcp__macuse__mail_compose_message",input:{body:$t}}')"
check "sharpen: mail draft"      "$S" "$(stop_payload)" '"block"'

U="python3 $HOOKS/ui-gate.py"
ui_payload() { jq -cn --arg s "$1" --arg p "$2" '{session_id:$s,transcript_path:"'"$TMP"'/t.jsonl",tool_name:"Edit",tool_input:{file_path:$p}}'; }
transcript '{"type":"tool_use","name":"Bash","input":{"command":"cat index.html"}}'
check "ui: edit without Read"    "$U" "$(ui_payload "ui-$$-a" /p/index.html)" 'Mobile-first'
check "ui: second edit passes"   "$U" "$(ui_payload "ui-$$-a" /p/index.html)" silent
transcript '{"type":"tool_use","name":"Read","input":{"file_path":"/p/resources/views/a.blade.php"}}'
check "ui: rule already loaded"  "$U" "$(ui_payload "ui-$$-b" /p/resources/views/a.blade.php)" silent
check "ui: boost guideline"      "$U" "$(ui_payload "ui-$$-d" /p/.ai/guidelines/pint/core.blade.php)" silent
check "ui: php file"             "$U" "$(ui_payload "ui-$$-c" /p/app/X.php)" silent
rm -f "${TMPDIR:-/tmp}"/claude-ui-gate/ui-$$-*

P="python3 $HOOKS/php-format.py"
mkdir -p "$TMP/proj/vendor/bin" "$TMP/proj/app"
printf '#!/bin/sh\necho "$@" > %s/pint-args\n' "$TMP" > "$TMP/proj/vendor/bin/pint"; chmod +x "$TMP/proj/vendor/bin/pint"
echo '<?php' > "$TMP/proj/app/X.php"
post=$(jq -cn --arg p "$TMP/proj/app/X.php" '{session_id:"php-'$$'",hook_event_name:"PostToolUse",tool_input:{file_path:$p}}')
check "php: record edit"         "$P" "$post" silent
check "php: stop runs pint"      "$P" "$(jq -cn '{session_id:"php-'$$'",hook_event_name:"Stop",stop_hook_active:false}')" silent
grep -q "app/X.php" "$TMP/pint-args" 2>/dev/null && echo "ok   php: pint got the file" || { echo "FAIL php: pint got the file"; fail=1; }
blade_post=$(jq -cn --arg p "$TMP/proj/resources/views/a.blade.php" '{session_id:"blade-'$$'",hook_event_name:"PostToolUse",tool_input:{file_path:$p}}')
check "php: blade not recorded"  "$P" "$blade_post" silent
[ ! -f "${TMPDIR:-/tmp}/claude-php-format/blade-$$.txt" ] && echo "ok   php: blade left alone" || { echo "FAIL php: blade left alone"; fail=1; }

M="python3 $HOOKS/memory-gate.py"
MEM="$HOME/.claude/projects/-p/memory"
mem_payload() { jq -cn --arg p "$1" --arg t "$2" --arg c "${3:-$TMP}" '{cwd:$c,tool_name:"Write",tool_input:{file_path:$p,content:$t}}'; }
fm() { printf -- '---\nname: x\ndescription: x\nmetadata:\n  type: %s\n---\n\n%s\n' "$1" "$2"; }
mkdir -p "$TMP/boost/.ai/guidelines" "$TMP/plain"
check "mem: feedback denied"       "$M" "$(mem_payload "$MEM/a.md" "$(fm feedback 'Always ask first.')" "$TMP/plain")" 'CLAUDE.md'
check "mem: feedback boost"        "$M" "$(mem_payload "$MEM/a.md" "$(fm feedback 'Always ask first.')" "$TMP/boost")" 'boost:update'
check "mem: project status"        "$M" "$(mem_payload "$MEM/b.md" "$(fm project 'Branch is uncommitted, next steps below.')")" '"deny"'
check "mem: project fact"          "$M" "$(mem_payload "$MEM/b.md" "$(fm project 'Prod runs on Forge server pxl-nl.')")" silent
check "mem: todo reference"        "$M" "$(mem_payload "$MEM/b.md" "$(fm project 'The plan lives in Solo todo 288; all pending migrations ran clean.')")" silent
check "mem: user fact"             "$M" "$(mem_payload "$MEM/c.md" "$(fm user 'Works in Dutch.')")" silent
check "mem: index"                 "$M" "$(mem_payload "$MEM/MEMORY.md" '- [a](a.md) pending')" silent
check "mem: not a memory dir"      "$M" "$(mem_payload /p/docs/a.md "$(fm feedback 'x')")" silent

R="bash $HOOKS/rtk-rewrite.sh"
if command -v rtk >/dev/null; then
  check "rtk: rewrites git status" "$R" "$(bash_payload 'git status')" 'rtk'
fi

exit $fail
