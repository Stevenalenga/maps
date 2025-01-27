const mongoose = require('mongoose');
const Joi = require('joi');

// User Schema
const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  email: { 
    type: String, 
    required: true, 
    unique: true,
    validate: {
      validator: function (email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
      },
      message: props => `${props.value} is not a valid email!`
    }
  },
  password: { type: String, required: true },
  created_at: { type: Date, default: Date.now },
});

// Tag Schema
const tagSchema = new mongoose.Schema({
  name: { type: String, required: true, unique: true },
  user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  created_at: { type: Date, default: Date.now },
});

// Location Schema
const locationSchema = new mongoose.Schema({
  name: { type: String, required: true },
  latitude: { type: Number, required: true },
  longitude: { type: Number, required: true },
  description: { type: String, required: true }, // Ensure no unique constraint
  user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  tags: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Tag' }],
  created_at: { type: Date, default: Date.now },
});


// Friendship Schema
const friendshipSchema = new mongoose.Schema({
  user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  friend_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  created_at: { type: Date, default: Date.now },
});

// Fact Schema
const factSchema = new mongoose.Schema({
  description: { type: String, required: true },
  location_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Location', required: true },
  user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  tags: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Tag' }],
  created_at: { type: Date, default: Date.now },
});

// Create Mongoose models
const User = mongoose.model('User', userSchema);
const Tag = mongoose.model('Tag', tagSchema);
const Location = mongoose.model('Location', locationSchema);
const Friendship = mongoose.model('Friendship', friendshipSchema);
const Fact = mongoose.model('Fact', factSchema);

// Export models
module.exports = { User, Tag, Location, Friendship, Fact };