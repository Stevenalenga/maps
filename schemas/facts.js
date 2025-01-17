const mongoose = require('mongoose');

// FactBase model
const factBaseSchema = new mongoose.Schema({
  description: { type: String, required: true },
});

// Fact model
const factSchema = new mongoose.Schema({
  description: { type: String, required: true },
  created_at: { type: Date, default: Date.now },
});

// FactCreate model (same as FactBase)
const factCreateSchema = new mongoose.Schema({
  description: { type: String, required: true },
});

// FactResponse model
const factResponseSchema = new mongoose.Schema({
  id: { type: String, required: true },
  description: { type: String, required: true },
  location_id: { type: String, required: true },
  user_id: { type: String, required: true },
  tags: [{ type: String }],  // List of strings for tags
  created_at: { type: Date, default: Date.now },
});

// Create Mongoose models
const Fact = mongoose.model('Fact', factSchema);
const FactCreate = mongoose.model('FactCreate', factCreateSchema);
const FactResponse = mongoose.model('FactResponse', factResponseSchema);

// Export models for use in other parts of the app
module.exports = { Fact, FactCreate, FactResponse };
