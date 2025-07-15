#!/bin/bash

USERNAME="又拍云账户"
PASSWORD="又拍云密码"
BUCKET_NAME="服务名称"
RULE_NAMES=("重定向1" "重定向2")
NEW_PORT="9999"

LOGIN_URL="https://console.upyun.com/accounts/signin/"
REWRITE_GET_URL="https://console.upyun.com/api/v2/rewrite?bucket_name=${BUCKET_NAME}"
REWRITE_POST_URL="https://console.upyun.com/api/v2/rewrite"

echo "[1] 登录..."

COOKIE=$(curl -s -L -D - -X POST "$LOGIN_URL" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" -o /dev/null |
  grep -i '^Set-Cookie: s=' | head -n1 | sed -E 's/Set-Cookie: (s=[^;]+);.*/\1/i')

if [ -z "$COOKIE" ]; then
  echo "[×] 登录失败"
  exit 1
fi
echo "[√] 登录成功"

echo "[2] 获取配置..."

REWRITE_JSON=$(curl -s -X GET "$REWRITE_GET_URL" -H "Cookie: $COOKIE")

# 拿到规则 ID 和描述，逐条处理
for NAME in "${RULE_NAMES[@]}"; do
  # 获取规则 JSON（纯文本）
  RULE=$(echo "$REWRITE_JSON" | jq -c --arg name "$NAME" '.data.rewrite[] | select(.describe == $name)')
  if [ -z "$RULE" ]; then
    echo "[!] 找不到规则 $NAME，跳过"
    continue
  fi
  REWRITE_ID=$(echo "$RULE" | jq '.rewrite_id')
  echo "[→] 规则: $NAME (ID:$REWRITE_ID)"

  # 用 sed 替换端口号
  # 先抽出content字段的JSON字符串（纯文本处理）
  CONTENT=$(echo "$RULE" | sed -n 's/.*"content":\({.*}\),*"break".*/\1/p')

  # 替换端口号
  NEW_CONTENT=$(echo "$CONTENT" | sed -E "s/:([0-9]+)/:$NEW_PORT/g")

  # 拼装最终 JSON，注意转义
  # jq 只负责解析顶层字段，content用新的文本替换
  FINAL_JSON=$(jq -n --argjson content "$NEW_CONTENT" --arg name "$NAME" --arg status "ON" --argjson priority "$(echo $RULE | jq '.priority')" --argjson brk "$(echo $RULE | jq '.break')" --argjson id "$REWRITE_ID" \
    '{
      describe: $name,
      type: "general",
      priority: $priority,
      break: $brk,
      status: $status,
      rewrite_id: $id,
      content: $content
    }')

  # 发送修改请求
  RESPONSE=$(curl -s -X POST "$REWRITE_POST_URL" \
    -H "Content-Type: application/json" \
    -H "Cookie: $COOKIE" \
    -d "$FINAL_JSON")

  if echo "$RESPONSE" | jq -e '.data' >/dev/null 2>&1; then
    echo "[√] 规则 $NAME 修改成功"
  else
    MSG=$(echo "$RESPONSE" | jq -r '.data.message // "未知错误"')
    echo "[×] 规则 $NAME 修改失败: $MSG"
  fi
done

echo "[完成]"
