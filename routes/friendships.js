const express = require("express");
const mongoose = require("mongoose");
const { Friendship, User } = require("../models/models"); // Import Mongoose models
const { authenticateToken } = require("../utils/authenticate_token");
const logger = require("../utils/logger");

const router = express.Router();

// Create a new friendship (follow)
router.post("/friendships", authenticateToken, async (req, res) => {
  const userId = req.user.id;
  const { friendId } = req.body;

  logger.info(`User ${userId} is attempting to follow user ${friendId}`);

  try {
    // Check if the friendship already exists
    const existingFriendship = await Friendship.findOne({ user_id: userId, friend_id: friendId });
    if (existingFriendship) {
      logger.warn(`User ${userId} already follows user ${friendId}`);
      return res.status(400).json({ error: "You already follow this user." });
    }

    const newFriendship = new Friendship({
      user_id: userId,
      friend_id: friendId,
      status: 'pending',
    });
    await newFriendship.save();

    logger.info(`User ${userId} successfully followed user ${friendId}`);
    res.status(201).json({ message: "Follow request sent." });
  } catch (error) {
    logger.error(`Error creating follow request for user ${userId}: ${error.message}`);
    res.status(500).json({ message: "Error creating follow request." });
  }
});

// Accept a friendship request
router.put("/friendships/accept", authenticateToken, async (req, res) => {
  const userId = req.user.id;
  const { friendId } = req.body;

  logger.info(`User ${userId} is attempting to accept follow request from user ${friendId}`);

  try {
    // Find the pending friendship request
    const pendingFriendship = await Friendship.findOne({ user_id: friendId, friend_id: userId, status: 'pending' });
    if (!pendingFriendship) {
      logger.warn(`No pending follow request from user ${friendId} to user ${userId}`);
      return res.status(404).json({ error: "No pending follow request found." });
    }

    // Update the status to accepted
    pendingFriendship.status = 'accepted';
    await pendingFriendship.save();

    // Create the reciprocal friendship
    const reciprocalFriendship = new Friendship({
      user_id: userId,
      friend_id: friendId,
      status: 'accepted',
    });
    await reciprocalFriendship.save();

    logger.info(`User ${userId} accepted follow request from user ${friendId}`);
    res.status(200).json({ message: "Friendship accepted." });
  } catch (error) {
    logger.error(`Error accepting follow request for user ${userId}: ${error.message}`);
    res.status(500).json({ message: "Error accepting follow request." });
  }
});

// Fetch friendships of a specific user
router.get("/friendships/user/:userId", authenticateToken, async (req, res) => {
  const { userId } = req.params;
  logger.info(`Fetching friendships for user: ${userId}`);

  try {
    const friendships = await Friendship.find({ user_id: userId, status: 'accepted' }).populate("friend_id");
    logger.info(`Retrieved ${friendships.length} friendships for user: ${userId}`);

    const response = friendships.map((friendship) => ({
      id: friendship._id,
      user_id: friendship.user_id,
      friend_id: friendship.friend_id,
      created_at: friendship.created_at,
    }));

    res.status(200).json(response);
  } catch (err) {
    logger.error(`Error fetching friendships for user ${userId}: ${err.message}`);
    return res.status(500).json({ error: "An error occurred while fetching friendships." });
  }
});

// Get friendship count for a specific user
router.get("/friendships/user/:userId/count", authenticateToken, async (req, res) => {
  const { userId } = req.params;
  logger.info(`Counting friendships for user: ${userId}`);

  try {
    const count = await Friendship.countDocuments({ user_id: userId, status: 'accepted' });
    logger.info(`User ${userId} has ${count} friendships`);

    res.status(200).json({ count });
  } catch (err) {
    logger.error(`Error counting friendships for user ${userId}: ${err.message}`);
    return res.status(500).json({ error: "An error occurred while counting friendships." });
  }
});

// Delete friendship
router.delete("/friendships/:friendshipId", authenticateToken, async (req, res) => {
  const { friendshipId } = req.params;
  const userId = req.user.id;

  logger.info(`Attempting to delete friendship with ID: ${friendshipId}`);

  try {
    // Validate ObjectId
    if (!mongoose.Types.ObjectId.isValid(friendshipId)) {
      logger.warn(`Invalid friendship ID: ${friendshipId}`);
      return res.status(400).json({ error: "Invalid friendship ID." });
    }

    // Find and delete the friendship
    const friendshipToDelete = await Friendship.findOneAndDelete({ _id: friendshipId, user_id: userId });
    if (!friendshipToDelete) {
      logger.warn(`Friendship ID ${friendshipId} not found for user: ${userId}`);
      return res.status(404).json({ error: "Friendship not found." });
    }

    logger.info(`Friendship ID ${friendshipId} deleted successfully for user: ${userId}`);
    res.status(204).send();
  } catch (err) {
    logger.error(`Error deleting friendship ID ${friendshipId} for user ${userId}: ${err.message}`);
    res.status(500).json({ error: "Error deleting friendship" });
  }
});

module.exports = router;