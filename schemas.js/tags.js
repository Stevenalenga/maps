const mongoose = require('mongoose');

// TagBase model
const tagBaseSchema = new mongoose.Schema({
  name: { type: String, required: true },
});

// TagCreate model (same as TagBase, no additional fields)
const tagCreateSchema = new mongoose.Schema({
  name: { type: String, required: true },
});

// TagResponse model (includes id as a string)
const tagResponseSchema = new mongoose.Schema({
  id: { type: String, required: true },
  name: { type: String, required: true },
});

// Tag model (includes id as an integer)
const tagSchema = new mongoose.Schema({
  id: { type: Number, required: true },
  name: { type: String, required: true },
});

// Create Mongoose models
const Tag = mongoose.model('Tag', tagSchema);
const TagCreate = mongoose.model('TagCreate', tagCreateSchema);
const TagResponse = mongoose.model('TagResponse', tagResponseSchema);

// Export models for use in other parts of the app
module.exports = { Tag, TagCreate, TagResponse };
