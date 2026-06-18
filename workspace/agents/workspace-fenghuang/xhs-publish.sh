#!/bin/bash
# 🕊️ 凤凰·小红书发布全链路脚本 v1.0
# 执行：bash xhs-publish.sh <图片文件名> <标题> <正文文件> [话题文件]
#
# 前提：
#   - OpenClaw browser 已启动
#   - 图片已放在 /tmp/openclaw/uploads/ 下
#   - 登录态有效(cookies 持久化)
#
# 示例：
#   bash xhs-publish.sh xhs_card_v2.png "普通人用AI搞钱的3个真实路径" /tmp/body.txt

set -e

IMAGE="${1:?用法: $0 <图片文件名> <标题> <正文文件> [话题]}"
TITLE="${2:?用法: $0 <图片文件名> <标题> <正文文件> [话题]}"
BODY_FILE="${3:?用法: $0 <图片文件名> <标题> <正文文件> [话题]}"
TOPICS="${4:-AI人工智能 普通人赚钱 自媒体工具 搞钱思维 AI工具}"

PUBLISH_URL="https://creator.xiaohongshu.com/publish/publish?from=direct&target=image"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🕊️ 凤凰·小红书发布 v1.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "图片 : $IMAGE"
echo "标题 : $TITLE"
echo "正文 : $(wc -c < "$BODY_FILE") chars"
echo "话题 : $TOPICS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 0: 检查发布页
echo ""
echo "[1/7] 打开发布页..."
openclaw browser open "$PUBLISH_URL" 2>/dev/null || true
sleep 2

# Step 1: 注册上传文件
echo "[2/7] 注册上传文件: $IMAGE..."
openclaw browser upload "$IMAGE"
sleep 1

# Step 2: 点击上传图片按钮
echo "[3/7] 点击上传图片..."
openclaw browser click e133 2>/dev/null || { openclaw browser snapshot; echo ">>> 重新获取 snapshot 后重试..."; openclaw browser click-coords 576 423; }
sleep 3

# Step 3: 填写标题
echo "[4/7] 填写标题..."
openclaw browser click e197 2>/dev/null
openclaw browser type e197 "$TITLE" 2>/dev/null || {
  # Fallback: via evaluate
  TITLE_ESCAPED=$(echo "$TITLE" | sed 's/"/\\"/g')
  openclaw browser evaluate --fn "(function(){ document.querySelector('[data-testid=title-input]') || document.querySelector('.tiptap-Editor input, [class*=title] input') || (function(){ const inputs=document.querySelectorAll('input'); for(let i=0;i<inputs.length;i++){if(inputs[i].offsetWidth>200&&inputs[i].offsetHeight>30){const inp=inputs[i];inp.focus();inp.value='$TITLE_ESCAPED';['input','change','blur'].forEach(t=>inp.dispatchEvent(new Event(t,{bubbles:true})));return 'ok';}} return 'no input found'; })() })()"
}
sleep 1

# Step 4: 填写正文
echo "[5/7] 填写正文..."
BODY_HTML=$(cat "$BODY_FILE" | sed 's/"/\\"/g' | sed 's/'\''/\\'\''/g' | sed ':a;N;$!ba;s/\n/<br>/g')

openclaw browser click e207 2>/dev/null || true
sleep 0.5

openclaw browser evaluate --fn "(function(){
  const editor = document.querySelector('.tiptap.ProseMirror')
  if (!editor) return 'ERROR: editor not found'
  editor.focus()
  const sel = window.getSelection()
  const range = document.createRange()
  range.selectNodeContents(editor)
  range.collapse(false)
  sel.removeAllRanges()
  sel.addRange(range)
  document.execCommand('insertHTML', false, '$BODY_HTML')
  editor.dispatchEvent(new InputEvent('input', {bubbles: true, cancelable: true}))
  editor.dispatchEvent(new Event('change', {bubbles: true}))
  return 'Body OK: ' + editor.textContent.length + ' chars'
})()"
sleep 1

# Step 5: 添加话题标签
echo "[6/7] 添加话题..."
TOPIC_HTML=""
for t in $TOPICS; do
  TOPIC_HTML="$TOPIC_HTML #$t"
done

openclaw browser evaluate --fn "(function(){
  const editor = document.querySelector('.tiptap.ProseMirror')
  if (!editor) return 'ERROR: editor not found'
  editor.focus()
  const sel = window.getSelection()
  const range = document.createRange()
  range.selectNodeContents(editor)
  range.collapse(false)
  sel.removeAllRanges()
  sel.addRange(range)
  document.execCommand('insertHTML', false, ' $TOPIC_HTML')
  editor.dispatchEvent(new InputEvent('input', {bubbles: true, cancelable: true}))
  editor.dispatchEvent(new Event('change', {bubbles: true}))
  return 'Topics OK'
})()"
sleep 1

# Step 6: 发布
echo "[7/7] 发布..."
openclaw browser click e472 2>/dev/null || {
  # Fallback to click-coords
  openclaw browser click-coords 1050 900
}
sleep 4

# 验证
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 验证发布结果..."
URL=$(openclaw browser evaluate --fn "(function(){ return window.location.href })()" 2>/dev/null || echo "")
if echo "$URL" | grep -q "published=true"; then
  echo "✅ 发布成功！URL: $URL"
else
  echo "⚠️ URL: $URL"
  echo "请手动检查发布结果"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
