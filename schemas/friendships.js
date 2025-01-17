const mongoose = require('mongoose');

// FriendshipBase model
const friendshipBaseSchema = new mongoose.Schema({
  user_id: { type: Number, required: true },
});

// FriendshipCreate model (inherits from FriendshipBase)
const friendshipCreateSchema = new mongoose.Schema({
  user_id: { type: Number, required: true },
  friend_id: { type: Number, required: true },
});

// Friendship model
const friendshipSchema = new mongoose.Schema({
  user_id: { type: Number, required: true },
  friend_id: { type: Number, required: true },
  created_at: { type: Date, default: Date.now },
});

// FriendshipResponse model
const friendshipResponseSchema = new mongoose.Schema({
  id: { type: String, required: true },
  user_id: { type: String, required: true },
  friend_id: { type: String, required: true },
  created_at: { type: Date, default: Date.now },
});

// Create Mongoose models
const Friendship = mongoose.model('Friendship', friendshipSchema);
const FriendshipCreate = mongoose.model('FriendshipCreate', friendshipCreateSchema);
const FriendshipResponse = mongoose.model('FriendshipResponse', friendshipResponseSchema);

// Export models for use in other parts of the app
module.exports = { Friendship, FriendshipCreate, FriendshipResponse };
