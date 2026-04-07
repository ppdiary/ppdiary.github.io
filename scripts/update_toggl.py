import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone

# ================= 設定區 =================
API_TOKEN = 'c26a913a43b9637c12873c8ad47386f1' 
FILE_PATH = 'content/piano.md' 
TARGET_PROJECT = '快樂練琴時光' 
# ==========================================

def get_stats():
    auth = HTTPBasicAuth(API_TOKEN, 'api_token')
    
    # 1. 獲取時區與今天日期
    tw_tz = timezone(timedelta(hours=8))
    now_tw = datetime.now(tw_tz)
    
    # 計算「本週一」的日期 (weekday 0 是週一)
    # 這樣統計就會從本週一凌晨 00:00 開始
    monday = now_tw - timedelta(days=now_tw.weekday())
    monday_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 2. 抓取時間條目 (從本週一至今)
    start_date = monday_start.astimezone(timezone.utc).isoformat()
    end_date = now_tw.astimezone(timezone.utc).isoformat()
    
    # 先抓取專案列表
    proj_res = requests.get("https://api.track.toggl.com/api/v9/me/projects", auth=auth)
    project_map = {p['id']: p['name'] for p in proj_res.json()} if proj_res.status_code == 200 else {}
    
    # 抓取條目
    url = "https://api.track.toggl.com/api/v9/me/time_entries"
    res = requests.get(url, params={"start_date": start_date, "end_date": end_date}, auth=auth)
    
    if res.status_code == 200:
        entries = res.json()
        total_seconds = sum(e.get('duration', 0) for e in entries 
                            if project_map.get(e.get('project_id')) == TARGET_PROJECT and e.get('duration', 0) > 0)
        
        total_hours = round(total_seconds / 3600, 1)
        
        # 3. 準備 Markdown 內容
        iso_date = now_tw.isoformat()
        display_monday = monday_start.strftime('%Y-%m-%d')
        display_today = now_tw.strftime('%Y-%m-%d')
        
        content = f"""---
title: "練習軌跡"
date: {iso_date}
draft: false
---

### 🎹 本週練琴進度 (Weekly Progress)

* **統計專案**：{TARGET_PROJECT}
* **本週區間**：{display_monday} (週一) ~ {display_today}
* **本週已累積**：`{total_hours}` 小時
* **最後更新**：{now_tw.strftime('%Y-%m-%d %H:%M')}

> 💡 統計範圍會於每週一自動重置。每一份努力，時間都會幫妳記住。
"""
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 週統計更新完成！本週已練習 {total_hours} 小時。")
    else:
        print(f"❌ 抓取失敗：{res.text}")

if __name__ == "__main__":
    get_stats()