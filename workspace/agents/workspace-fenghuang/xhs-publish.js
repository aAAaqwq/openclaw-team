#!/usr/bin/env node
/**
 * 🕊️ 凤凰·小红书发布全链路脚本
 * 
 * 用法：配合 OpenClaw browser 使用
 * 
 * 前提：
 *   1. OpenClaw browser 已启动
 *   2. 小红书 cookies 已持久化（登录态有效）
 *   3. 图片已放在 /tmp/openclaw/uploads/ 目录下
 * 
 * 完整发布流程：
 *   1. 打开(或切换至) 小红书发布页
 *   2. `openclaw browser upload <filename>` 注册文件
 *   3. 点击「上传图片」按钮 → 文件自动填入
 *   4. 填写标题和正文
 *   5. 添加话题标签
 *   6. 点击「发布」按钮
 * 
 * 成功标志：页面 URL 出现 ?published=true
 * 
 * @version 1.0.0
 * @license MIT
 * @author 凤凰 (Fenghuang CCO) @ OpenClaw
 */

// ===== 配置 =====
const CONFIG = {
  // 发布页 URL
  publishUrl: 'https://creator.xiaohongshu.com/publish/publish?from=direct&target=image',
  
  // 图片上传区
  uploadButtonRef: 'e133',    // "上传图片" 按钮
  fileInputSelector: 'input.upload-input[type="file"]',
  
  // 标题
  titleRef: 'e197',            // textbox "填写标题会有更多赞哦"
  
  // 正文编辑器（tiptap）
  bodySelector: '.tiptap.ProseMirror',
  
  // 话题按钮
  topicButtonRef: 'e222',      // "话题" 按钮
  
  // 发布按钮
  publishButtonRef: 'e472',    // "发布" 按钮
  
  // 截图保存
  screenshotDir: '/tmp/openclaw/uploads/xhs_screenshots',
}

// ===== 命令参考 =====
const COMMANDS = `
# 🏁 完整发布流程 (手动运行)：

# Step 1: 打开发布页（如未打开）
openclaw browser open "${CONFIG.publishUrl}"

# Step 2: 检查登录态（看是否有"蓝血菁英"字样）
openclaw browser snapshot

# Step 3: 注册上传文件
openclaw browser upload <image_filename.png>

# Step 4: 点击上传图片按钮
openclaw browser click ${CONFIG.uploadButtonRef}

# Step 5: 等待图片上传完成（约2-3秒）
sleep 2

# Step 6: 填写标题
openclaw browser type ${CONFIG.titleRef} "你的标题"

# Step 7: 填写正文（注入HTML，支持换行）
# 焦点在正文区域后，用 evaluate 注入
openclaw browser click e207  # 先点击正文让其获得焦点

# 注入正文 HTML
openclaw browser evaluate --fn '(BODY) => {
  const editor = document.querySelector(".tiptap.ProseMirror")
  if (!editor) return "ERROR"
  editor.focus()
  const sel = window.getSelection()
  const range = document.createRange()
  range.selectNodeContents(editor)
  range.collapse(false)
  sel.removeAllRanges()
  sel.addRange(range)
  document.execCommand("insertHTML", false, BODY)
  editor.dispatchEvent(new InputEvent("input", { bubbles: true }))
  editor.dispatchEvent(new Event("change", { bubbles: true }))
  return "OK: " + editor.textContent.length + "chars"
}'  # 注意：实际用 --fn 要传不含分号的函数

# Step 8: 添加话题标签（在正文末尾注入 #话题名）
openclaw browser evaluate --fn '() => {
  const TOPICS = ["AI人工智能", "普通人赚钱", "自媒体工具", "搞钱思维", "AI工具"]
  const editor = document.querySelector(".tiptap.ProseMirror")
  if (!editor) return "ERROR"
  editor.focus()
  const sel = window.getSelection()
  const range = document.createRange()
  range.selectNodeContents(editor)
  range.collapse(false)
  sel.removeAllRanges()
  sel.addRange(range)
  const topicHtml = TOPICS.map(t => "#" + t).join(" ")
  document.execCommand("insertHTML", false, " " + topicHtml)
  editor.dispatchEvent(new InputEvent("input", { bubbles: true }))
  editor.dispatchEvent(new Event("change", { bubbles: true }))
  return "Topics: " + topicHtml
}'

# Step 9: 发布
openclaw browser click ${CONFIG.publishButtonRef}

# Step 10: 验证发布结果
sleep 3
openclaw browser evaluate --fn '() => window.location.href'

# 成功标志：URL 包含 ?published=true
`

module.exports = { CONFIG, COMMANDS }

// 如果直接执行，打印命令参考
if (require.main === module) {
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕊️ 凤凰·小红书全链路发布脚本 v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`)
  console.log(COMMANDS)
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 第二阶段已验证全链路可发布！
   2026-05-04 10:05 CST 第一条真实发布成功
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`)
}
