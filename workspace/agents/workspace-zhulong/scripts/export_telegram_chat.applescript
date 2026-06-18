-- Telegram Desktop 聊天记录导出自动化脚本
-- 用途：导出与 @zhulong 的聊天记录
-- 平台：macOS + Telegram Desktop

property targetChat : "zhulong" -- 可以修改为具体的聊天名称
property exportPath : POSIX path of (path to desktop) & "zhulong_export/"

-- 主流程
on run
	display notification "开始导出烛龙聊天记录..." with title "Telegram RPA"
	
	-- 1. 激活 Telegram
	activateTelegram()
	
	-- 2. 搜索并打开 zhulong 聊天
	openChat(targetChat)
	
	-- 3. 打开导出对话框
	openExportDialog()
	
	-- 4. 配置导出选项
	configureExportOptions()
	
	display notification "请手动确认导出路径并点击导出" with title "Telegram RPA" subtitle "需要人工确认最后一步"
end run

-- 激活 Telegram Desktop
on activateTelegram()
	tell application "System Events"
		if not (exists (processes where name is "Telegram")) then
			tell application "Telegram" to activate
			delay 3 -- 等待启动
		else
			tell application "Telegram" to activate
			delay 1
		end if
	end tell
end activateTelegram

-- 打开指定聊天
on openChat(chatName)
	tell application "System Events"
		tell process "Telegram"
			-- 使用 Command + F 打开搜索
			keystroke "f" using command down
			delay 0.5
			
			-- 输入聊天名称
			keystroke chatName
			delay 1
			
			-- 按回车选择第一个结果
			key code 36 -- Return key
			delay 1
			
			-- 再次回车进入聊天
			key code 36
			delay 1
		end tell
	end tell
end openChat

-- 打开导出对话框 (Settings → Advanced → Export Data)
on openExportDialog()
	tell application "System Events"
		tell process "Telegram"
			-- 点击菜单栏
			click menu "Telegram" of menu bar 1
			delay 0.5
			
			-- 点击 Preferences/Settings
			click menu item "Preferences…" of menu "Telegram" of menu bar 1
			delay 1
			
			-- 点击 Advanced 标签 (可能需要根据实际界面调整)
			-- 注意：这里需要根据实际 UI 调整
			keystroke "Advanced" -- 尝试直接输入搜索
			delay 0.5
			
			-- 向下导航到 Export Data
			key code 125 -- Down arrow
			delay 0.3
			key code 125
			delay 0.3
			key code 36 -- Return
			delay 1
		end tell
	end tell
end openExportDialog

-- 配置导出选项
on configureExportOptions()
	tell application "System Events"
		tell process "Telegram"
			-- 这里需要根据实际导出对话框的 UI 进行调整
			-- 通常需要：
			-- 1. 选择导出格式 (HTML/JSON)
			-- 2. 选择时间范围
			-- 3. 选择包含媒体文件与否
			
			display dialog "请在 Telegram 导出对话框中：" & return & return & \
				"1. 选择导出格式：JSON (便于程序解析)" & return & \
				"2. 选择时间范围：全部历史" & return & \
				"3. 取消勾选媒体文件（只导出文本）" & return & \
				"4. 点击导出并选择保存位置" & return & return & \
				"完成后点击确定继续" buttons {"确定"} default button "确定"
		end tell
	end tell
end configureExportOptions

-- 辅助：滚动聊天记录（用于截图/OCR方式）
on scrollChatHistory()
	tell application "System Events"
		tell process "Telegram"
			-- 滚动到最顶部
			key code 126 using command down -- Command + Up
			delay 0.5
			
			-- 持续向下滚动并截图
			repeat 100 times -- 滚动100次
				key code 121 -- Page Down
				delay 0.3
			end repeat
		end tell
	end tell
end scrollChatHistory
