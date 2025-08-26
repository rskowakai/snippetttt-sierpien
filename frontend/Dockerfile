FROM node:20-alpine

WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock, etc.)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port
EXPOSE 5173

# Default command for development
CMD ["npm", "run", "dev", "--", "--host"]
