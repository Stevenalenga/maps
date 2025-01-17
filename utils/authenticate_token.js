const jwt = require('jsonwebtoken');
const { User } = require('../models/models');  // Adjust path based on your project structure
const dotenv = require('dotenv');

dotenv.config();  // Load environment variables from .env

const SECRET_KEY = process.env.SECRET_KEY;
const ALGORITHM = process.env.ALGORITHM || 'HS256';
const ACCESS_TOKEN_EXPIRE_MINUTES = parseInt(process.env.ACCESS_TOKEN_EXPIRE_MINUTES) || 30;

// Middleware to authenticate JWT token
const authenticateToken = async (req, res, next) => {
  // Get the token from the Authorization header (Bearer Token format)
  const token = req.header('Authorization')?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ message: 'Access denied. No token provided.' });
  }

  try {
    const decoded = jwt.verify(token, SECRET_KEY, { algorithms: [ALGORITHM] });
    
    if (!decoded.id) {
      return res.status(401).json({ message: 'Invalid credentials. ID is missing.' });
    }

    req.user = decoded;
    next();
  } catch (error) {
    res.status(400).json({ message: 'Invalid token.' });
  }
};

// Middleware to get current user
const getCurrentUser = async (req, res, next) => {
  const token = req.header('Authorization')?.replace('Bearer ', '');
  const credentialsException = new Error('Could not validate credentials');
  credentialsException.status = 401;
  credentialsException.headers = { 'WWW-Authenticate': 'Bearer' };

  try {
    const tokenData = verifyAccessToken(token, credentialsException);
    const user = await User.findById(tokenData.id);
    if (!user) {
      throw credentialsException;
    }
    req.user = user;
    next();
  } catch (error) {
    res.status(credentialsException.status).json({ message: credentialsException.message });
  }
};


module.exports = { authenticateToken, getCurrentUser };