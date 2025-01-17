const express = require("express");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const mongoose = require("mongoose");
const dotenv = require("dotenv");
const bodyParser = require("body-parser");
const { User } = require("../models/models");
const logger = require("../utils/logger");
const { createAccessToken } = require("../utils/auth_utils");

dotenv.config();
const router = express.Router();

// Middleware to parse form data and JSON
router.use(bodyParser.urlencoded({ extended: true }));
router.use(bodyParser.json());

// Middleware to log responses
router.use((req, res, next) => {
  const originalSend = res.send;
  res.send = function (body) {
    logger.info(`Response: ${res.statusCode} - ${body}`);
    originalSend.call(this, body);
  };
  next();
});

/**
 * @route POST /api/v3/signup
 * @desc User Signup
 */
router.post("/signup", async (req, res) => {
  const { username, email, password } = req.body;

  try {
    // Check if username or email already exists
    const existingUser = await User.findOne({ $or: [{ username }, { email }] });
    if (existingUser) {
      return res.status(400).json({ message: "Username or email already exists" });
    }

    // Hash the password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create a new user
    const user = new User({ username, email, password: hashedPassword });
    await user.save();

    // Create access token
    const token = createAccessToken({ id: user._id });

    res.status(201).json({ access_token: token, token_type: "bearer" });
    logger.info(`User ${user.username} signed up successfully`);
  } catch (err) {
    logger.error("Error during signup:", err);
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

    // Create access token
    const token = createAccessToken({ id: user._id });

    res.status(200).json({ access_token: token, token_type: "bearer" });
    logger.info(`User ${user.username} logged in successfully`);
  } catch (err) {
    logger.error("Error during login:", err);
    res.status(500).json({ message: "Internal Server Error" });
  }
});

module.exports = router;