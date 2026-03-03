#!/usr/bin/env python3
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

def main():
    print("初始化 undetected Chrome...")
    
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        print("正在訪問 Upwork...")
        driver.get('https://www.upwork.com/nx/jobs/search/?sort=recency')
        
        print("等待頁面載入...")
        time.sleep(15)  # 給 Cloudflare 時間驗證
        
        # 檢查頁面內容
        page_source = driver.page_source
        
        if 'Cloudflare' in page_source or 'Enable JavaScript' in page_source:
            print("⚠️ 仍被 Cloudflare 攔截")
            print("頁面標題:", driver.title)
            driver.save_screenshot('upwork_cf.png')
            print("截圖已儲存：upwork_cf.png")
        else:
            print("✅ 成功訪問 Upwork!")
            print("頁面標題:", driver.title)
            
            # 等待工作列表載入
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="job-tile-title"]'))
                )
                
                jobs = driver.find_elements(By.CSS_SELECTOR, '[data-test="job-tile-title"]')
                
                if jobs:
                    print(f"\n找到 {len(jobs[:15])} 個工作:\n")
                    for i, job in enumerate(jobs[:15], 1):
                        title = job.text.strip()
                        if title:
                            print(f"{i}. {title}")
                else:
                    print("未找到工作列表元素")
                    driver.save_screenshot('upwork_page.png')
                    print("截圖已儲存：upwork_page.png")
                    
            except Exception as e:
                print(f"等待元素時出錯: {e}")
                driver.save_screenshot('upwork_error.png')
                print("截圖已儲存：upwork_error.png")
                
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("\n瀏覽器已關閉")

if __name__ == '__main__':
    main()
