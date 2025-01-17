const mongoose = require('mongoose');

// UserBase schema
const userBaseSchema = new mongoose.Schema({
  username: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
});

// UserUpdate schema (extends UserBase and allows for optional password)
const userUpdateSchema = new mongoose.Schema({
  username: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: false },  // Optional password
});

// UserResponse schema (includes username and email)
const userResponseSchema = new mongoose.Schema({
  username: { type: String, required: true },
  email: { type: String, required: true },
});

// UserLogin schema (used for login with username and password)
const userLoginSchema = new mongoose.Schema({
  username: { type: String, required: true },
  password: { type: String, required: true },
});

// Token schema (used for storing access tokens)
const tokenSchema = new mongoose.Schema({
  access_token: { type: String, required: true },
  token_type: { type: String, required: true },
});

// TokenData schema (stores username if present)
const tokenDataSchema = new mongoose.Schema({
  username: { type: String, required: false },
});

// User model (with an id field)
const userSchema = new mongoose.Schema({
  id: { type: Number, required: true },
  username: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
});

// Create Mongoose models
const User = mongoose.model('User', userSchema);
const UserUpdate = mongoose.model('UserUpdate', userUpdateSchema);
const UserResponse = mongoose.model('UserResponse', userResponseSchema);
const UserLogin = mongoose.model('UserLogin', userLoginSchema);
const Token = mongoose.model('Token', tokenSchema);
const TokenData = mongoose.model('TokenData', tokenDataSchema);

// Export models for use in other parts of the app
module.exports = { User, UserUpdate, UserResponse, UserLogin, Token, TokenData };
