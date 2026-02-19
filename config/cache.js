const { Redis } = require('@upstash/redis');

const redis = new Redis({
  url: 'https://vocal-vervet-20039.upstash.io',
  token: process.env.CACHE_URL
});

module.exports = redis;
