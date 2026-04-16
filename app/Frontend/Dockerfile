# Stage 1: Build
# Uses node version 18 as our base image
FROM node:18 AS build

# Goes to the app directory
WORKDIR /app

COPY package.json package-lock.json ./

# Set prod env and install deps
ENV NODE_ENV=production

# Install app dependencies
RUN npm install

# Copy package.json and package-lock.json
COPY . .

# Run the app
CMD [ "npm", "run", "build" ]

# Stage 2 : Serve
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
