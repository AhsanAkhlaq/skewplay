FROM node:22-alpine

WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./

# Install dependencies
RUN npm install

# Expose Vite's default port
EXPOSE 5173

# Start the dev server and explicitly bind to all interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
