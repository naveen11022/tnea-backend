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

router.get('/get_branch_category', limiter, async (req, res) => {
  try {
    const cacheKey = 'unique_branch';
    const cached = await redis.get(cacheKey);
    
    if (cached) {
      return res.json(cached);
    }
    
    const query = 'SELECT DISTINCT category FROM branch';
    const [results] = await db.query(query);
    const categories = results.map(row => row.category);
    
    await redis.setex(cacheKey, 3600, JSON.stringify(categories));
    
    res.json(categories);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
