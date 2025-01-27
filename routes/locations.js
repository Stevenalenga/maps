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
    // Check if the user has already created a location with the same details
    const existingLocation = await Location.findOne({ user_id: userId, name, latitude, longitude, description });
    if (existingLocation) {
      logger.warn(`User ${userId} already has a location with the same details`);
      return res.status(400).json({ error: "You have already created a location with the same details." });
    }

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
      tags: newLocation.tags,
    });
  } catch (error) {
    logger.error(`Error creating location for user ${userId}: ${error.message}`);
    res.status(500).json({ message: "Error creating location" });
  }
});

// Update a location
router.put("/locations/:locationId", authenticateToken, async (req, res) => {
  const userId = req.user.id;
  const { locationId } = req.params;
  const { name, latitude, longitude, description, tags } = req.body;

  logger.info(`Updating location ID: ${locationId} for user: ${userId}`);

  try {
    const existingLocation = await Location.findOne({ _id: locationId, user_id: userId }); // Ensure correct field name
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
    logger.info(`Location ID: ${locationId} updated successfully for user: ${userId}`);
    res.status(200).json({ message: "Location updated successfully" });
  } catch (error) {
    logger.error(`Error updating location ID ${locationId} for user ${userId}: ${error.message}`);
    res.status(500).json({ message: "Error updating location" });
  }
});

// Delete a location
router.delete("/locations/:locationId", authenticateToken, async (req, res) => {
  const userId = req.user.id;
  const { locationId } = req.params;

  logger.info(`Attempting to delete location ID: ${locationId} for user: ${userId}`);

  try {
    const location = await Location.findOneAndDelete({ _id: locationId, user_id: userId }); // Ensure correct field name
    if (!location) {
      logger.warn(`Location ID ${locationId} not found for user: ${userId}`);
      return res.status(404).json({ error: "Location not found." });
    }

    logger.info(`Location ID ${locationId} deleted successfully for user: ${userId}`);
    res.status(204).send();
  } catch (error) {
    logger.error(`Error deleting location ID ${locationId} for user ${userId}: ${error.message}`);
    res.status(500).json({ message: "Error deleting location" });
  }
});


// Count user locations
router.get("/locations/count", authenticateToken, async (req, res) => {
  const userId = req.user.id;

  logger.info(`Counting locations for user: ${userId}`);

  try {
    const count = await Location.countDocuments({ user_id: userId }); // Ensure correct field name
    res.status(200).json({ count });
  } catch (error) {
    logger.error(`Error counting locations for user ${userId}: ${error.message}`);
    res.status(500).json({ message: "Error counting locations" });
  }
});


// Fetch all locations for all users
router.get("/locations/all", authenticateToken, async (req, res) => {
  logger.info(`Fetching all locations for all users`);

  try {
    const allLocations = await Location.find().populate("tags");
    logger.info(`Retrieved ${allLocations.length} locations for all users`);

    const response = allLocations.map((location) => ({
      id: location._id,
      name: location.name,
      latitude: location.latitude,
      longitude: location.longitude,
      description: location.description,
      user_id: location.user_id,
      tags: location.tags,
    }));

    res.status(200).json(response);
  } catch (error) {
    logger.error(`Error fetching all locations: ${error.message}`);
    res.status(500).json({ message: "Error fetching all locations" });
  }
});

module.exports = router;
