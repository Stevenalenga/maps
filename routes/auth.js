const express = require("express");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const mongoose = require("mongoose");
const dotenv = require("dotenv");
const bodyParser = require("body-parser");
const { User } = require("../models/models");
const logger = require("../utils/logger");


dotenv.config();
const router = express.Router();

// Load environment variables
const SECRET_KEY = process.env.SECRET_KEY || "your_secret_key";
const ALGORITHM = process.env.ALGORITHM || "HS256";
const ACCESS_TOKEN_EXPIRE_MINUTES = parseInt(process.env.ACCESS_TOKEN_EXPIRE_MINUTES) || 30;

// Middleware to parse form data and JSON
router.use(bodyParser.urlencoded({ extended: true }));
router.use(bodyParser.json());

// Utility Functions
const createAccessToken = (data, expiresIn = ACCESS_TOKEN_EXPIRE_MINUTES) => {
  const payload = {
    ...data,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + expiresIn * 60,
    aud: "express-users",
  };
  return jwt.sign(payload, SECRET_KEY, { algorithm: ALGORITHM });
};

// Routes
/**
 * @route POST /api/v3/signup
 * @desc User Signup
 */
router.post("/signup", async (req, res) => {
  const { username, email, password } = req.body;

  try {
    // Check if username or email already exists
    const existingUser = await User.findOne({ username });
    if (existingUser) return res.status(400).json({ message: "Username already exists" });

    const existingEmail = await User.findOne({ email });
    if (existingEmail) return res.status(400).json({ message: "Email already exists" });

    // Hash password and save user
    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = new User({ username, email, password: hashedPassword });
    await newUser.save();

    res.status(201).json({ username: newUser.username, email: newUser.email });
  } catch (err) {
    console.error("Error during signup:", err);
    res.status(500).json({ message: "Internal Server Error" });
  }
});

/**
 * @route POST /api/v3/login
 * @desc User Login
 */
router.post("/login", async (req, res) => {
  const { username, password } = req.body;

  try {
    // Check if user exists by username or email
    const user = await User.findOne({ $or: [{ username }, { email: username }] });
    if (!user || !(await bcrypt.compare(password, user.password))) {
      return res.status(401).json({ message: "Invalid username or password" });
    }

    // Generate access token
    const accessToken = createAccessToken({ sub: user.username });
    res.status(200).json({ access_token: accessToken, token_type: "bearer" });
    logger.info(`User ${user.username} logged in successfully`);
  } catch (err) {
    console.error("Error during login:", err);
    res.status(500).json({ message: "Internal Server Error" });
  }
});

module.exports = router;
