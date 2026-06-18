-- 导出 @zhulong 聊天记录自动化脚本
-- 步骤：打开 Telegram → 搜索 @zhulong → 导出聊天历史

property chatUsername : "zhulong"
property exportPath : (path to downloads folder as string) & "zhulong_export"

-- 主流程
on run
	display notification "开始导出 @zhulong 聊天记录..." with title "烛龙数据恢复"
	
	-- 1. 激活 Telegram Desktop
	tell application "Telegram"
		if not running then
			launch
			delay 3
		end if
		activate
		delay 1
	end tell
	
	-- 2. 使用快捷键打开搜索 (Cmd + F)
	tell application "System Events"
		tell process "Telegram"
			set frontmost to true
			delay 0.5
			-- 打开搜索
			keystroke "f" using command down
			delay 0.5
			-- 输入搜索词
			keystroke chatUsername
			delay 1
			-- 按回车选择第一个结果
			key code 36
			delay 2
		end tell
	end tell
	
	display notification "已打开 @zhulong 聊天，请手动导出..." with title "下一步"
	
	-- 提示用户手动操作导出（因为 AppleScript 无法直接触发导出对话框）
	display dialog "请手动完成以下步骤：" & return & return & ¬
		"1. 在聊天窗口右键点击" & return & ¬
		"2. 选择 'Export chat history'" & return & ¬
		"3. 格式选择：JSON" & return & ¬
		"4. 取消勾选媒体文件（只导出文字）" & return & ¬
		"5. 保存到 Downloads/zhulong_export/" & return & return & ¬
		"完成后点击'已完成'" buttons {"已完成", "取消"} default button "已完成"
	
	return "等待用户完成导出..."
end run
