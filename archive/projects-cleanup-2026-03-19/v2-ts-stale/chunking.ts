
import * as yaml from 'js-yaml';
import { IndexMap } from './indexing';

export interface EndpointDef {
  pathKey: string;
  method: string;
  spec: Record<string, unknown>;
  sourceFile?: string; // The file we think this lives in
}

export interface ChunkGroup {
  name: string; // e.g. "src/controllers/UserController.ts" or "chunk_1"
  endpoints: EndpointDef[];
  relevantFiles: string[]; // Files that MUST be read for this chunk
}

// Estimate tokens (rough heuristic: 4 chars = 1 token)
const estimateTokenCount = (obj: unknown): number => {
  const json = JSON.stringify(obj);
  return Math.ceil(json.length / 4);
};

export const createLocalityAwareChunks = (
  specYaml: string,
  indexMap: IndexMap,
  maxTokensPerChunk: number = 4000
): ChunkGroup[] => {
  const parsed = yaml.load(specYaml) as Record<string, unknown>;
  const paths = (parsed?.paths ?? {}) as Record<string, Record<string, unknown>>;
  
  // 1. Map endpoints to files
  const fileGroups: Record<string, EndpointDef[]> = {};
  const unknownEndpoints: EndpointDef[] = [];

  for (const [pathKey, pathObj] of Object.entries(paths)) {
    // Check direct match
    let foundFile = indexMap[pathKey];

    // Fuzzy match attempt: if /users/{id} is in spec, but code has /users/:id
    // This is hard to do statically perfectly, but we can try matching prefixes?
    // For now, let's trust the indexer found exact string literals or assume the spec matches code style.
    
    // Fallback: If not found, try stripping params from pathKey for lookup?
    // e.g. /users/{id} -> look for /users
    if (!foundFile) {
        // Try looking for the "base" path
        const basePath = pathKey.split('/').slice(0, 3).join('/'); // /api/v1
        // This is weak. Let's rely on exact match for V1 or "Unknown".
    }

    const endpoint: EndpointDef = {
      pathKey,
      method: 'ALL',
      spec: pathObj,
      sourceFile: foundFile
    };

    if (foundFile) {
      if (!fileGroups[foundFile]) {
        fileGroups[foundFile] = [];
      }
      fileGroups[foundFile].push(endpoint);
    } else {
      unknownEndpoints.push(endpoint);
    }
  }

  const chunks: ChunkGroup[] = [];

  // 2. Create chunks from File Groups
  // Optimally, one file = one chunk (if it fits).
  // If a file group is huge, split it.
  // If file groups are tiny, merge them? (Merging is better for cost, but splitting by file is better for context purity).
  // Let's try to merge small file groups to fill the token window.

  let currentBuffer: EndpointDef[] = [];
  let currentBufferFiles: Set<string> = new Set();
  let currentTokens = 0;

  const flushBuffer = () => {
    if (currentBuffer.length === 0) return;
    chunks.push({
      name: `Group: ${Array.from(currentBufferFiles).join(', ').slice(0, 50)}...`,
      endpoints: [...currentBuffer],
      relevantFiles: Array.from(currentBufferFiles)
    });
    currentBuffer = [];
    currentBufferFiles.clear();
    currentTokens = 0;
  };

  for (const [file, endpoints] of Object.entries(fileGroups)) {
    const groupTokens = endpoints.reduce((sum, ep) => sum + estimateTokenCount(ep.spec), 0);

    // If adding this file exceeds limit, flush first
    if (currentTokens + groupTokens > maxTokensPerChunk) {
      flushBuffer();
    }

    // If this single file is huge (> maxTokens), we must split it
    if (groupTokens > maxTokensPerChunk) {
        // Simple split logic for huge files
        let tempChunk: EndpointDef[] = [];
        let tempTokens = 0;
        for (const ep of endpoints) {
            const epTokens = estimateTokenCount(ep.spec);
            if (tempTokens + epTokens > maxTokensPerChunk) {
                chunks.push({
                    name: `Split: ${file}`,
                    endpoints: tempChunk,
                    relevantFiles: [file]
                });
                tempChunk = [];
                tempTokens = 0;
            }
            tempChunk.push(ep);
            tempTokens += epTokens;
        }
        if (tempChunk.length > 0) {
             chunks.push({ name: `Split: ${file}`, endpoints: tempChunk, relevantFiles: [file] });
        }
    } else {
        // It fits, add to buffer
        currentBuffer.push(...endpoints);
        currentBufferFiles.add(file);
        currentTokens += groupTokens;
    }
  }
  flushBuffer();

  // 3. Handle Unknowns (Fallback to basic chunking)
  let unknownBuffer: EndpointDef[] = [];
  let unknownTokens = 0;
  
  for (const ep of unknownEndpoints) {
      const tokens = estimateTokenCount(ep.spec);
      if (unknownTokens + tokens > maxTokensPerChunk) {
          chunks.push({
              name: "Misc / Unknown Sources",
              endpoints: unknownBuffer,
              relevantFiles: [] // No specific hint
          });
          unknownBuffer = [];
          unknownTokens = 0;
      }
      unknownBuffer.push(ep);
      unknownTokens += tokens;
  }
  if (unknownBuffer.length > 0) {
      chunks.push({
          name: "Misc / Unknown Sources",
          endpoints: unknownBuffer,
          relevantFiles: []
      });
  }

  return chunks;
};
