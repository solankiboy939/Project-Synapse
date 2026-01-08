# Project Synapse - Frontend

Modern React-based user interface for Project Synapse, the Cross-Silo Enterprise Knowledge Fabric.

## Features

- **Interactive Dashboard**: Real-time system overview with metrics and charts
- **Federated Query Interface**: Intuitive search across organizational silos
- **Silo Management**: Visual management of data silos and indexing status
- **Privacy Center**: Privacy budget monitoring and compliance tracking
- **Analytics Dashboard**: Comprehensive usage analytics and insights
- **Interactive Demo**: Live demonstrations of all system capabilities
- **Documentation**: Complete technical documentation with code examples

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Technology Stack

- **React 18**: Modern React with hooks and functional components
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Recharts**: Responsive charts and data visualizations
- **Framer Motion**: Smooth animations and transitions
- **React Router**: Client-side routing
- **Heroicons**: Beautiful SVG icons
- **React Hot Toast**: Elegant toast notifications

## Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Navbar.js       # Main navigation component
├── pages/              # Main application pages
│   ├── Dashboard.js    # System overview dashboard
│   ├── QueryInterface.js # Federated search interface
│   ├── SiloManagement.js # Silo management interface
│   ├── PrivacyCenter.js  # Privacy monitoring center
│   ├── Analytics.js      # Usage analytics dashboard
│   ├── Documentation.js  # Technical documentation
│   └── Demo.js          # Interactive demonstrations
├── App.js              # Main application component
├── index.js            # Application entry point
└── index.css           # Global styles and Tailwind imports
```

## Key Features

### Dashboard
- Real-time system metrics and health monitoring
- Interactive charts showing query trends and silo distribution
- Recent activity feeds and system status indicators
- Quick action buttons for common tasks

### Query Interface
- Intelligent search with auto-suggestions
- Real-time federated search across multiple silos
- Privacy-preserving result display with source attribution
- AI-powered knowledge synthesis from multiple sources
- Privacy budget tracking and usage indicators

### Silo Management
- Visual silo overview with status indicators
- Real-time indexing progress monitoring
- Silo configuration and access control management
- Performance metrics and document counts

### Privacy Center
- Privacy budget usage visualization
- Compliance status monitoring (GDPR, SOX, FedRAMP)
- Access log auditing with detailed tracking
- Privacy mechanism usage analytics
- Budget reset functionality with warnings

### Analytics
- Comprehensive usage analytics and trends
- Performance monitoring and optimization insights
- User engagement patterns and behavior analysis
- Query popularity and response time metrics

### Interactive Demo
- Live demonstrations of all system capabilities
- Multiple demo scenarios (basic, enterprise, synthesis)
- Real-time progress tracking and logging
- ROI calculations and business impact metrics

## Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run test suite
- `npm run eject` - Eject from Create React App (not recommended)

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
REACT_APP_API_URL=http://localhost:8080
REACT_APP_VERSION=0.1.0
```

### Customization

The UI is built with Tailwind CSS and uses a custom design system:

- **Primary Colors**: Synapse blue (`synapse-*`)
- **Privacy Colors**: Purple gradient (`privacy-*`)
- **Component Classes**: Predefined utility classes in `index.css`

### API Integration

The frontend communicates with the Synapse backend API:

- **Base URL**: Configured via `REACT_APP_API_URL`
- **Endpoints**: RESTful API with JSON responses
- **Authentication**: JWT-based authentication (when implemented)
- **Error Handling**: Comprehensive error handling with user feedback

## Deployment

### Production Build

```bash
# Build optimized production bundle
npm run build

# Serve static files
npx serve -s build
```

### Docker Deployment

```bash
# Build Docker image
docker build -t synapse-frontend .

# Run container
docker run -p 3000:3000 synapse-frontend
```

### Integration with Backend

The frontend is designed to work seamlessly with the Synapse backend:

1. **API Proxy**: Development server proxies API calls to `http://localhost:8080`
2. **Real-time Updates**: WebSocket integration for live updates (planned)
3. **Authentication**: JWT token management and refresh
4. **Error Handling**: Graceful degradation when backend is unavailable

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style and patterns
2. Use TypeScript for new components (migration in progress)
3. Add proper error handling and loading states
4. Include responsive design for mobile devices
5. Test across different browsers and screen sizes

## Performance Considerations

- **Code Splitting**: Automatic route-based code splitting
- **Lazy Loading**: Components loaded on demand
- **Memoization**: React.memo for expensive components
- **Optimized Images**: WebP format with fallbacks
- **Bundle Analysis**: Use `npm run build` and analyze bundle size

This frontend provides a complete, production-ready interface for Project Synapse, making the powerful federated knowledge capabilities accessible through an intuitive, modern web interface.