#!/bin/bash
# Auto-Sync: discover new skills, services -> update JSON -> commit
# Runs daily via hermes cron (no-agent mode, 0 token if nothing changed)

set -euo pipefail

CDIR="/home/zhang/my-first-web"
cd "$CDIR"

dirty=0

# ──────────────────────────────────────
# Helper: extract description from SKILL.md
# ──────────────────────────────────────
extract_skill_info() {
  local skill_id="$1"
  local skill_file
  skill_file=$(find ~/.hermes/skills -maxdepth 3 -name SKILL.md -path "*/${skill_id}/SKILL.md" 2>/dev/null | head -1)

  if [ -n "$skill_file" ]; then
    local desc
    desc=$(sed -n '/^description:/{s/description:[[:space:]]*"//;s/"$//p}' "$skill_file" 2>/dev/null || echo "")
    local detail
    detail=$(sed -n '/^---$/,/^---$/!p' "$skill_file" 2>/dev/null | grep -v '^#' | grep -v '^$' | head -3 | tr '\n' ' ' | sed 's/^ *//;s/ *$//' || echo "")
    echo "${desc:-Hermes Agent 技能}"
    echo "---"
    echo "${detail:-这是一个 Hermes Agent 技能，详细说明请查看 skill_view。}"
  else
    echo "Hermes Agent 技能"
    echo "---"
    echo "自动同步添加的 Hermes Agent 技能。"
  fi
}

# ──────────────────────────────────────
# 1. Sync skills
# ──────────────────────────────────────
if command -v hermes &>/dev/null; then
  EXISTING_IDS=$(python3 << 'PYEOF'
import json
with open('data/skills.json') as f:
    skills = json.load(f)
ids = sorted([sk['id'] for sk in skills])
print('\n'.join(ids))
PYEOF
  )

  HERMES_IDS=$(
    hermes skills list 2>/dev/null \
      | grep '│' \
      | grep -v 'Name│─│━│┃│┏│┡│└' \
      | while IFS='│' read -r _ name _; do
          # Strip surrounding whitespace AND trailing … (CLI truncates long names)
          name="${name#"${name%%[![:space:]]*}"}"
          name="${name%"${name##*[![:space:]]}"}"
          name="${name%…}"
          [ -n "$name" ] && echo "$name"
        done
  )

  while IFS= read -r skill_id; do
    [ -z "$skill_id" ] && continue
    if ! echo "$EXISTING_IDS" | grep -qF "$skill_id" 2>/dev/null; then
      echo "[SYNC] New skill detected: $skill_id"
      dirty=1

      INFO=$(extract_skill_info "$skill_id")
      SUMMARY=$(echo "$INFO" | head -1)
      DETAIL=$(echo "$INFO" | sed -n '3p')

      python3 << PYEOF
import json
summary = '''${SUMMARY}'''
detail = '''${DETAIL}'''
with open('data/skills.json') as f:
    skills = json.load(f)
skills.append({
    'id': '${skill_id}',
    'name_cn': '${skill_id}',
    'name_en': '${skill_id}',
    'icon': '🔌',
    'category': 'Other',
    'summary': summary if summary else 'Hermes Agent 技能',
    'detail': detail if detail else '自动同步添加的 Hermes Agent 技能。',
    'related': []
})
with open('data/skills.json', 'w', encoding='utf-8') as f:
    json.dump(skills, f, ensure_ascii=False, indent=2)
print(f'Added ${skill_id} to skills.json')
PYEOF
    fi
  done <<< "$HERMES_IDS"
fi

# ──────────────────────────────────────
# 1b. Sync MCP tools: discover new MCP servers
# ──────────────────────────────────────
if command -v hermes &>/dev/null; then
  EXISTING_TOOLS=$(python3 << 'PYEOF'
import json
with open('data/tools.json') as f:
    tools = json.load(f)
ids = sorted([t['id'] for t in tools])
print('\n'.join(ids))
PYEOF
  )

  # Get MCP tool names from hermes mcp list (column 1, space-aligned table)
  MCP_NAMES=$(
    hermes mcp list 2>/dev/null \
      | sed -n '5,$p' \
      | awk 'NF > 0 {print $1}'
  )

  while IFS= read -r mcp_id; do
    [ -z "$mcp_id" ] && continue
    if ! echo "$EXISTING_TOOLS" | grep -qF "$mcp_id" 2>/dev/null; then
      echo "[SYNC] New MCP tool detected: $mcp_id"
      dirty=1

      python3 << PYEOF
import json

with open('data/tools.json') as f:
    tools = json.load(f)

tools.append({
    'id': '${mcp_id}',
    'name_cn': '${mcp_id}',
    'name_en': '${mcp_id}',
    'icon': '🔌',
    'category': 'mcp',
    'summary': 'MCP 工具 - ${mcp_id}',
    'detail': '通过 Model Context Protocol 集成的外部工具服务。',
    'status': 'connected'
})

with open('data/tools.json', 'w', encoding='utf-8') as f:
    json.dump(tools, f, ensure_ascii=False, indent=2)

print(f'Added ${mcp_id} to tools.json')
PYEOF
    fi
  done <<< "$MCP_NAMES"
fi

# ──────────────────────────────────────
# 2. Sync services: check systemd vs status.json
# ──────────────────────────────────────
EXISTING_SVCS=$(python3 << 'PYEOF'
import json
with open('status.json') as f:
    data = json.load(f)
svcs = sorted([s['name'] for s in data.get('services', [])])
print('\n'.join(svcs))
PYEOF
)

MONITORED_SVCS="langchain-backend langgraph langflow n8n openclaw-gateway assistant-ui hermes-webui hermes-dashboard redis postgresql dify-api dify-worker dify-web docker portainer"

for svc in $MONITORED_SVCS; do
  if ! echo "$EXISTING_SVCS" | grep -q "^${svc}$" 2>/dev/null; then
    echo "[SYNC] New service detected: $svc"
    dirty=1

    status=$(systemctl --user is-active "$svc" 2>/dev/null || echo "inactive")

    python3 << PYEOF
import json
with open('status.json') as f:
    data = json.load(f)
data['services'].append({
    'name': '${svc}',
    'icon': '⚙️',
    'status': '${status}',
    'type': 'Service'
})
with open('status.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'Added ${svc} to status.json')
PYEOF
  fi
done

# ──────────────────────────────────────
# 3. Commit and push if anything changed
# ──────────────────────────────────────
if [ "$dirty" = "1" ]; then
  git add data/skills.json status.json 2>/dev/null || true
  git commit -m "sync: auto-discover new skills/services $(date +%Y-%m-%d)" --no-gpg-sign 2>/dev/null || true
  git push 2>/dev/null || true
  echo "[SYNC] Changes committed and pushed."
else
  echo "[SYNC] Nothing to sync. All up to date."
fi