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
  local status=$?
  if [ $status -ne 0 ]; then
    echo "FAIL $name: the hook exited $status"; fail=1
  elif [ "$expect" = "silent" ]; then
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
check "guard: add -A as a dry run" "$G" "$(bash_payload 'git add -A --dry-run')" silent
check "guard: add -n ."          "$G" "$(bash_payload 'git add -n .')" silent
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
check "guard: pkill pest"        "$G" "$(bash_payload 'pkill -f pest')" 'PID'
check "guard: killall phpunit"   "$G" "$(bash_payload 'cd app && killall -9 phpunit')" '"deny"'
check "guard: pkill artisan test" "$G" "$(bash_payload 'pkill -f "artisan test"')" '"deny"'
check "guard: kill by pid"       "$G" "$(bash_payload 'kill 48213')" silent
check "guard: pkill other"       "$G" "$(bash_payload 'pkill -f vite')" silent
check "guard: pkill queue worker" "$G" "$(bash_payload 'pkill -f "artisan queue:work"')" silent
check "guard: herd secure"       "$G" "$(bash_payload 'herd secure mysite')" 'Herd app'
check "guard: herd links"        "$G" "$(bash_payload 'herd links')" silent

check "guard: newline commands" "$G" "$(bash_payload $'git status\ngit add -A')" '"deny"'
check "guard: absolute git" "$G" "$(bash_payload '/usr/bin/git add -A')" '"deny"'
check "guard: absolute pkill" "$G" "$(bash_payload '/usr/bin/pkill -f pest')" '"deny"'
check "guard: echo arguments" "$G" "$(bash_payload 'echo git add -A')" silent
check "guard: echo trailer" "$G" "$(bash_payload 'echo git commit Co-Authored-By')" silent
check "guard: quoted newline" "$G" "$(bash_payload $'printf "git status\ngit add -A"')" silent
check "guard: env wrapper" "$G" "$(bash_payload 'env LANG=C /usr/bin/git add -A')" '"deny"'
check "guard: command wrapper" "$G" "$(bash_payload 'command git add -A')" '"deny"'
check "guard: then keyword" "$G" "$(bash_payload 'if true; then git add -A; fi')" '"deny"'
check "guard: do keyword" "$G" "$(bash_payload 'for f in a; do git commit -am x; done')" '"deny"'
check "guard: time prefix" "$G" "$(bash_payload 'time git add -A')" '"deny"'
check "guard: nice prefix" "$G" "$(bash_payload 'nice -n 10 git add .')" '"deny"'
check "guard: timeout prefix" "$G" "$(bash_payload 'timeout 30 git add -A')" '"deny"'
check "guard: brace group" "$G" "$(bash_payload '{ git add -A; }')" '"deny"'
check "guard: negation" "$G" "$(bash_payload '! git add -A')" '"deny"'
check "guard: condition, add by path" "$G" "$(bash_payload 'if git diff --quiet; then git add app/a.php; fi')" silent
check "guard: heredoc trailer" "$G" "$(bash_payload $'git commit -F - -- a <<\'EOF\'\nFix login\n\nCo-Authored-By: Claude\nEOF')" 'trailer'
check "guard: heredoc clean" "$G" "$(bash_payload $'git commit -F - -- a <<\'EOF\'\nFix login\nEOF')" silent
check "guard: heredoc to python" "$G" "$(bash_payload $'python3 - <<\'EOF\'\nprint("x")\ngit add -A\nthen git add -A\nEOF')" silent
check "guard: heredoc to file" "$G" "$(bash_payload $'cat > notes.md <<EOF\ngit add -A\nEOF\nls')" silent
check "guard: heredoc to shell" "$G" "$(bash_payload $'bash <<\'EOF\'\ngit add -A\nEOF')" '"deny"'
check "guard: after a heredoc" "$G" "$(bash_payload $'cat > notes.md <<EOF\nnotes\nEOF\ngit add -A')" '"deny"'
check "guard: here-string" "$G" "$(bash_payload $'grep x <<< hello\ngit add -A')" '"deny"'
check "guard: shift arithmetic" "$G" "$(bash_payload $'echo $((1<<2))\ngit add -A')" '"deny"'
check "guard: heredoc in a string" "$G" "$(bash_payload $'echo "use <<EOF for heredocs"\ngit add -A')" '"deny"'

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
# clauset gives each account a config dir whose projects/ links to ~/.claude/projects.
ACCOUNT="$TMP/.claude-accounts/work"
mkdir -p "$ACCOUNT" && ln -s "$HOME/.claude/projects" "$ACCOUNT/projects"
check "dash: account memory file" "$D" "$(file_payload "$ACCOUNT/projects/x/memory/a.md" $'a — b')" silent
check "dash: panel run file"     "$D" "$(file_payload "$HOME/.panels/site/run/context/probe.md" $'a — b')" silent
check "dash: panel run file in the config dir" "$D" "$(file_payload "$HOME/.claude/panels/site/run/notes/a.md" $'a — b')" silent
check "dot: md middle dot"       "$D" "$(file_payload /p/README.md $'Fast · cheap')" '"block"'
check "dot: lang middle dot"     "$D" "$(file_payload /p/lang/en/app.php $'Fast · cheap')" '"block"'
check "dot: formula in code"     "$D" "$(file_payload /p/README.md 'The formula `v²/(2·decel)` holds.')" silent
check "dot: outside code"        "$D" "$(file_payload /p/README.md 'The formula `v²` holds · always.')" '"block"'
check "dot: blade separator"     "$D" "$(file_payload /p/resources/views/a.blade.php $'<span>·</span>')" silent

# Transcripts: one prompt, then each argument: a tool call, or a line starting with {"type":"user" that goes in whole.
transcript() {
  printf '%s\n' '{"type":"user","message":{"content":"do it"}}' > "$TMP/t.jsonl"
  for call in "$@"; do
    case "$call" in
      '{"type":"user"'*) printf '%s\n' "$call" >> "$TMP/t.jsonl" ;;
      *) printf '{"type":"assistant","message":{"content":[%s]}}\n' "$call" >> "$TMP/t.jsonl" ;;
    esac
  done
}
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
check "mem: feedback denied"       "$M" "$(mem_payload "$MEM/a.md" "$(fm feedback 'Always ask first.')" "$TMP/plain")" 'For this repo: .*plain/CLAUDE.md.*every project'
check "mem: feedback boost"        "$M" "$(mem_payload "$MEM/a.md" "$(fm feedback 'Always ask first.')" "$TMP/boost")" 'boost:update'
check "mem: project status"        "$M" "$(mem_payload "$MEM/b.md" "$(fm project 'Branch is uncommitted, next steps below.')")" '"deny"'
check "mem: project fact"          "$M" "$(mem_payload "$MEM/b.md" "$(fm project 'Prod runs on Forge server web-1.')")" silent
check "mem: todo reference"        "$M" "$(mem_payload "$MEM/b.md" "$(fm project 'The plan lives in Solo todo 288; all pending migrations ran clean.')")" silent
check "mem: user fact"             "$M" "$(mem_payload "$MEM/c.md" "$(fm user 'Works in Dutch.')")" silent
check "mem: index"                 "$M" "$(mem_payload "$MEM/MEMORY.md" '- [a](a.md) pending')" silent
check "mem: not a memory dir"      "$M" "$(mem_payload /p/docs/a.md "$(fm feedback 'x')")" silent
check "mem: account feedback"      "$M" "$(mem_payload "$ACCOUNT/projects/-p/memory/a.md" "$(fm feedback 'Always ask first.')" "$TMP/plain")" '"deny"'

stop_payload() { jq -cn --argjson a "${1:-false}" '{session_id:"test",transcript_path:"'"$TMP"'/t.jsonl",hook_event_name:"Stop",stop_hook_active:$a}'; }
words() { python3 -c "print(' '.join(['word']*$1))"; }
readme() { jq -cn --arg t "$(words "$1")" '{type:"tool_use",name:"Write",input:{file_path:"/p/README.md",content:$t}}'; }
edit() { jq -cn --arg o "$(words "$1")" --arg n "$(words "$2")" '{type:"tool_use",name:"Edit",input:{file_path:"/p/README.md",old_string:$o,new_string:$n}}'; }
SHARPEN='{"type":"tool_use","name":"Skill","input":{"skill":"writing"}}'
NEXT='{"type":"user","message":{"content":"apply it"}}'
META='{"type":"user","isMeta":true,"message":{"content":"[Image: original 390x2600]"}}'

SG="python3 $HOOKS/../skills/writing/hooks/sharpen-gate.py"
transcript "$(readme 200)"
check "sharpen: long README"        "$SG" "$(stop_payload)" '"block"'
check "sharpen: already active"     "$SG" "$(stop_payload true)" silent
transcript "$(readme 200)" "$SHARPEN"
check "sharpen: ran already"        "$SG" "$(stop_payload)" silent
transcript "$(readme 200)" '{"type":"tool_use","name":"Skill","input":{"skill":"sharpen"}}'
check "sharpen: ran under its old name"    "$SG" "$(stop_payload)" silent
transcript "$(readme 200)" '{"type":"tool_use","name":"Skill","input":{"skill":"anthropic-skills:writing"}}'
check "sharpen: ran via claude.ai"  "$SG" "$(stop_payload)" silent
transcript "$(readme 60)"
check "sharpen: short"              "$SG" "$(stop_payload)" silent
transcript "$(jq -cn --arg t "$(words 200)" '{type:"tool_use",name:"Write",input:{file_path:"/p/skills/x/SKILL.md",content:$t}}')"
check "sharpen: SKILL.md"           "$SG" "$(stop_payload)" silent
ELSEWHERE="env CLAUDE_CONFIG_DIR=/home/u/.claude-accounts/work $SG"
transcript "$(jq -cn --arg t "$(words 200)" '{type:"tool_use",name:"Write",input:{file_path:"/home/u/.claude-accounts/work/projects/-p/memory/note.md",content:$t}}')"
check "sharpen: memory under a moved config dir" "$ELSEWHERE" "$(stop_payload)" silent
transcript "$(readme 200)"
check "sharpen: README with a moved config dir" "$ELSEWHERE" "$(stop_payload)" '"block"'
transcript "$(jq -cn --arg t "$(words 200)" '{type:"tool_use",name:"mcp__macuse__mail_compose_message",input:{body:$t}}')"
check "sharpen: mail draft"         "$SG" "$(stop_payload)" silent
transcript "$(readme 200)" "$META"
check "sharpen: meta entry"         "$SG" "$(stop_payload)" '"block"'
transcript "$SHARPEN" "$NEXT" "$(readme 200)"
check "sharpen: previous sharpen is not a blanket exemption" "$SG" "$(stop_payload)" '"block"'
transcript "$SHARPEN" "$(readme 200)"
check "sharpen: prose after sharpen" "$SG" "$(stop_payload)" '"block"'
transcript "$(edit 60 62)" "$(edit 60 62)" "$(edit 60 62)"
check "sharpen: small edits"        "$SG" "$(stop_payload)" silent
transcript "$(edit 10 200)"
check "sharpen: large edit"         "$SG" "$(stop_payload)" '"block"'

transcript "$(jq -cn --arg o "$(words 200)" --arg n "$(python3 -c "print('replacement '*200)")" '{type:"tool_use",name:"Edit",input:{file_path:"/p/README.md",old_string:$o,new_string:$n}}')"
check "sharpen: same length rewrite" "$SG" "$(stop_payload)" '"block"'
transcript "$(edit 200 200)"
check "sharpen: unchanged text" "$SG" "$(stop_payload)" silent

IMAGE='{"type":"user","message":{"content":[{"type":"image","source":{"type":"base64","media_type":"image/png","data":"x"}},{"type":"text","text":"[Image #1] look at this"}]}}'
RESULT='{"type":"user","message":{"content":[{"type":"tool_result","tool_use_id":"t1","content":"ok"}]}}'
transcript "$(readme 120)" "$IMAGE" "$(readme 40)"
check "sharpen: a prompt with an image starts a turn" "$SG" "$(stop_payload)" silent
transcript "$(readme 100)" "$RESULT" "$(readme 100)"
check "sharpen: a tool result does not start a turn" "$SG" "$(stop_payload)" '"block"'

OLD=$(words 400)
transcript "$(jq -cn --arg t "$OLD extra" '{type:"tool_use",id:"w1",name:"Write",input:{file_path:"/p/README.md",content:$t}}')" \
  "$(jq -cn --arg o "$OLD" '{type:"user",message:{content:[{type:"tool_result",tool_use_id:"w1",content:"ok"}]},toolUseResult:{type:"update",filePath:"/p/README.md",originalFile:$o}}')"
check "sharpen: a Write over an existing file counts its changed words" "$SG" "$(stop_payload)" silent
transcript "$(jq -cn --arg t "$(words 200)" '{type:"tool_use",id:"w2",name:"Write",input:{file_path:"/p/NEW.md",content:$t}}')" \
  "$(jq -cn '{type:"user",message:{content:[{type:"tool_result",tool_use_id:"w2",content:"ok"}]},toolUseResult:{type:"create",filePath:"/p/NEW.md",originalFile:null}}')"
check "sharpen: a Write of a new file counts every word" "$SG" "$(stop_payload)" '"block"'

template() { jq -cn --arg p "$1" --arg t "$2" '{type:"tool_use",name:"Write",input:{file_path:$p,content:$t}}'; }
transcript "$(template /p/resources/views/a.blade.php "<section><p>$(words 60)</p></section>")"
check "sharpen: a template with a paragraph" "$SG" "$(stop_payload)" '"block"'
transcript "$(template /p/resources/views/a.blade.php "$(python3 -c "print('<li>word word</li>'*40)")")"
check "sharpen: a template of short labels" "$SG" "$(stop_payload)" silent
transcript "$(template /p/lang/en/app.php "<?php return ['a' => '$(words 30)', 'b' => '$(words 30)'];")"
check "sharpen: a lang file with sentences" "$SG" "$(stop_payload)" '"block"'
transcript "$(template /p/resources/content/pages/home.json "{\"lede\": \"$(words 60)\"}")"
check "sharpen: a content file with sentences" "$SG" "$(stop_payload)" '"block"'
transcript "$(template /private/tmp/claude-501/-p/abc/scratchpad/notes.md "$(words 200)")"
check "sharpen: a scratch file" "$SG" "$(stop_payload)" silent
transcript "$(template /home/u/.claude-accounts/other/projects/-p/memory/note.md "$(words 200)")"
check "sharpen: a memory note under another config dir" "$SG" "$(stop_payload)" silent
transcript "$(template /home/u/.panels/site/2026-01-01-x/context/probe.md "$(words 200)")"
check "sharpen: a panel run file" "$SG" "$(stop_payload)" silent

S="python3 $HOOKS/scope-gate.py"
scope_payload() { jq -cn --arg s "$1" --arg d "$2" --arg p "$3" --arg t "$4" '{session_id:$s,transcript_path:("/c/projects/"+$d+"/s.jsonl"),tool_name:"Edit",tool_input:{file_path:$p,new_string:$t}}'; }
HOME_PROJECT=$(printf '%s' "$HOME" | sed 's/[^A-Za-z0-9]/-/g')
check "scope: project session"     "$S" "$(scope_payload "scope-$$-a" -p-site "$HOME/.claude/rules/x.md" 'A rule.')" 'every project'
check "scope: same edit again"     "$S" "$(scope_payload "scope-$$-a" -p-site "$HOME/.claude/rules/x.md" 'A rule.')" silent
check "scope: new text, new check" "$S" "$(scope_payload "scope-$$-a" -p-site "$HOME/.claude/rules/x.md" 'Another rule.')" '"deny"'
check "scope: home, first edit"    "$S" "$(scope_payload "scope-$$-b" "$HOME_PROJECT" "$HOME/.claude/CLAUDE.md" 'A rule.')" '"deny"'
check "scope: home, later edits"   "$S" "$(scope_payload "scope-$$-b" "$HOME_PROJECT" "$HOME/.claude/rules/x.md" 'Other text.')" silent
check "scope: setup dir is home"   "$S" "$(scope_payload "scope-$$-b" "$HOME_PROJECT--claude-skills" "$HOME/.claude/hooks/x.py" 'More.')" silent
check "scope: handoff"             "$S" "$(scope_payload "scope-$$-c" -p-site "$HOME/.claude/handoffs/site-2026-01-01-x.md" x)" silent
check "scope: panel run"           "$S" "$(scope_payload "scope-$$-c" -p-site "$HOME/.panels/site/run/briefs/round-1.md" x)" silent
check "scope: memory file"         "$S" "$(scope_payload "scope-$$-c" -p-site "$HOME/.claude/projects/-p-site/memory/a.md" x)" silent
check "scope: synced skill"        "$S" "$(scope_payload "scope-$$-c" -p-site "$HOME/.claude/skills/synced/a/SKILL.md" x)" silent
for skill in accounts clauset rex; do
  check "scope: local $skill" "$S" "$(scope_payload "scope-$$-local-$skill" -p-site "$HOME/.claude/skills/$skill/SKILL.md" 'A local rule.')" silent
done
check "scope: exact setup filename" "$S" "$(scope_payload "scope-$$-suffix" -p-site "$HOME/.claude/CLAUDE.md.backup" x)" silent
check "scope: tool state"          "$S" "$(scope_payload "scope-$$-c" -p-site "$HOME/.claude/clauset/config.toml" x)" silent
check "scope: project guideline"   "$S" "$(scope_payload "scope-$$-c" -p-site /p/site/CLAUDE.md x)" silent
check "scope: own skill"           "$S" "$(scope_payload "scope-$$-c" -p-site "$HOME/.claude/skills/finish/SKILL.md" 'A step.')" '"deny"'
check "scope: own skill, any file" "$S" "$(scope_payload "scope-$$-c" -p-site "$HOME/.claude/skills/ui/surfaces.md" 'A value.')" '"deny"'
rm -f "${TMPDIR:-/tmp}"/claude-scope-gate/scope-$$-*

R="rtk hook claude"
if command -v rtk >/dev/null; then
  check "rtk: rewrites git status" "$R" "$(bash_payload 'git status')" 'rtk'
fi

exit $fail
