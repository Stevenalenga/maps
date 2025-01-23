const dotenv = require('dotenv');

dotenv.config();

module.exports = {
  mongodbUri: process.env.MONGODB_URI,
  database_name : process.env.DATABASE_NAME,
  secretKey: process.env.SECRET_KEY,
  algorithm: process.env.ALGORITHM || 'HS256',
};