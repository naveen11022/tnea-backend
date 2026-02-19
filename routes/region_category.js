const express = require('express');
const router = express.Router();
const rateLimit = require('express-rate-limit');
const db = require('../config/database');
const redis = require('../config/cache');

const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 20,
  message: 'Too many requests'
});

router.get('/get_region', limiter, async (req, res) => {
  try {
    const cacheKey = 'region';
    const cached = await redis.get(cacheKey);
    
    if (cached) {
      return res.json(cached);
    }
    
    const query = 'SELECT DISTINCT region FROM colleges';
    const [results] = await db.query(query);
    const regions = results.map(row => row.region);
    
    await redis.setex(cacheKey, 3600, JSON.stringify(regions));
    
    res.json(regions);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message });
  }
});

router.get('/get_category', limiter, async (req, res) => {
  try {
    const cacheKey = 'category';
    const cached = await redis.get(cacheKey);
    
    if (cached) {
      return res.json(cached);
    }
    
    const query = 'SELECT DISTINCT community FROM candidate_allotment';
    const [results] = await db.query(query);
    const categories = results.map(row => row.community);
    
    await redis.setex(cacheKey, 3600, JSON.stringify(categories));
    
    res.json(categories);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
