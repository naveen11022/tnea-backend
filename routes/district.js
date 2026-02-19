const express = require('express');
const router = express.Router();
const rateLimit = require('express-rate-limit');
const db = require('../config/database');
const redis = require('../config/cache');

const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 15,
  message: 'Too many requests'
});

const limiter2 = rateLimit({
  windowMs: 60 * 1000,
  max: 20,
  message: 'Too many requests'
});

router.post('/districts', limiter, async (req, res) => {
  try {
    const { District } = req.body;
    
    const query = `
      SELECT DISTINCT location 
      FROM colleges 
      WHERE region IN (${District.map(() => '?').join(',')})
      ORDER BY location
    `;
    
    const [results] = await db.query(query, District);
    const districts = results.map(row => row.location);
    
    res.json(districts);
  } catch (error) {
    console.error('Error:', error);
    res.json([]);
  }
});

router.get('/college_type', limiter2, async (req, res) => {
  try {
    const cacheKey = 'college_type';
    const cached = await redis.get(cacheKey);
    
    if (cached) {
      return res.json(cached);
    }
    
    const query = 'SELECT DISTINCT college_type FROM colleges';
    const [results] = await db.query(query);
    const collegeTypes = results.map(row => row.college_type);
    
    await redis.setex(cacheKey, 3600, JSON.stringify(collegeTypes));
    
    res.json(collegeTypes);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
