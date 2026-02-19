const express = require('express');
const router = express.Router();
const rateLimit = require('express-rate-limit');
const db = require('../config/database');

const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 5,
  message: 'Too many requests'
});

router.post('/fetch_data', limiter, async (req, res) => {
  try {
    const data = req.body;
    
    let query = `
      SELECT 
        ca.aggr_mark, ca.general_rank, ca.community_rank, ca.community,
        ca.college_code, c.college_name, b.branch_name,
        ca.allotted_category, ca.year, ca.round
      FROM candidate_allotment ca
      LEFT JOIN colleges c ON ca.college_code = c.college_code
      LEFT JOIN branch b ON ca.branch_code = b.branch_code
      WHERE 1=1
    `;
    
    const params = [];
    
    if (data.Group && data.Group.length > 0) {
      query += ` AND b.category IN (${data.Group.map(() => '?').join(',')})`;
      params.push(...data.Group);
    }
    
    if (data.Year && data.Year.length > 0) {
      query += ` AND ca.year IN (${data.Year.map(() => '?').join(',')})`;
      params.push(...data.Year);
    }
    
    if (data.Community && data.Community.length > 0) {
      query += ` AND ca.community IN (${data.Community.map(() => '?').join(',')})`;
      params.push(...data.Community);
    }
    
    if (data.Department && data.Department.length > 0) {
      query += ` AND ca.branch_code IN (${data.Department.map(() => '?').join(',')})`;
      params.push(...data.Department);
    }
    
    if (data.Region && data.Region.length > 0) {
      query += ` AND c.region IN (${data.Region.map(() => '?').join(',')})`;
      params.push(...data.Region);
    }
    
    if (data.District && data.District.length > 0) {
      query += ` AND c.location IN (${data.District.map(() => '?').join(',')})`;
      params.push(...data.District);
    }
    
    if (data.Cutoff && data.Cutoff.length > 0) {
      const operator = data.Cutoff[0];
      if (operator === 'between') {
        query += ` AND ca.aggr_mark BETWEEN ? AND ?`;
        params.push(data.FirstValue[0], data.SecondValue[0]);
      } else if (operator === '>') {
        query += ` AND ca.aggr_mark > ?`;
        params.push(data.FirstValue[0]);
      } else if (operator === '<') {
        query += ` AND ca.aggr_mark < ?`;
        params.push(data.FirstValue[0]);
      } else if (operator === '>=') {
        query += ` AND ca.aggr_mark >= ?`;
        params.push(data.FirstValue[0]);
      } else if (operator === '<=') {
        query += ` AND ca.aggr_mark <= ?`;
        params.push(data.FirstValue[0]);
      } else if (operator === '=') {
        query += ` AND ca.aggr_mark = ?`;
        params.push(data.FirstValue[0]);
      }
    }
    
    if (data.CollegeType && data.CollegeType.length > 0) {
      query += ` AND c.college_type IN (${data.CollegeType.map(() => '?').join(',')})`;
      params.push(...data.CollegeType);
    }
    
    query += ` ORDER BY ca.year DESC, ca.aggr_mark DESC`;
    
    const [results] = await db.query(query, params);
    
    res.json(results);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
