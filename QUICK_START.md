# 🚀 Quick Start - Project Synapse Demo

## Option 1: Frontend Demo Only (Fastest)

**Experience the complete UI with demo data:**

```bash
# Windows
start_demo.bat

# Or manually:
cd frontend
npm install
npm start
```

**Access:** http://localhost:3000

This shows the complete user interface with:
- ✅ Interactive dashboard with real-time metrics
- ✅ Federated query interface with AI synthesis
- ✅ Silo management with visual status
- ✅ Privacy center with budget tracking
- ✅ Analytics dashboard with charts
- ✅ Interactive demos with live progress
- ✅ Complete documentation

## Option 2: Full System (Backend + Frontend)

**Complete system with real API:**

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start backend (Terminal 1)
python -m synapse.api.server

# Start frontend (Terminal 2)
cd frontend
npm install
npm start
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080/docs

## Option 3: Docker Complete Stack

**Everything with Docker:**

```bash
# Complete stack
docker-compose -f docker-compose.full.yml up -d

# Check status
docker-compose -f docker-compose.full.yml ps
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8080
- Monitoring: http://localhost:3001

## What You'll See

### 🏠 Dashboard
- Real-time system metrics and health
- Query trends and silo distribution
- Recent activity and system status

### 🔍 Query Interface
- Intelligent federated search
- Auto-suggestions and real-time results
- AI-powered knowledge synthesis
- Privacy budget tracking

### 🏢 Silo Management
- Visual silo overview
- Real-time indexing progress
- Access control configuration

### 🔒 Privacy Center
- Privacy budget monitoring
- Compliance status tracking
- Access audit logs

### 📊 Analytics
- Usage trends and performance metrics
- User engagement patterns
- System optimization insights

### 🎭 Interactive Demos
- Live system demonstrations
- Enterprise-scale simulations
- ROI calculations and business impact

## Demo Features

**The interface demonstrates:**
- Cross-silo federated search
- Privacy-preserving query routing
- AI-powered knowledge synthesis
- Real-time privacy budget management
- Enterprise security and compliance
- Scalable architecture visualization

## Troubleshooting

**Frontend won't start:**
```bash
# Clear npm cache
npm cache clean --force
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

**Port conflicts:**
- Frontend: Change port in `frontend/package.json`
- Backend: Use `--port` flag with API server

**Dependencies missing:**
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Next Steps

1. **Explore the Interface**: Navigate through all sections
2. **Try the Demos**: Run interactive demonstrations
3. **Read the Docs**: Built-in documentation with examples
4. **Deploy to Production**: See `DEPLOYMENT.md` for enterprise setup

**Project Synapse transforms organizational knowledge silos into a unified, privacy-preserving knowledge fabric.**