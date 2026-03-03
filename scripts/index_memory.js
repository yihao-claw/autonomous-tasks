#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const db = require('@lancedb/lancedb');
const { pipeline } = require('@xenova/transformers');

const MEMORY_DIR = '/home/node/.openclaw/workspace/memory';
const LANCEDB_DIR = '/home/node/.openclaw/workspace/memory_lancedb';
const MEMORIES_TABLE = 'memories';

// 初始化嵌入模型
let embedder = null;

async function initEmbedder() {
  if (!embedder) {
    console.log('[Index] Loading embedding model...');
    embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
  }
  return embedder;
}

async function getEmbedding(text) {
  const embedding = await embedder(text, {
    pooling: 'mean',
    normalize: true
  });
  return Array.from(embedding.data);
}

function parseMarkdownMemory(content, filename) {
  // 简单的 markdown 解析
  const lines = content.split('\n');
  const entries = [];
  let currentEntry = null;

  for (const line of lines) {
    // 检测标题（## 作为分隔符）
    if (line.startsWith('## ')) {
      if (currentEntry) {
        entries.push(currentEntry);
      }
      currentEntry = {
        title: line.replace('## ', '').trim(),
        content: [],
        date: filename.replace('.md', ''),
        tags: []
      };
    } else if (currentEntry && line.trim()) {
      currentEntry.content.push(line);
    }
  }

  if (currentEntry) {
    entries.push(currentEntry);
  }

  return entries;
}

function extractTags(text) {
  // 简单的标签提取（可以扩展）
  const tags = [];
  if (text.includes('decision') || text.includes('決定')) tags.push('decision');
  if (text.includes('bug') || text.includes('問題')) tags.push('bug');
  if (text.includes('lesson') || text.includes('學習')) tags.push('lesson');
  if (text.includes('context') || text.includes('背景')) tags.push('context');
  return tags;
}

function summarize(content) {
  // 取前 100 个字符作为摘要
  const text = content.join(' ').trim();
  return text.length > 100 ? text.substring(0, 100) + '...' : text;
}

async function indexMemories() {
  console.log('[Index] Starting memory indexing...');

  try {
    await initEmbedder();

    // 连接 LanceDB
    const database = await db.connect(LANCEDB_DIR);

    // 读取所有 markdown 文件
    const files = fs.readdirSync(MEMORY_DIR).filter(f => f.endsWith('.md'));
    console.log(`[Index] Found ${files.length} memory files`);

    const allEntries = [];

    // 解析所有 markdown 文件
    for (const file of files) {
      const content = fs.readFileSync(path.join(MEMORY_DIR, file), 'utf8');
      const entries = parseMarkdownMemory(content, file);

      for (const entry of entries) {
        const fullText = entry.content.join('\n');
        const summary = summarize(entry.content);
        const tags = extractTags(fullText);

        console.log(`[Index] Processing: ${entry.date} - ${entry.title}`);

        // 生成嵌入
        const embedding = await getEmbedding(summary || entry.title);

        allEntries.push({
          id: `${entry.date}-${entry.title.replace(/\s+/g, '-')}`,
          date: entry.date,
          title: entry.title,
          summary: summary,
          fullText: fullText,
          tags: tags,
          embedding: embedding,
          type: tags.length > 0 ? tags[0] : 'general',
          createdAt: new Date().toISOString()
        });
      }
    }

    if (allEntries.length === 0) {
      console.log('[Index] No entries to index');
      return;
    }

    // 创建或覆盖表 - 转换 tags 为字符串
    console.log(`[Index] Creating LanceDB table with ${allEntries.length} entries...`);
    const tableEntries = allEntries.map(entry => ({
      ...entry,
      tags: JSON.stringify(entry.tags)  // 转换为字符串
    }));
    const table = await database.createTable(MEMORIES_TABLE, tableEntries, {
      mode: 'overwrite'
    });

    console.log(`[Index] ✅ Indexed ${allEntries.length} memory entries`);
    console.log(`[Index] 📊 Memory types: ${[...new Set(allEntries.map(e => e.type))].join(', ')}`);

    process.exit(0);
  } catch (error) {
    console.error(`[Index] ❌ Error: ${error.message}`);
    process.exit(1);
  }
}

indexMemories();
