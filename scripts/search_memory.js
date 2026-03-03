#!/usr/bin/env node

const db = require('@lancedb/lancedb');
const { pipeline } = require('@xenova/transformers');

const LANCEDB_DIR = '/home/node/.openclaw/workspace/memory_lancedb';
const MEMORIES_TABLE = 'memories';

let embedder = null;

async function initEmbedder() {
  if (!embedder) {
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

function estimateTokens(text) {
  // 粗略估计：4个字符 ≈ 1个 token
  return Math.ceil((text || '').length / 4);
}

async function searchMemories(query, maxTokens = 500) {
  try {
    await initEmbedder();

    const database = await db.connect(LANCEDB_DIR);
    const table = await database.openTable(MEMORIES_TABLE);

    // 获取查询的嵌入
    const queryEmbedding = await getEmbedding(query);

    // 向量搜索 - 取 Top 5，需要 await search().limit() 的结果
    const results = await table
      .search(queryEmbedding)
      .limit(5);

    if (!results || results.length === 0) {
      console.log(JSON.stringify({
        success: true,
        query: query,
        results: [],
        tokensUsed: 0,
        maxTokens: maxTokens,
        count: 0,
        message: 'No relevant memories found'
      }, null, 2));
      process.exit(0);
    }

    // 过滤和压缩结果
    const filtered = [];
    let totalTokens = 0;

    for (const result of results) {
      // 距离越小，相关性越高（余弦距离）
      // 相关性 = 1 - distance（对于归一化向量）
      const relevance = (1 - result._distance);
      
      // 相关性门槛 > 0.3（保留更多结果）
      if (relevance < 0.3) continue;

      const summary = result.summary || result.title || '';
      const tokens = estimateTokens(summary);

      // 检查 token 预算
      if (totalTokens + tokens > maxTokens) {
        break;
      }

      filtered.push({
        title: result.title,
        summary: summary,
        date: result.date,
        type: result.type || 'general',
        tags: typeof result.tags === 'string' ? JSON.parse(result.tags) : (result.tags || []),
        relevance: relevance.toFixed(3),
        tokens: tokens
      });

      totalTokens += tokens;
    }

    // 输出结果
    const output = {
      success: true,
      query: query,
      results: filtered,
      tokensUsed: totalTokens,
      maxTokens: maxTokens,
      count: filtered.length
    };

    console.log(JSON.stringify(output, null, 2));
    process.exit(0);

  } catch (error) {
    console.error('Error details:', error);
    const output = {
      success: false,
      error: error.message,
      stack: error.stack
    };
    console.log(JSON.stringify(output, null, 2));
    process.exit(1);
  }
}

// 从命令行参数获取查询
const query = process.argv[2] || 'general';
const maxTokens = process.argv[3] ? parseInt(process.argv[3]) : 500;

searchMemories(query, maxTokens);
