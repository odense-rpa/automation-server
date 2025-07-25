# Build stage
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --no-audit

# Copy application code
COPY . .

# Build arguments for environment configuration
ARG VITE_ATS_API_BASE_URL=/api
ENV VITE_ATS_API_BASE_URL=$VITE_ATS_API_BASE_URL

# Build the application
RUN npm run build

# Production stage
FROM nginx:stable-alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Add metadata labels
LABEL maintainer="miwn@odense.dk" \
      version="0.2.0" \
      description="Automation Server Frontend"

# Start nginx
CMD ["nginx", "-g", "daemon off;"]