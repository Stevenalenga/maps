const jwt = require('jsonwebtoken');
const { User } = require('../models/models');  // Assuming User is your Mongoose model
const { tokenDataSchema } = require('../schemas/auth');  // Assuming TokenData schema
const dotenv = require('dotenv');
const { Unauthorized } = require('http-errors');
const logger = require('pino')();  // Logger setup

dotenv.config();

// JWT Configuration
const SECRET_KEY = process.env.SECRET_KEY || 'your_secret_key';
const ALGORITHM = process.env.ALGORITHM || 'HS256';
const ACCESS_TOKEN_EXPIRE_MINUTES = parseInt(process.env.ACCESS_TOKEN_EXPIRE_MINUTES) || 30;

const createAccessToken = (data) => {
  const toEncode = { ...data };
  const expire = Math.floor(Date.now() / 1000) + ACCESS_TOKEN_EXPIRE_MINUTES * 60;
  toEncode.exp = expire;
  const encodedJwt = jwt.sign(toEncode, SECRET_KEY, { algorithm: ALGORITHM });
  return encodedJwt;
};

const oauth2Scheme = 'Bearer';  // For token validation

// Function to get current user based on JWT token
async function getCurrentUser(req, res, next) {
  const token = req.headers.authorization && req.headers.authorization.startsWith(oauth2Scheme)
    ? req.headers.authorization.split(' ')[1]
    : null;

  if (!token) {
    return next(new Unauthorized('Could not validate credentials'));
  }

  try {
    const payload = jwt.verify(token, SECRET_KEY, { algorithms: [ALGORITHM], audience: 'fastapi-users' });
    const username = payload.sub;

    if (!username || typeof username !== 'string') {
      logger.error("Invalid or missing 'sub' claim in token");
      throw new Unauthorized('Could not validate credentials');
    }

    const tokenDataSchema = new tokenDataSchema({ id });

    // Retrieve the user from the database
    const user = await User.findOne({ id: tokenDataSchema.id });

    if (!user) {
      logger.warn(`User not found for username: ${tokenDataSchema.id}`);
      throw new Unauthorized('Could not validate credentials');
    }

    logger.info(`Authenticated user: ${user._id}`);
    req.user = user;  // Attach user to request object

    next();
  } catch (err) {
    if (err instanceof jwt.TokenExpiredError) {
      logger.error(`Expired token error: ${err}`);
      return next(new Unauthorized('Token has expired'));
    }
    
    if (err instanceof jwt.JsonWebTokenError) {
      logger.error(`JWT error: ${err}`);
      return next(new Unauthorized('Could not validate credentials'));
    }

    logger.error(`Error authenticating user: ${err.message}`);
    return next(new Unauthorized('Invalid authentication credentials'));
  }
}

module.exports = { getCurrentUser, createAccessToken };
