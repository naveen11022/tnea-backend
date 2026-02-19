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

router.get('/get_branch', limiter, async (req, res) => {
  try {
    const cacheKey = 'branch';
    const cached = await redis.get(cacheKey);
    
    if (cached) {
      return res.json(cached);
    }
    
    const query = 'SELECT branch_code, branch_name FROM branch';
    const [results] = await db.query(query);
    const branches = results.map(row => [row.branch_code, row.branch_name]);
    
    await redis.setex(cacheKey, 3600, JSON.stringify(branches));
    
    res.json(branches);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message });
  }
});

router.get('/get_year', limiter, async (req, res) => {
  try {
    const cacheKey = 'year';
    const cached = await redis.get(cacheKey);
    
    if (cached) {
      return res.json(cached);
    }
    
    const query = 'SELECT DISTINCT year FROM candidate_allotment ORDER BY year DESC';
    const [results] = await db.query(query);
    const years = results.map(row => row.year);
    
    await redis.setex(cacheKey, 3600, JSON.stringify(years));
    
    res.json(years);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
