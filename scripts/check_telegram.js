
const https = require('https');

const TOKEN = '8364962139:AAEj2-kjbU1KB3zt-eXC9P0fDkmOTh6oqjI';
const url = `https://api.telegram.org/bot${TOKEN}/getUpdates`;

https.get(url, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    try {
      const json = JSON.parse(data);
      console.log(JSON.stringify(json, null, 2));
    } catch (e) {
      console.error(e);
    }
  });
}).on('error', (e) => {
  console.error(e);
});
