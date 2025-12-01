# DALS Multi-Monitor Workers Frontend

A React/Next.js frontend for the DALS Workers Management System with native multi-monitor support.

## Features

- 🖥️ **Multi-Monitor Support**: Pop-out windows for different control panels
- 📋 **Worker Registry**: Real-time worker monitoring and management
- ⚒️ **Worker Forge**: Industrial-grade worker creation interface
- 📄 **Template Management**: Worker blueprint customization
- 🔍 **Worker Inspector**: Deep inspection of worker configurations
- 🎨 **Modern UI**: Dark theme optimized for control center environments

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000/workers
```

## Multi-Monitor Setup

1. **Monitor 1**: Main Dashboard (`/workers`) - Overview and quick actions
2. **Monitor 2**: Worker Registry (`/workers/registry`) - Real-time monitoring
3. **Monitor 3**: Worker Forge (`/workers/forge`) - Creation interface

Use the "Pop Out" buttons to open each panel in separate windows.

## Architecture

- **Next.js 14**: React framework with SSR
- **Tailwind CSS**: Utility-first styling
- **API Proxy**: Automatic proxy to DALS backend (port 8003)
- **Real-time Updates**: WebSocket support for live data
- **Responsive Design**: Works on any screen size

## API Integration

The frontend automatically proxies API calls to the DALS backend:

- `GET /api/workers/status` - System status
- `GET /api/workers/` - Worker list
- `POST /api/workers/forge` - Create worker
- `GET /api/workers/templates/` - Template list

## Development

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build
npm start
```

## Multi-Monitor Workflow

1. Start DALS backend on port 8003
2. Start frontend on port 3000
3. Open main dashboard
4. Click "Pop Out" buttons for each monitor
5. Arrange windows across your displays
6. Monitor and control workers in real-time