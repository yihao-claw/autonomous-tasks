const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();

(async () => {
  // 應用 stealth 插件
  chromium.use(stealth);
  
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled'
    ]
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    timezoneId: 'America/New_York'
  });
  
  const page = await context.newPage();
  
  // 隱藏 webdriver 特徵
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined,
    });
  });
  
  console.log('正在訪問 Upwork（使用 stealth 模式）...');
  
  try {
    await page.goto('https://www.upwork.com/nx/jobs/search/?sort=recency', {
      waitUntil: 'domcontentloaded',
      timeout: 90000
    });
    
    console.log('頁面已載入，等待 Cloudflare 驗證...');
    await page.waitForTimeout(10000); // 等待 Cloudflare 驗證
    
    // 檢查是否被 Cloudflare 攔截
    const bodyText = await page.textContent('body');
    if (bodyText.includes('Cloudflare') || bodyText.includes('Enable JavaScript')) {
      console.log('仍被 Cloudflare 攔截，嘗試截圖...');
      await page.screenshot({ path: 'upwork_cloudflare.png' });
      console.log('截圖已儲存：upwork_cloudflare.png');
    } else {
      console.log('成功繞過 Cloudflare！');
      
      // 嘗試抓取工作列表
      await page.waitForTimeout(5000);
      const jobs = await page.$$eval('[data-test="job-tile-title"]', elements => 
        elements.slice(0, 15).map(el => el.textContent.trim())
      ).catch(() => []);
      
      if (jobs.length > 0) {
        console.log('\n✅ 找到的工作:');
        jobs.forEach((job, i) => {
          console.log(`${i + 1}. ${job}`);
        });
      } else {
        console.log('未找到工作列表，嘗試其他選擇器...');
        await page.screenshot({ path: 'upwork_page.png' });
        console.log('截圖已儲存：upwork_page.png');
        console.log('\n頁面內容預覽:');
        console.log(bodyText.substring(0, 500));
      }
    }
  } catch (error) {
    console.error('錯誤:', error.message);
  }
  
  await browser.close();
})();
