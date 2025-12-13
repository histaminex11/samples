# Node.js Frontend + Java Backend Sample Project

> **Note:** This project was created entirely using Cursor AI prompts. It demonstrates a full-stack application with a React frontend (Node.js/Vite) and a Spring Boot backend (Java).

## 📋 Project Overview

This is a sample full-stack application that demonstrates:
- **Frontend**: React application built with Vite (Node.js)
- **Backend**: Spring Boot REST API (Java)
- **Integration**: Frontend communicates with backend via REST API through Vite proxy

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   React App     │  ────>  │  Spring Boot    │
│   (Port 5173)   │  Proxy  │  (Port 8080)    │
│   Vite Dev      │         │  REST API       │
└─────────────────┘         └─────────────────┘
```

- Frontend runs on `http://localhost:5173`
- Backend runs on `http://localhost:8080`
- Vite proxy forwards `/api/*` requests to the backend

## 🚀 Quick Start

### Prerequisites

Before running the application, ensure you have the following installed:

- **Java 17+** - Required for Spring Boot backend
- **Maven 3.6+** - Java dependency management
- **Node.js 16+** - Required for React frontend
- **npm** - Node package manager (comes with Node.js)

### Verify Prerequisites

Check if you have the required tools installed:

```bash
java -version    # Should show Java 17 or higher
mvn -version     # Should show Maven 3.6 or higher
node -v          # Should show Node.js 16 or higher
npm -v           # Should show npm version
```

### Running the Application

#### Option 1: Automated Setup (Recommended)

Simply run the setup script:

```bash
chmod +x runme.sh
./runme.sh
```

This script will:
1. Check for required prerequisites
2. Install all dependencies (Maven and npm packages)
3. Start both backend and frontend servers

#### Option 2: Manual Setup

**Step 1: Install Backend Dependencies**

```bash
cd backend
mvn clean install
cd ..
```

**Step 2: Install Frontend Dependencies**

```bash
cd frontend
npm install
cd ..
```

**Step 3: Start Backend Server**

In a terminal window:

```bash
cd backend
mvn spring-boot:run
```

The backend will start on `http://localhost:8080`

**Step 4: Start Frontend Server**

In a new terminal window:

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

## 🌐 Accessing the Application

Once both servers are running:

1. Open your browser and navigate to: **http://localhost:5173**
2. You should see the message: "Hello from the Java backend!"
3. This confirms the frontend successfully communicated with the backend

## 🧪 Testing

### Automated Testing

Run the test script to verify everything is working:

```bash
chmod +x test-frontend.sh
./test-frontend.sh
```

This will test:
- Frontend server status
- Backend server status
- API endpoint responses
- Vite proxy functionality

### Manual API Testing

Test the backend API directly:

```bash
curl http://localhost:8080/api/greeting
```

Expected response:
```json
{"message":"Hello from the Java backend!"}
```

### Browser Testing

1. Open **http://localhost:5173** in your browser
2. Open Developer Tools (F12)
3. Check the **Network** tab to see the API request to `/api/greeting`
4. Verify the response shows the greeting message

## 📁 Project Structure

```
node_java_project/
├── backend/                 # Java Spring Boot backend
│   ├── pom.xml             # Maven configuration
│   └── src/
│       ├── main/java/com/example/demo/
│       │   ├── DemoApplication.java    # Spring Boot main class
│       │   └── HelloController.java    # REST API controller
│       └── test/java/com/example/demo/
│           └── HelloControllerTest.java # Unit tests
│
├── frontend/                # React frontend
│   ├── package.json        # npm dependencies
│   ├── vite.config.js      # Vite configuration with proxy
│   ├── index.html          # HTML entry point
│   └── src/
│       ├── main.jsx        # React entry point
│       └── App.jsx         # Main React component
│
├── runme.sh                # Automated setup and run script
├── test-frontend.sh        # Frontend testing script
└── README.md               # This file
```

## 🔧 Configuration

### Backend Configuration

- **Port**: 8080 (default Spring Boot port)
- **Java Version**: 17
- **Framework**: Spring Boot 3.3.2

### Frontend Configuration

- **Port**: 5173 (default Vite port)
- **Framework**: React 18.3.1
- **Build Tool**: Vite 5.4.1
- **Proxy**: Configured in `vite.config.js` to forward `/api/*` to `http://localhost:8080`

## 🛠️ Development

### Backend Development

- Main application: `backend/src/main/java/com/example/demo/DemoApplication.java`
- REST Controller: `backend/src/main/java/com/example/demo/HelloController.java`
- Run tests: `cd backend && mvn test`

### Frontend Development

- Main component: `frontend/src/App.jsx`
- Entry point: `frontend/src/main.jsx`
- Hot reload is enabled - changes will reflect automatically

## 🐛 Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

**Backend (8080):**
```bash
# Find and kill process on port 8080
lsof -ti:8080 | xargs kill -9
```

**Frontend (5173):**
```bash
# Find and kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Dependencies Not Installing

**Maven:**
- Ensure you have internet connection
- Check Maven settings: `mvn -version`
- Try clearing cache: `mvn clean`

**npm:**
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, then run `npm install` again

### Backend Not Starting

- Verify Java version: `java -version` (needs Java 17+)
- Check Maven installation: `mvn -version`
- Review backend logs for specific errors

### Frontend Not Connecting to Backend

- Ensure backend is running on port 8080
- Check Vite proxy configuration in `frontend/vite.config.js`
- Verify CORS settings if needed

## 📝 API Endpoints

### GET /api/greeting

Returns a greeting message from the backend.

**Response:**
```json
{
  "message": "Hello from the Java backend!"
}
```

## 🤝 Contributing

This is a sample project created with Cursor AI. Feel free to extend it with:
- Additional API endpoints
- Database integration
- Authentication
- More React components
- Testing frameworks

## 📄 License

This is a sample project for demonstration purposes.

---

**Created with ❤️ using Cursor AI**
