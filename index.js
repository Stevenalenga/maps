const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const dotenv = require("dotenv");

dotenv.config(); // Load environment variables

const authRouter = require("./routes/auth");
const usersRouter = require("./routes/users");
const locationsRouter = require("./routes/locations");
const tagsRouter = require("./routes/tags");
const friendshipsRouter = require("./routes/friendships");
const factsRouter = require("./routes/facts");

// Initialize Express app
const app = express();

// Middleware
app.use(cors()); // Allow CORS and remote connections
app.use(express.json()); // Parse JSON bodies

// Application metadata (for reference purposes)
const appMetadata = {
  title: "My API",
  description: "This is a maps API project, meant to give details on locations",
  version: "3.5.0",
  terms_of_service: "http://mola.com/terms/",
  contact: {
    name: "Steven Alenga",
    url: "http://steven.alenga@gmail.com/contact/",
    email: "steven.alenga@gmail.com",
  },
  license: {
    name: "Apache 2.0",
    url: "https://www.apache.org/licenses/LICENSE-2.0.html",
  },
};

// MongoDB connection
const dbUri = `${process.env.MONGO_URI}/${process.env.DATABASE_NAME}`; // Use the MongoDB URI and database name from the .env file
mongoose
  .connect(dbUri, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log("Connected to MongoDB"))
  .catch((err) => console.error("Error connecting to MongoDB:", err));
  
// Routes
app.use("/auth", authRouter);
app.use("/users", usersRouter);
app.use("/locations", locationsRouter);
app.use("/tags", tagsRouter);
app.use("/friendships", friendshipsRouter);
app.use("/facts", factsRouter);

// Root endpoint
app.get("/", (req, res) => {
  res.json({
    message: "Welcome to our maps API project",
    description: "This is a project meant to give details on locations",
  });
});

// Status endpoint
app.get("/status", (req, res) => {
  res.json({ status: "API is running" });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});