# Stage 1: Building the code
FROM node:latest as builder

WORKDIR /app

# Copy package.json and package-lock.json/yarn.lock files
COPY ./client/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the code
COPY ./client .
# Build the project
RUN npm run build

# Stage 2: Run the code
FROM node:alpine

WORKDIR /app

# Copy build from the builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Expose the port the app runs on
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
