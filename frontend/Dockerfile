FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy project files
COPY . .

# Set environment variables
ENV NODE_ENV=development

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"] 