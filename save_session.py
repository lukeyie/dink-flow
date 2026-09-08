from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 啟動乾淨的 Chrome 瀏覽器
    browser = p.chromium.launch(channel="chrome", headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 前往網站
    page.goto("https://dinkup.club/xinyi")

    print("\n==========================================")
    print("請在彈出的瀏覽器中手動完成 DinkUp 登入。")
    print("登入成功後，請回到這個終端機視窗按 Enter 鍵！")
    print("==========================================\n")

    input("按下 Enter 鍵儲存登入狀態...")

    # 儲存登入狀態與 Cookie 到 auth.json
    context.storage_state(path="auth.json")
    print("✅ 登入狀態已成功儲存至 auth.json！")

    browser.close()