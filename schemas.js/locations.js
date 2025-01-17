const mongoose = require('mongoose');

// LocationBase model
const locationBaseSchema = new mongoose.Schema({
  name: { type: String, required: true },
  latitude: { type: Number, required: true },
  longitude: { type: Number, required: true },
  description: { type: String, required: true },
});

// LocationCreate model (extends LocationBase and includes tags)
const locationCreateSchema = new mongoose.Schema({
  name: { type: String, required: true },
  latitude: { type: Number, required: true },
  longitude: { type: Number, required: true },
  description: { type: String, required: true },
  tags: [{ type: String }],  // Array of tags
});

// Location model (includes owner reference to User)
const locationSchema = new mongoose.Schema({
  name: { type: String, required: true },
  latitude: { type: Number, required: true },
  longitude: { type: Number, required: true },
  description: { type: String, required: true },
  created_at: { type: Date, default: Date.now },
  owner: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },  // Reference to User model
});

// LocationSchema model (includes tags and user reference)
const locationResponseSchema = new mongoose.Schema({
  id: { type: String, required: true },
  user_id: { type: String, required: true },  // User ID as a string
  created_at: { type: Date, default: Date.now },
  tags: [{ type: String }],  // Array of tags
});

// Create Mongoose models
const Location = mongoose.model('Location', locationSchema);
const LocationCreate = mongoose.model('LocationCreate', locationCreateSchema);
const LocationResponse = mongoose.model('LocationResponse', locationResponseSchema);

// Export models for use in other parts of the app
module.exports = { Location, LocationCreate, LocationResponse };
