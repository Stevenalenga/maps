const express = require("express");
const router = express.Router();
const { Fact, Location, Tag } = require("../models/models"); // Import Mongoose models
const { authenticateToken } = require("../utils/authenticate_token"); // Import the authenticateToken middleware
const logger = require("../utils/logger"); // Logger utility

// Get facts by location ID
router.get("/locations/:locationId/facts", authenticateToken, async (req, res) => {
  const { locationId } = req.params;
  const userId = req.user.id;

  logger.info(`Fetching facts for location ID: ${locationId} by user ID: ${userId}`);

  try {
    const facts = await Fact.find({ locationId }).populate("locationId").exec();
    if (!facts.length) {
      logger.warn(`No facts found for location ID: ${locationId}`);
      return res.status(404).json({ error: "No facts found for this location." });
    }

    logger.info(`Found ${facts.length} facts for location ID: ${locationId}`);
    const response = facts.map((fact) => ({
      id: fact._id,
      description: fact.description,
      locationId: fact.locationId._id,
      userId: fact.userId,
      createdAt: fact.createdAt,
    }));

    res.json(response);
  } catch (err) {
    logger.error(`Error fetching facts: ${err.message}`);
    res.status(500).json({ error: "Internal server error." });
  }
});

// Create a fact for a location
router.post("/locations/:locationId/facts", authenticateToken, async (req, res) => {
  const { locationId } = req.params;
  const { description, tags } = req.body;
  const userId = req.user.id;

  logger.info(`Creating fact for location ID: ${locationId} by user ID: ${userId}`);

  try {
    const location = await Location.findById(locationId);
    if (!location) {
      logger.warn(`Location ID: ${locationId} does not exist`);
      return res.status(404).json({ error: "Location not found." });
    }

    // Validate tags
    const tagObjects = [];
    for (const tag of tags) {
      const tagObject = await Tag.findOne({ name: tag });
      if (!tagObject) {
        logger.warn(`Tag '${tag}' not found.`);
        return res.status(400).json({ error: `Tag '${tag}' not found.` });
      }
      tagObjects.push(tagObject);
    }

    // Create and save the fact
    const newFact = new Fact({
      description,
      locationId,
      userId,
      tags: tagObjects,
    });
    await newFact.save();

    logger.info(`Fact created with ID: ${newFact._id} for location ID: ${locationId}`);
    res.status(201).json({
      id: newFact._id,
      description: newFact.description,
      locationId: newFact.locationId,
      userId: newFact.userId,
      createdAt: newFact.createdAt,
    });
  } catch (err) {
    logger.error(`Error creating fact: ${err.message}`);
    res.status(500).json({ error: "Internal server error." });
  }
});

// Delete a fact by ID
router.delete("/facts/:factId", authenticateToken, async (req, res) => {
  const { factId } = req.params;
  const userId = req.user.id;

  logger.info(`Attempting to delete fact with ID: ${factId} by user ID: ${userId}`);

  try {
    const fact = await Fact.findOneAndDelete({ _id: factId, userId });
    if (!fact) {
      logger.warn(`Fact ID: ${factId} does not exist or not owned by user ID: ${userId}`);
      return res.status(404).json({ error: "Fact not found." });
    }

    logger.info(`Fact with ID: ${factId} deleted`);
    res.status(204).send();
  } catch (err) {
    logger.error(`Error deleting fact: ${err.message}`);
    res.status(500).json({ error: "Internal server error." });
  }
});

// Update a fact by ID
router.put("/locations/:locationId/facts/:factId", authenticateToken, async (req, res) => {
  const { locationId, factId } = req.params;
  const { description } = req.body;
  const userId = req.user.id;

  logger.info(`Updating fact with ID: ${factId} for location ID: ${locationId} by user ID: ${userId}`);

  try {
    const location = await Location.findById(locationId);
    if (!location) {
      logger.warn(`Location ID ${locationId} does not exist.`);
      return res.status(404).json({ error: "Location not found." });
    }

    const fact = await Fact.findOneAndUpdate(
      { _id: factId, locationId, userId },
      { description },
      { new: true }
    );
    if (!fact) {
      logger.warn(`Fact with ID ${factId} not found for location ID ${locationId}`);
      return res.status(404).json({ error: "Fact not found." });
    }

    logger.info(`Fact with ID ${factId} updated successfully for location ID: ${locationId}`);
    res.json({
      id: fact._id,
      description: fact.description,
      locationId: fact.locationId,
      userId: fact.userId,
      createdAt: fact.createdAt,
    });
  } catch (err) {
    logger.error(`Error updating fact: ${err.message}`);
    res.status(500).json({ error: "Internal server error." });
  }
});

module.exports = router;
