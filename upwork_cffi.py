#!/usr/bin/env python3
from curl_cffi import requests
import json
import re

def main():
    print("使用 curl-cffi 訪問 Upwork...")
    
    try:
        # 使用 Chrome 的 TLS 指紋
        response = requests.get(
            'https://www.upwork.com/nx/jobs/search/?sort=recency',
            impersonate="chrome120",
            timeout=30
        )
        
        print(f"狀態碼: {response.status_code}")
        print(f"內容長度: {len(response.text)} 字元\n")
        
        # 檢查是否被 Cloudflare 攔截
        if 'Cloudflare' in response.text or 'Enable JavaScript' in response.text:
            print("⚠️ 仍被 Cloudflare 攔截")
            print("頁面內容預覽:")
            print(response.text[:500])
        else:
            print("✅ 成功繞過 Cloudflare!")
            
            # 嘗試提取工作標題
            # Upwork 可能用 React，所以數據可能在 JSON 中
            
            # 方法 1: 尋找 data-test="job-tile-title"
            titles = re.findall(r'data-test="job-tile-title"[^>]*>([^<]+)', response.text)
            
            if titles:
                print(f"\n找到 {len(titles)} 個工作標題:\n")
                for i, title in enumerate(titles[:15], 1):
                    print(f"{i}. {title.strip()}")
            else:
                # 方法 2: 尋找 JSON 數據
                json_matches = re.findall(r'<script[^>]*>window\.__INITIAL_STATE__\s*=\s*({.+?})</script>', response.text, re.DOTALL)
                
                if json_matches:
                    print("找到 JSON 數據，嘗試解析...")
                    try:
                        data = json.loads(json_matches[0])
                        print("JSON 結構:")
                        print(json.dumps(list(data.keys()), indent=2))
                    except:
                        pass
                
                # 保存完整 HTML 以便分析
                with open('upwork_page.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("\nHTML 已儲存到 upwork_page.html")
                
                print("\n頁面內容預覽:")
                print(response.text[:1000])
                
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
