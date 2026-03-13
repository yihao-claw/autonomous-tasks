
const http = require('http');

const options = {
  hostname: 'localhost',
  port: 8000,
  path: '/res/v1/web/search?q=test',
  method: 'GET'
};

const req = http.request(options, (res) => {
  console.log(`STATUS: ${res.statusCode}`);
  res.setEncoding('utf8');
  res.on('data', (chunk) => {
    console.log(`BODY: ${chunk.substring(0, 100)}...`);
  });
});

req.on('error', (e) => {
  console.error(`problem with request: ${e.message}`);
});

req.end();
