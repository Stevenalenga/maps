const express = require("express");
const router = express.Router();
const { User, Friendship } = require("../models/models"); // Import Mongoose models
const { authenticateToken } = require("../utils/authenticate_token"); // Import the authenticateToken middleware
const logger = require("../utils/logger"); // Logger utility
const mongoose = require("mongoose");

// Create friendship
router.post("/friendships/:friendId", authenticateToken, async (req, res) => {
  const { friendId } = req.params;
  const userId = req.user.id;

  logger.info(`Creating friendship for user: ${userId} with friend: ${friendId}`);

  try {
    // Ensure the friend exists
    const friend = await User.findById(friendId);
    if (!friend) {
      logger.warn(`Friend with ID ${friendId} does not exist.`);
      return res.status(404).json({ error: "Friend not found." });
    }

    // Check if the friendship already exists
    const existingFriendship = await Friendship.findOne({
      userId,
      friendId,
    });
    if (existingFriendship) {
      logger.warn(`Friendship already exists between user ${userId} and friend ${friendId}.`);
      return res.status(400).json({ error: "Friendship already exists." });
    }

    // Create and save the friendship
    const newFriendship = new Friendship({
      userId,
      friendId,
    });
    await newFriendship.save();

    logger.info(`Friendship created successfully: ${newFriendship._id}`);
    return res.status(201).json({
      id: newFriendship._id,
      userId: newFriendship.userId,
      friendId: newFriendship.friendId,
      createdAt: newFriendship.createdAt,
    });
  } catch (err) {
    logger.error(`Error creating friendship: ${err.message}`);
    return res.status(500).json({ error: "An error occurred while creating the friendship." });
  }
});

// Get friendships
router.get("/friendships", authenticateToken, async (req, res) => {
  const userId = req.user.id;

  logger.info(`Fetching friendships for user: ${userId}`);

  try {
    const friendships = await Friendship.find({ userId }).populate("friendId").exec();

    logger.info(`Found ${friendships.length} friendships.`);
    return res.json(
      friendships.map((friendship) => ({
        id: friendship._id,
        userId: friendship.userId,
        friendId: friendship.friendId._id,
        createdAt: friendship.createdAt,
      }))
    );
  } catch (err) {
    logger.error(`Error fetching friendships: ${err.message}`);
    return res.status(500).json({ error: "An error occurred while fetching friendships." });
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
    const friendshipToDelete = await Friendship.findOneAndDelete({
      _id: friendshipId,
      userId,
    });

    if (!friendshipToDelete) {
      logger.warn(`Friendship with ID ${friendshipId} not found.`);
      return res.status(404).json({ error: "Friendship not found." });
    }

    logger.info(`Friendship with ID ${friendshipId} deleted successfully.`);
    return res.status(204).send();
  } catch (err) {
    logger.error(`Error deleting friendship: ${err.message}`);
    return res.status(500).json({ error: "An error occurred while deleting the friendship." });
  }
});

module.exports = router;
