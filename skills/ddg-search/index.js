/**
 * DuckDuckGo Search Skill for OpenClaw
 * Provides web search without requiring an API key
 */

const { execSync } = require('child_process');
const path = require('path');

module.exports = {
  id: 'ddg-search',
  name: 'DuckDuckGo Search',
  description: 'Search the web using DuckDuckGo without an API key',
  
  tools: {
    ddg_search: {
      description: 'Search the web using DuckDuckGo',
      parameters: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Search query'
          },
          num_results: {
            type: 'number',
            description: 'Number of results to return (default: 10)',
            default: 10,
            minimum: 1,
            maximum: 50
          }
        },
        required: ['query']
      },
      
      async execute(args) {
        try {
          const scriptPath = path.join(__dirname, 'ddg_search.py');
          const cmd = `python3 "${scriptPath}" "${args.query}" -n ${args.num_results || 10} --json`;
          const output = execSync(cmd, { encoding: 'utf-8' });
          return JSON.parse(output);
        } catch (error) {
          return {
            error: error.message,
            query: args.query
          };
        }
      }
    }
  },
  
  commands: {
    'ddg-search': {
      description: 'Search the web using DuckDuckGo',
      action: async (context, query) => {
        const tool = module.exports.tools.ddg_search;
        return tool.execute({ query, num_results: 10 });
      }
    }
  }
};
