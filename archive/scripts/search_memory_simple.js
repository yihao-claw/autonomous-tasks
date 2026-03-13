#!/usr/bin/env node

const fs = require('fs');
const { pipeline } = require('@xenova/transformers');

const INDEX_FILE = '/home/node/.openclaw/workspace/.memory_index.json';

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

function cosineSimilarity(vecA, vecB) {
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    normA += vecA[i] * vecA[i];
    normB += vecB[i] * vecB[i];
  }

  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  return denom === 0 ? 0 : dotProduct / denom;
}

function estimateTokens(text) {
  return Math.ceil((text || '').length / 4);
}

async function searchMemories(query, maxTokens = 500, limit = 5) {
  try {
    // 检查索引是否存在
    if (!fs.existsSync(INDEX_FILE)) {
      return {
        success: false,
        error: 'Memory index not built. Run: node scripts/build_memory_index.js'
      };
    }

    await initEmbedder();

    // 读取索引
    const memories = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8'));

    // 获取查询嵌入
    const queryEmbedding = await getEmbedding(query);

    // 计算相似度
    const scored = memories.map(m => ({
      ...m,
      similarity: cosineSimilarity(queryEmbedding, m.embedding)
    }));

    // 排序和过滤
    const results = scored
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit);
    
    // 日志输出前几个分数供调试
    if (process.env.DEBUG) {
      console.error('Top scores:', scored.sort((a, b) => b.similarity - a.similarity).slice(0, 3).map(r => ({ title: r.title, sim: r.similarity })));
    }

    // 检查 token 预算
    const filtered = [];
    let totalTokens = 0;

    for (const result of results) {
      const tokens = estimateTokens(result.summary);

      if (totalTokens + tokens > maxTokens) {
        break;
      }

      filtered.push({
        title: result.title,
        summary: result.summary,
        date: result.date,
        relevance: result.similarity.toFixed(3),
        tokens: tokens
      });

      totalTokens += tokens;
    }

    return {
      success: true,
      query: query,
      results: filtered,
      tokensUsed: totalTokens,
      maxTokens: maxTokens,
      count: filtered.length,
      searchedTotal: scored.length
    };

  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

// 主函数
(async () => {
  const query = process.argv[2] || 'general';
  const maxTokens = process.argv[3] ? parseInt(process.argv[3]) : 500;

  const result = await searchMemories(query, maxTokens);
  console.log(JSON.stringify(result, null, 2));

  process.exit(result.success ? 0 : 1);
})();
