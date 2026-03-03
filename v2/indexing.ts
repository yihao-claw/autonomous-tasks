
import * as fs from 'fs/promises';
import * as path from 'path';

export interface IndexEntry {
  urlPath: string;
  httpMethod: string;
  sourceFile: string;
  lineNo: number;
}

export interface IndexMap {
  [urlPath: string]: string; // URL -> FilePath (Simplified for now)
}

// Regex patterns for common frameworks
// We can expand this list iteratively.
const PATTERNS = [
  // Express/JS: router.get('/users', ...) or app.post('/login', ...)
  {
    name: 'Express/Standard',
    regex: /\.(get|post|put|delete|patch|options|head)\s*\(\s*['"`]([^'"`]+)['"`]/g,
    methodGroup: 1,
    pathGroup: 2
  },
  // NestJS/TS: @Get('/users') or @Post('login')
  {
    name: 'NestJS/Decorators',
    regex: /@(Get|Post|Put|Delete|Patch|Options|Head)\s*\(\s*['"`]([^'"`]*)['"`]?\s*\)/g,
    methodGroup: 1,
    pathGroup: 2
  },
  // Java/Spring style (sometimes appears in TS too): @RequestMapping(value = "/path", method = ...)
  // Keeping it simple for JS/TS context for now.
];

async function walkDir(dir: string, fileList: string[] = []): Promise<string[]> {
  const files = await fs.readdir(dir);
  for (const file of files) {
    const p = path.join(dir, file);
    const stat = await fs.stat(p);
    if (stat.isDirectory()) {
      if (file !== 'node_modules' && file !== '.git' && file !== 'dist') {
        await walkDir(p, fileList);
      }
    } else {
      if (/\.(ts|js|jsx|tsx)$/.test(file)) {
        fileList.push(p);
      }
    }
  }
  return fileList;
}

export const staticCodeIndexer = async (projectRoot: string): Promise<IndexMap> => {
  const files = await walkDir(projectRoot);
  const index: IndexMap = {};

  for (const file of files) {
    try {
      const content = await fs.readFile(file, 'utf-8');
      const relativePath = path.relative(projectRoot, file);

      for (const pattern of PATTERNS) {
        // Reset regex state
        pattern.regex.lastIndex = 0;
        let match;
        while ((match = pattern.regex.exec(content)) !== null) {
          let urlPath = match[pattern.pathGroup];
          
          // Basic normalization (remove trailing slash, ensure leading slash)
          if (!urlPath.startsWith('/')) urlPath = '/' + urlPath;
          if (urlPath.length > 1 && urlPath.endsWith('/')) urlPath = urlPath.slice(0, -1);

          // Heuristic: If we find a path in a file, map it.
          // Note: This is "fuzzy". NestJS controllers usually have a @Controller('prefix') that prepends.
          // For V1, simple mapping is better than nothing.
          // If we have multiple matches for same path in diff files, last one wins (or we could store array).
          // For specific methods, we might need a more complex key like "GET /users".
          
          // Simplification: Just mapping Path to File. 
          // The LLM will use this as a hint.
          index[urlPath] = relativePath;
        }
      }
    } catch (e) {
      console.warn(`Failed to index ${file}:`, e);
    }
  }
  return index;
};
