// schemas/auth.js
const Joi = require("joi");

// Base User Schema
const userBaseSchema = Joi.object({
  username: Joi.string().min(3).max(30).required(),
  email: Joi.string().email().required(),
});

// User Creation Schema
const userCreateSchema = userBaseSchema.keys({
  password: Joi.string().min(8).required(),
});

// User Response Schema
const userResponseSchema = userBaseSchema;

// User Login Schema
const userLoginSchema = Joi.object({
  username: Joi.string().required(),
  password: Joi.string().required(),
});

// Token Schema
const tokenSchema = Joi.object({
  accessToken: Joi.string().required(),
  tokenType: Joi.string().default("Bearer"),
});

// Token Data Schema
const tokenDataSchema = Joi.object({
  id: Joi.string().required(),
});

module.exports = {
  userCreateSchema,
  userResponseSchema,
  userLoginSchema,
  tokenSchema,
  tokenDataSchema,
};
