const express = require("express");
const { ObjectId } = require("mongoose").Types;
const router = express.Router();
const Tag = require("../models/Tag"); // Import the Tag model
const { authenticateToken } = require("../utils/authenticate_token"); // Import the authenticateToken middleware
const logger = require("../utils/logger"); // Utility for logging

// Create a new tag
router.post("/tags", authenticateToken, async (req, res) => {
  const { name } = req.body;
  const currentUser = req.user;

  logger.info(`Creating tag with name: ${name}`);

  try {
    const dbTag = new Tag({
      name,
      user_id: currentUser.id,
    });

    await dbTag.save();

    logger.info(`Tag created successfully: ${dbTag._id} - ${dbTag.name}`);
    return res.status(201).json({
      id: dbTag._id.toString(),
      name: dbTag.name,
    });
  } catch (error) {
    if (error.code === 11000) {
      logger.warn(`Tag with name '${name}' already exists.`);
      return res.status(400).json({ detail: "Tag with this name already exists." });
    }
    logger.error(`Error creating tag: ${error.message}`);
    return res.status(500).json({ detail: "An error occurred while creating the tag." });
  }
});

// Search for tags
router.get("/tags/search", async (req, res) => {
  const query = req.query.query || "";

  logger.info(`Searching tags with query: ${query}`);

  try {
    const tags = query
      ? await Tag.find({ name: { $regex: query, $options: "i" } })
      : await Tag.find();

    logger.info(`Found ${tags.length} tags.`);

    return res.status(200).json(
      tags.map((tag) => ({
        id: tag._id.toString(),
        name: tag.name,
      }))
    );
  } catch (error) {
    logger.error(`Error searching tags: ${error.message}`);
    return res.status(500).json({ detail: "An error occurred while searching for tags." });
  }
});

// Delete a tag
router.delete("/tags/:tagId", authenticateToken, async (req, res) => {
  const { tagId } = req.params;
  const currentUser = req.user;

  logger.info(`Attempting to delete tag with ID: ${tagId}`);

  try {
    if (!ObjectId.isValid(tagId)) {
      logger.warn(`Invalid tag ID: ${tagId}`);
      return res.status(400).json({ detail: "Invalid tag ID." });
    }

    const tagToDelete = await Tag.findOne({ _id: tagId, user_id: currentUser.id });

    if (!tagToDelete) {
      logger.warn(`Tag with ID ${tagId} not found.`);
      return res.status(404).json({ detail: "Tag not found." });
    }

    await tagToDelete.deleteOne();

    logger.info(`Tag with ID ${tagId} deleted successfully.`);
    return res.status(204).send();
  } catch (error) {
    logger.error(`Error deleting tag: ${error.message}`);
    return res.status(500).json({ detail: "An error occurred while deleting the tag." });
  }
});

module.exports = router;
