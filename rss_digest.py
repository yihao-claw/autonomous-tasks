#!/usr/bin/env python3
"""
RSS Daily Digest Generator
Fetches feeds from OPML, categorizes, and creates a curated summary
"""

import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from collections import defaultdict
import re
import time

def parse_opml(file_path):
    """Extract RSS feed URLs from OPML file using regex"""
    feeds = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Use regex to find RSS feed outlines
        pattern = r'<outline[^>]*type="rss"[^>]*title="([^"]*)"[^>]*xmlUrl="([^"]*)"'
        matches = re.findall(pattern, content)
        
        for title, url in matches:
            feeds.append({
                'title': title,
                'url': url,
                'html_url': ''
            })
        
        return feeds
    except Exception as e:
        print(f"Error parsing OPML: {e}")
        return []

def fetch_feed(url, timeout=10):
    """Fetch RSS feed with timeout"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (RSS Digest Bot)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except Exception as e:
        return None

def parse_rss(xml_content):
    """Parse RSS/Atom feed and extract recent entries"""
    if not xml_content:
        return []
    
    try:
        root = ET.fromstring(xml_content)
        items = []
        
        # Handle RSS 2.0
        for item in root.findall('.//item'):
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            description = item.findtext('description', '').strip()
            pub_date = item.findtext('pubDate', '')
            
            if title and link:
                items.append({
                    'title': title,
                    'link': link,
                    'description': clean_html(description)[:300],
                    'pub_date': pub_date
                })
        
        # Handle Atom
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('.//atom:entry', ns):
            title = entry.findtext('atom:title', '', ns).strip()
            link_elem = entry.find('atom:link[@rel="alternate"]', ns)
            if link_elem is None:
                link_elem = entry.find('atom:link', ns)
            link = link_elem.get('href', '') if link_elem is not None else ''
            summary = entry.findtext('atom:summary', '', ns).strip()
            
            if title and link:
                items.append({
                    'title': title,
                    'link': link,
                    'description': clean_html(summary)[:300],
                    'pub_date': ''
                })
        
        return items[:10]  # Return top 10 recent items
    except Exception as e:
        return []

def clean_html(text):
    """Remove HTML tags and clean text"""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def categorize_item(title, description, feed_title):
    """Categorize content based on keywords - prioritize specific over general"""
    text = (title + ' ' + description + ' ' + feed_title).lower()
    
    # More specific AI/ML keywords
    ai_keywords = ['llm', 'gpt', 'claude', 'neural network', 'deep learning', 'transformer', 
                   'anthropic', 'openai', 'deepmind', 'machine learning model', 
                   'training data', 'inference', 'fine-tuning', 'embedding']
    
    security_keywords = ['vulnerability', 'cve', 'exploit', 'breach', 'malware', 
                        'ransomware', 'phishing', 'authentication', 'encryption', 
                        'zero-day', 'security flaw', 'hack', 'botnet']
    
    programming_keywords = ['rust', 'golang', 'typescript', 'compiler', 'interpreter',
                           'algorithm', 'data structure', 'api design', 'database design',
                           'linux kernel', 'memory management', 'concurrency', 
                           'functional programming', 'type system']
    
    # Check in order of specificity
    if any(kw in text for kw in security_keywords):
        return '安全相关'
    elif any(kw in text for kw in ai_keywords):
        return 'AI/机器学习'
    elif any(kw in text for kw in programming_keywords):
        return '系统设计/编程'
    # Generic tech indicators
    elif any(kw in text for kw in ['tech', 'startup', 'software', 'developer', 'app']):
        return '技术新闻'
    else:
        return '其他'

def score_item(title, description):
    """Simple scoring for importance"""
    score = 0
    
    # Longer titles and descriptions tend to be more substantial
    score += min(len(title.split()), 10) * 2
    score += min(len(description.split()), 20)
    
    # Boost for certain indicators
    important_words = ['breakthrough', 'major', 'new', 'release', 'announce', 
                      'critical', 'important', 'significant', '重要', '发布', '突破']
    text = (title + ' ' + description).lower()
    score += sum(5 for word in important_words if word in text)
    
    return score

def main():
    print("📰 Fetching RSS feeds...")
    
    feeds = parse_opml('/home/node/.openclaw/workspace/subscriptions.opml')
    print(f"Found {len(feeds)} feeds")
    
    categories = defaultdict(list)
    processed = 0
    failed = 0
    
    for feed in feeds:
        print(f"Fetching: {feed['title']}...", end=' ')
        xml_content = fetch_feed(feed['url'])
        
        if xml_content:
            items = parse_rss(xml_content)
            if items:
                for item in items:
                    category = categorize_item(item['title'], item['description'], feed['title'])
                    item['feed_title'] = feed['title']
                    item['score'] = score_item(item['title'], item['description'])
                    categories[category].append(item)
                print(f"✓ ({len(items)} items)")
                processed += 1
            else:
                print("✗ (no items)")
                failed += 1
        else:
            print("✗ (fetch failed)")
            failed += 1
        
        time.sleep(0.1)  # Be nice to servers
    
    print(f"\n✅ Processed: {processed}, Failed: {failed}")
    
    # Generate digest
    print("\n" + "="*60)
    print(f"📰 每日技术摘要 | Daily Tech Digest")
    print(f"📅 {datetime.now().strftime('%Y年%m月%d日 %A')}")
    print("="*60 + "\n")
    print(f"⚡️ 从 {processed} 个来源获取了 {sum(len(v) for v in categories.values())} 条内容\n")
    
    category_order = ['AI/机器学习', '系统设计/编程', '安全相关', '技术新闻']
    
    for category in category_order:
        if category not in categories:
            continue
        
        items = categories[category]
        # Sort by score and take top 5
        items.sort(key=lambda x: x['score'], reverse=True)
        top_items = items[:5]
        
        if not top_items:
            continue
        
        emoji = {'AI/机器学习': '🤖', '系统设计/编程': '💻', '安全相关': '🔐', '技术新闻': '📱'}
        print(f"{emoji.get(category, '📌')} **{category}**")
        print()
        
        for i, item in enumerate(top_items, 1):
            # Clean title for display
            title = item['title'].replace('\n', ' ').strip()
            print(f"**{i}. {title}**")
            if item['description'] and len(item['description']) > 30:
                desc = item['description'][:180].replace('\n', ' ').strip()
                print(f"   {desc}...")
            print(f"   <{item['link']}>")
            print()
    
    # Other notable content
    other_items = []
    for cat, items in categories.items():
        if cat not in category_order:
            other_items.extend(items)
    
    if other_items and len(other_items) > 0:
        other_items.sort(key=lambda x: x['score'], reverse=True)
        print(f"🌟 **其他值得关注**")
        print()
        for i, item in enumerate(other_items[:3], 1):
            title = item['title'].replace('\n', ' ').strip()
            print(f"**{i}. {title}**")
            print(f"   <{item['link']}>")
            print()
    
    print("─" * 60)
    print(f"📊 统计：{processed} 个有效源 | {sum(len(v) for v in categories.values())} 条内容")
    print(f"💾 生成时间：{datetime.now().strftime('%H:%M:%S UTC')}")
    print("─" * 60)

if __name__ == '__main__':
    main()
