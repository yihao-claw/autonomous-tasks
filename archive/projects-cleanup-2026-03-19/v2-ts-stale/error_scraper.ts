
import * as fs from 'fs/promises';

export interface DetectedError {
  status: number;
  message?: string;
  sourceLine?: number;
  codeSnippet?: string;
}

export const errorScraper = async (filePath: string): Promise<DetectedError[]> => {
  let content = "";
  try {
    content = await fs.readFile(filePath, 'utf-8');
  } catch (e) {
    return [];
  }

  const errors: DetectedError[] = [];
  const lines = content.split('\n');

  // Regex Patterns
  const patterns = [
    // res.status(404)
    { regex: /res\.status\(\s*(\d{3})\s*\)/, group: 1 },
    // throw new HttpError(400, "Bad Request")
    // Assuming signatures like new Error(status, msg) or new StatusError(msg) -> hard to guess status unless explicit
    // Common: throw new NotFoundError() -> Map to 404?
    // Let's stick to explicit numbers for high precision first.
    
    // NestJS: new HttpException('...', 403)
    { regex: /new\s+HttpException\s*\([^,]+,\s*(\d{3})\)/, group: 1 },
    
    // Boom/Hapi: Boom.notFound() -> need mapping. 
    // Let's catch generic "throw new" and try to infer from name
  ];

  // Name-based inference (Heuristic)
  const namePatterns = [
    { regex: /NotFound/, status: 404 },
    { regex: /BadRequest/, status: 400 },
    { regex: /Unauthorized/, status: 401 },
    { regex: /Forbidden/, status: 403 },
    { regex: /Conflict/, status: 409 },
    { regex: /InternalServer/, status: 500 },
  ];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // 1. Check explicit status codes
    for (const p of patterns) {
      const match = p.regex.exec(line);
      if (match) {
        const status = parseInt(match[p.group], 10);
        if (!isNaN(status)) {
          errors.push({
            status,
            sourceLine: i + 1,
            codeSnippet: line.trim()
          });
        }
      }
    }

    // 2. Check "throw new Error" patterns
    if (line.includes('throw new')) {
        for (const np of namePatterns) {
            if (np.regex.test(line)) {
                errors.push({
                    status: np.status,
                    sourceLine: i + 1,
                    codeSnippet: line.trim()
                });
            }
        }
    }
  }

  return errors;
};
