const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const { User, Location, Friendship } = require("../models/models");
const { authenticateToken } = require("../utils/authenticate_token");
const logger = require("../utils/logger");

const router = express.Router();

// Utility function for hashing passwords
const hashPassword = async (password) => {
  const salt = await bcrypt.genSalt(10);
  return await bcrypt.hash(password, salt);
};

// Get user details
router.get("/:userId", authenticateToken, async (req, res) => {
  const { userId } = req.params;

  if (req.user.id !== userId) {
    return res.status(403).json({ message: "Access denied." });
  }

  try {
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ message: "User not found." });
    }

    res.status(200).json(user);
  } catch (error) {
    res.status(500).json({ message: "Error fetching user details." });
  }
});

// Update user
router.put("/update/:userId", authenticateToken, async (req, res) => {
  const { userId } = req.params;
  const { username, email, password } = req.body;

  if (req.user.id !== userId) {
    return res.status(403).json({ message: "Access denied." });
  }

  try {
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ message: "User not found." });
    }

    user.username = username || user.username;
    user.email = email || user.email;
    if (password) {
      user.password = await hashPassword(password);
    }

    await user.save();
    res.status(200).json({ message: "User updated successfully." });
  } catch (error) {
    res.status(500).json({ message: "Error updating user." });
  }
});

// Delete user
router.delete("/delete/:userId", authenticateToken, async (req, res) => {
  const { userId } = req.params;

  if (req.user.id !== userId) {
    return res.status(403).json({ message: "Access denied." });
  }

  try {
    const user = await User.findByIdAndDelete(userId);
    if (!user) {
      return res.status(404).json({ message: "User not found." });
    }

    res.json({ detail: "User deleted successfully" });
  } catch (error) {
    console.error(`Error deleting user ${userId}:`, error);
    res.status(500).json({ detail: "An error occurred while deleting the user" });
  }
});

// Search user by username and include location and friendship counts
router.get("/search/:username", authenticateToken, async (req, res) => {
  const { username } = req.params;

  logger.info(`Searching for user with username: ${username}`);

  try {
    const user = await User.findOne({ username });
    if (!user) {
      logger.warn(`User with username ${username} not found`);
      return res.status(404).json({ message: "User not found." });
    }

    const locationCount = await Location.countDocuments({ user_id: user._id });
    const friendshipCount = await Friendship.countDocuments({ user_id: user._id });

    logger.info(`User with username ${username} found. Location count: ${locationCount}, Friendship count: ${friendshipCount}`);

    res.status(200).json({
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        created_at: user.created_at,
      },
      locationCount,
      friendshipCount,
    });
  } catch (error) {
    logger.error(`Error searching for user with username ${username}: ${error.message}`);
    res.status(500).json({ message: "Error searching for user." });
  }
});

module.exports = router;