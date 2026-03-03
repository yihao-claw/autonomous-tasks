#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { pipeline } = require('@xenova/transformers');

const MEMORY_DIR = '/home/node/.openclaw/workspace/memory';
const INDEX_FILE = '/home/node/.openclaw/workspace/.memory_index.json';

let embedder = null;

async function initEmbedder() {
  if (!embedder) {
    console.log('[Build] Loading embedding model...');
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
  const lines = content.split('\n');
  const entries = [];
  let currentEntry = null;

  for (const line of lines) {
    if (line.startsWith('## ')) {
      if (currentEntry) {
        entries.push(currentEntry);
      }
      currentEntry = {
        title: line.replace('## ', '').trim(),
        content: [],
        date: filename.replace('.md', '')
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

function summarize(content) {
  const text = content.join(' ').trim();
  return text.length > 100 ? text.substring(0, 100) + '...' : text;
}

async function buildIndex() {
  console.log('[Build] Starting memory index build...');

  try {
    await initEmbedder();

    const files = fs.readdirSync(MEMORY_DIR).filter(f => f.endsWith('.md'));
    console.log(`[Build] Found ${files.length} memory files`);

    const memories = [];

    // 解析所有 markdown 文件
    for (const file of files) {
      const content = fs.readFileSync(path.join(MEMORY_DIR, file), 'utf8');
      const entries = parseMarkdownMemory(content, file);

      for (const entry of entries) {
        const fullText = entry.content.join('\n');
        const summary = summarize(entry.content);

        console.log(`[Build] Processing: ${entry.date} - ${entry.title}`);

        // 生成嵌入向量
        const embedding = await getEmbedding(summary || entry.title);

        memories.push({
          id: `${entry.date}:${entry.title}`.replace(/\s+/g, '_'),
          date: entry.date,
          title: entry.title,
          summary: summary,
          fullText: fullText,
          embedding: embedding,
          textLength: fullText.length
        });
      }
    }

    if (memories.length === 0) {
      console.log('[Build] No entries found');
      return;
    }

    // 保存索引
    fs.writeFileSync(INDEX_FILE, JSON.stringify(memories, null, 2));
    console.log(`[Build] ✅ Built index with ${memories.length} memories`);
    console.log(`[Build] 📁 Index saved to ${INDEX_FILE}`);

    process.exit(0);
  } catch (error) {
    console.error(`[Build] ❌ Error: ${error.message}`);
    process.exit(1);
  }
}

buildIndex();
