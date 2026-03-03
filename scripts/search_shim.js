
const http = require('http');

const QUERY = process.argv[2];
if (!QUERY) {
  console.error('Usage: node search_shim.js <query>');
  process.exit(1);
}

const options = {
  hostname: 'localhost',
  port: 8000,
  path: `/res/v1/web/search?q=${encodeURIComponent(QUERY)}&count=10`,
  method: 'GET',
  headers: {
    'Accept': 'application/json',
    'X-Subscription-Token': 'shim' // Shim might expect this or ignore it
  }
};

const req = http.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    try {
      const json = JSON.parse(data);
      // Format output for readability
      if (json.web && json.web.results) {
        console.log(JSON.stringify(json.web.results, null, 2));
      } else {
        console.log(JSON.stringify(json, null, 2));
      }
    } catch (e) {
      console.error('Error parsing JSON:', e);
      console.log(data); // print raw if parse fails
    }
  });
});

req.on('error', (e) => {
  console.error(`Request failed: ${e.message}`);
});

req.end();
