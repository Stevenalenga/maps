const express = require("express");
const mongoose = require("mongoose");
const { Location, Fact, Tag, User } = require("../models/models"); // Import Mongoose models
const { authenticateToken } = require("../utils/authenticate_token");
const logger = require("../utils/logger");

const router = express.Router();

// Fetch user locations
router.get("/locations", authenticateToken, async (req, res) => {
  const userId = req.user.id;
  logger.info(`Fetching locations for user: ${userId}`);

  try {
    const userLocations = await Location.find({ user_id: userId }).populate("tags");  // Change this line
    logger.info(`Retrieved ${userLocations.length} locations for user: ${userId}`);

    const response = userLocations.map((location) => ({
      id: location._id,
      name: location.name,
      latitude: location.latitude,
      longitude: location.longitude,
      description: location.description,
      //tags: location.tags,
    }));

    res.status(200).json(response);
  } catch (error) {
    logger.error(`Error fetching locations for user ${userId}: ${error.message}`);
    res.status(500).json({ message: "Error fetching locations" });
  }
});


// Create a new location
router.post("/locations", authenticateToken, async (req, res) => {
  const userId = req.user.id;
  const { name, latitude, longitude, description, tags } = req.body;

  logger.info(`Creating new location for user: ${userId}`);

  try {
    const tagObjects = await Tag.find({ name: { $in: tags } });

    const newLocation = new Location({
      name,
      latitude,
      longitude,
      description,
      user_id: userId,
      tags: tagObjects,
    });
    await newLocation.save();

    const newFact = new Fact({
      description,
      location_id: newLocation._id,
      user_id: userId,
    });
    await newFact.save();

    logger.info(`Location created with ID: ${newLocation._id} for user: ${userId}`);
    res.status(201).json({
      id: newLocation._id,
      name: newLocation.name,
      latitude: newLocation.latitude,
      longitude: newLocation.longitude,
      description: newLocation.description,
      userId,
      createdAt: newLocation.createdAt,
      tags: tagObjects.map((tag) => tag.name),
    });
  } catch (err) {
    logger.error(`Error creating location for user ${userId}: ${err.message}`);
    if (err.code === 11000) {
      return res.status(400).json({ error: "Location with the same latitude and longitude already exists." });
    }
    res.status(500).json({ error: "An unexpected error occurred." });
  }
});

// Update a location
router.put("/locations/:locationId", authenticateToken, async (req, res) => {
  const userId = req.user.id;
  const { locationId } = req.params;
  const { name, latitude, longitude, description, tags } = req.body;

  logger.info(`Updating location ID: ${locationId} for user: ${userId}`);

  try {
    const existingLocation = await Location.findOne({ _id: locationId, userId });
    if (!existingLocation) {
      logger.warn(`Location ID ${locationId} not found for user: ${userId}`);
      return res.status(404).json({ error: "Location not found." });
    }

    const tagObjects = await Tag.find({ name: { $in: tags } });

    existingLocation.name = name;
    existingLocation.latitude = latitude;
    existingLocation.longitude = longitude;
    existingLocation.description = description;
    existingLocation.tags = tagObjects;

    await existingLocation.save();

    await Fact.updateMany(
      { locationId: existingLocation._id },
      { description: existingLocation.description }
    );

    logger.info(`Location updated with ID: ${existingLocation._id} for user: ${userId}`);
    res.json({
      id: existingLocation._id,
      name: existingLocation.name,
      latitude: existingLocation.latitude,
      longitude: existingLocation.longitude,
      description: existingLocation.description,
      userId,
      createdAt: existingLocation.createdAt,
      tags: tagObjects.map((tag) => tag.name),
    });
  } catch (err) {
    logger.error(`Error updating location ID ${locationId} for user ${userId}: ${err.message}`);
    res.status(500).json({ error: "An unexpected error occurred." });
  }
});

// Delete a location
router.delete("/locations/:locationId", authenticateToken, async (req, res) => {
  const userId = req.user.id;
  const { locationId } = req.params;

  logger.info(`Attempting to delete location ID: ${locationId} for user: ${userId}`);

  try {
    const location = await Location.findOneAndDelete({ _id: locationId, userId });
    if (!location) {
      logger.warn(`Location ID ${locationId} not found for user: ${userId}`);
      return res.status(404).json({ error: "Location not found." });
    }

    logger.info(`Location ID ${locationId} deleted successfully for user: ${userId}`);
    res.status(204).send();
  } catch (err) {
    logger.error(`Error deleting location ID ${locationId} for user ${userId}: ${err.message}`);
    res.status(500).json({ error: "An unexpected error occurred." });
  }
});

// Count user locations
router.get("/locations/count", authenticateToken, async (req, res) => {
  const userId = req.user.id;

  logger.info(`Counting locations for user: ${userId}`);

  try {
    const count = await Location.countDocuments({ userId });
    logger.info(`User ${userId} has ${count} locations.`);
    res.json(count);
  } catch (err) {
    logger.error(`Error counting locations for user ${userId}: ${err.message}`);
    res.status(500).json({ error: "An error occurred while counting locations." });
  }
});

module.exports = router;
