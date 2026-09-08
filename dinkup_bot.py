import os
import time
import json
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def wait_until_target_time(target_hour=12, target_minute=0, target_second=0):
    """毫秒級倒數等待至 12:00:00"""
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=target_second, microsecond=0)

    if now > target_time:
        print(f"⏰ 當前時間 {now.strftime('%H:%M:%S')} 已超過開搶時間，直接啟動！")
        return

    print(f"⏳ 當前時間：{now.strftime('%H:%M:%S')}，毫秒級預熱倒數中...")
    while True:
        now = datetime.now()
        remaining = (target_time - now).total_seconds()
        if remaining <= 0:
            print("\n🚀 12:00:00 到達！啟動 API 搶報！")
            break
        elif remaining > 2:
            time.sleep(0.5)
        else:
            time.sleep(0.001)  # 最後 2 秒進入高頻迴圈

def run():
    # 1. 動態計算 6 天後的目標日期
    target_date_dt = datetime.now() + timedelta(days=6)
    target_date_iso = target_date_dt.strftime("%Y-%m-%d")
    print(f"🎯 計算目標預約日期（6天後）：{target_date_iso}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 優先從 GitHub Secrets (環境變數) 讀取；若沒有則讀取本地 auth.json
        auth_env = os.environ.get("AUTH_JSON_CONTENT")
        if auth_env:
            print("🔑 使用 GitHub Secrets 進行身分驗證")
            auth_data = json.loads(auth_env)
            context = browser.new_context(storage_state=auth_data)
        elif os.path.exists("auth.json"):
            print("🔑 使用本地 auth.json 進行身分驗證")
            context = browser.new_context(storage_state="auth.json")
        else:
            raise FileNotFoundError("❌ 找不到認證資料！請設定 AUTH_JSON_CONTENT 或提供 auth.json 檔案。")
        
        # 2. 提取 Session Cookies 轉給 requests
        playwright_cookies = context.cookies()
        session = requests.Session()
        for cookie in playwright_cookies:
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Origin": "https://dinkup.club",
            "Referer": "https://dinkup.club/xinyi"
        }

        # 3. 精準倒數至 12:00:00
        wait_until_target_time(12, 0, 0)

        # 4. 極速輪詢撈取 Event ID 與 Division ID
        events_url = f"https://dinkup.club/api/events?club=xinyi&date={target_date_iso}"
        event_id = None
        division_id = None

        print("🔄 正在向 API 獲取開放場次...")
        for attempt in range(1, 40):
            try:
                res = session.get(events_url, headers=headers, timeout=2)
                if res.status_code == 200:
                    data = res.json()
                    events = data if isinstance(data, list) else data.get("events", [])
                    
                    if len(events) > 0:
                        for ev in events:
                            event_title = ev.get("title", "") or ev.get("location", "")
                            
                            # 優先鎖定包含「信義」或「週五」的場次（若都沒有則取第一個開放場次）
                            if "信義" in event_title or "週五" in event_title or len(events) == 1:
                                event_id = ev.get("id")
                                divisions = ev.get("divisions", [])
                                
                                for div in divisions:
                                    div_name = str(div.get("name", "") or div.get("level", "") or div.get("id", "")).lower()
                                    # 匹配代碼 'fun' 或中文 '歡樂'
                                    if "fun" in div_name or "歡樂" in div_name:
                                        division_id = div.get("id")
                                        break
                                if event_id and division_id:
                                    break
                        
                        if event_id and division_id:
                            print(f"🔥 [第 {attempt} 次嘗試] 成功獲取 ID！Event: {event_id} | Division (fun): {division_id}")
                            break
            except Exception:
                pass

            time.sleep(0.1)  # 每 0.1 秒極速重試一次

        # 5. 發射 POST 報名封包 (+2 人)
        if event_id and division_id:
            register_url = f"https://dinkup.club/api/events/{event_id}/registrations?club=xinyi"
            payload = {
                "divisionId": division_id,
                "displayName": "Luke",
                "needsPaddle": False,
                "count": 2
            }

            print(f"⚡ 正在發送搶報 POST 請求：{register_url}")
            reg_res = session.post(register_url, json=payload, headers=headers)

            print(f"📩 後端回應狀態碼：{reg_res.status_code}")
            print(f"📩 回應詳細內容：{reg_res.text}")

            if reg_res.status_code in [200, 201]:
                print("\n🎉🎉🎉 恭喜！API 報名成功！🎉🎉🎉")
            else:
                print(f"\n❌ 報名失敗，回應碼: {reg_res.status_code}")
        else:
            print("\n❌ 未能在時間內獲取到開放的 Event ID 或 fun 分組 ID。")

        browser.close()

if __name__ == "__main__":
    run()