const express = require("express")
const { ObjectId } = require("mongoose").Types
const router = express.Router()
const { Tag } = require("../models/models") // Correct import statement
const { authenticateToken } = require("../utils/authenticate_token")
const logger = require("../utils/logger")

// Create a new tag
router.post("/tags", authenticateToken, async (req, res) => {
  const { name } = req.body
  const currentUser = req.user

  logger.info(`Creating tag with name: ${name}`)

  try {
    const dbTag = new Tag({
      name,
      user_id: currentUser.id,
    })

    await dbTag.save()

    logger.info(`Tag created successfully: ${dbTag._id} - ${dbTag.name}`)
    return res.status(201).json({
      id: dbTag._id.toString(),
      name: dbTag.name,
    })
  } catch (error) {
    if (error.code === 11000) {
      logger.warn(`Tag with name '${name}' already exists.`)
      return res.status(400).json({ detail: "Tag with this name already exists." })
    }
    if (error.name === "ValidationError") {
      logger.warn(`Validation error: ${error.message}`)
      return res.status(400).json({ detail: error.message })
    }
    logger.error(`Error creating tag: ${error.message}`)
    return res.status(500).json({ detail: "An error occurred while creating the tag." })
  }
})

// Search for tags
router.get("/tags/search", async (req, res) => {
  const query = req.query.query || ""

  logger.info(`Searching tags with query: ${query}`)

  try {
    const tags = await Tag.find(query ? { name: { $regex: query, $options: "i" } } : {}).exec()

    logger.info(`Found ${tags.length} tags.`)

    return res.status(200).json(
      tags.map((tag) => ({
        id: tag._id.toString(),
        name: tag.name,
      })),
    )
  } catch (error) {
    logger.error(`Error searching tags: ${error.message}`)
    return res.status(500).json({ detail: "An error occurred while searching for tags." })
  }
})

// Delete a tag
router.delete("/tags/:tagId", authenticateToken, async (req, res) => {
  const { tagId } = req.params
  const currentUser = req.user

  logger.info(`Attempting to delete tag with ID: ${tagId}`)

  try {
    if (!ObjectId.isValid(tagId)) {
      logger.warn(`Invalid tag ID: ${tagId}`)
      return res.status(400).json({ detail: "Invalid tag ID." })
    }

    const deletedTag = await Tag.findOneAndDelete({ _id: tagId, user_id: currentUser.id })

    if (!deletedTag) {
      logger.warn(`Tag with ID ${tagId} not found or user not authorized.`)
      return res.status(404).json({ detail: "Tag not found or you're not authorized to delete it." })
    }

    logger.info(`Tag with ID ${tagId} deleted successfully.`)
    return res.status(204).send()
  } catch (error) {
    logger.error(`Error deleting tag: ${error.message}`)
    return res.status(500).json({ detail: "An error occurred while deleting the tag." })
  }
})

// Update a tag
router.put("/tags/:tagId", authenticateToken, async (req, res) => {
  const { tagId } = req.params
  const { name } = req.body
  const currentUser = req.user

  logger.info(`Attempting to update tag with ID: ${tagId}`)

  try {
    if (!ObjectId.isValid(tagId)) {
      logger.warn(`Invalid tag ID: ${tagId}`)
      return res.status(400).json({ detail: "Invalid tag ID." })
    }

    if (!name || typeof name !== "string" || name.trim() === "") {
      logger.warn(`Invalid tag name provided for update: ${name}`)
      return res.status(400).json({ detail: "Invalid tag name. Name must be a non-empty string." })
    }

    const updatedTag = await Tag.findOneAndUpdate(
      { _id: tagId, user_id: currentUser.id },
      { name: name.trim() },
      { new: true, runValidators: true },
    )

    if (!updatedTag) {
      logger.warn(`Tag with ID ${tagId} not found or user not authorized.`)
      return res.status(404).json({ detail: "Tag not found or you're not authorized to update it." })
    }

    logger.info(`Tag updated successfully: ${updatedTag._id} - ${updatedTag.name}`)
    return res.status(200).json({
      id: updatedTag._id.toString(),
      name: updatedTag.name,
    })
  } catch (error) {
    if (error.code === 11000) {
      logger.warn(`Tag with name '${name}' already exists.`)
      return res.status(400).json({ detail: "Tag with this name already exists." })
    }
    if (error.name === "ValidationError") {
      logger.warn(`Validation error: ${error.message}`)
      return res.status(400).json({ detail: error.message })
    }
    logger.error(`Error updating tag: ${error.message}`)
    return res.status(500).json({ detail: "An error occurred while updating the tag." })
  }
})

module.exports = router
