const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const { User } = require("../models/models");
const { authenticateToken } = require("../utils/authenticate_token");

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
    return res.status(403).json({ detail: "Not authorized to view this user" });
  }

  try {
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ detail: "User not found" });
    }

    res.json({ username: user.username, email: user.email });
  } catch (error) {
    console.error(`Error fetching user ${userId}:`, error);
    res.status(500).json({ detail: "An error occurred while fetching the user" });
  }
});

// Update user
router.put("/update/:userId", authenticateToken, async (req, res) => {
  const { userId } = req.params;
  const { username, email, password } = req.body;

  if (req.user.id !== userId) {
    return res.status(403).json({ detail: "Not authorized to update this user" });
  }

  try {
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ detail: "User not found" });
    }

    // Update user fields
    user.username = username;
    user.email = email;
    if (password) {
      user.password = await hashPassword(password);
    }

    await user.save();
    console.log(`User updated successfully: ${user.username} with email: ${user.email}`);
    res.json({ username: user.username, email: user.email });
  } catch (error) {
    console.error(`Error updating user ${userId}:`, error);
    res.status(500).json({ detail: "An error occurred while updating the user" });
  }
});

// Delete user
router.delete("/delete/:userId", authenticateToken, async (req, res) => {
  const { userId } = req.params;

  if (req.user.id !== userId) {
    return res.status(403).json({ detail: "Not authorized to delete this user" });
  }

  try {
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ detail: "User not found" });
    }

    await User.deleteOne({ _id: userId });
    console.log(`User deleted successfully: ${user.username}`);
    res.json({ detail: "User deleted successfully" });
  } catch (error) {
    console.error(`Error deleting user ${userId}:`, error);
    res.status(500).json({ detail: "An error occurred while deleting the user" });
  }
});

module.exports = router;