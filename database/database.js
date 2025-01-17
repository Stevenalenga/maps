const mongoose = require('mongoose');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config();

// MongoDB Connection
const MONGO_URI = process.env.MONGO_URI;
const DATABASE_NAME = process.env.DATABASE_NAME;
const PORT = parseInt(process.env.PORT, 10);

// Add the current directory to the module path (optional)
require('module').globalPaths.push(path.join(__dirname));

// Validate MongoDB URI
if (!MONGO_URI || !MONGO_URI.startsWith('mongodb://') && !MONGO_URI.startsWith('mongodb+srv://')) {
  throw new Error("Invalid MongoDB URI. It must begin with 'mongodb://' or 'mongodb+srv://'");
}

// Connect to MongoDB
const db = () => {
  mongoose.connect(MONGO_URI, { dbName: DATABASE_NAME, useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('Connected to MongoDB'))
    .catch((err) => {
      console.error('MongoDB connection error:', err);
      process.exit(1);
    });
};

module.exports = db;
