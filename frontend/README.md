# ARIS Frontend

Production-grade React/Vite frontend for the ARIS system.

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

## Build

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── api/          # API client
│   ├── services/     # API service integrations
│   ├── auth/         # Authentication
│   ├── pages/        # Page components
│   ├── components/   # Reusable UI components
│   ├── hooks/        # Custom hooks
│   ├── routes/       # Routing configuration
│   ├── store/        # Global state management
│   ├── App.jsx       # Main app component
│   └── main.jsx      # Entry point
├── index.html        # HTML template
├── vite.config.js    # Vite configuration
└── package.json      # Dependencies
```

## Features

✅ User authentication  
✅ Excel file upload  
✅ Analytics dashboard  
✅ Toppers leaderboard  
✅ Section-wise performance  
✅ Subject analysis  
✅ Excel export  
✅ Responsive design  
✅ Data visualization with Recharts  
✅ Global state management  
✅ Protected routes  

## Environment Variables

See `.env` for configurable environment variables:

- `VITE_API_URL` - Backend API URL
- `VITE_ENABLE_PRESENTATION_MODE` - Enable presentation mode
- `VITE_ENABLE_EXPORT` - Enable Excel export

## API Integration

All API calls go through the centralized client in `src/api/client.js`.

Endpoints used:
- `POST /api/upload/` - Upload Excel file
- `GET /api/analytics/{upload_id}/` - Get complete analytics
- `GET /api/toppers/{upload_id}/` - Get toppers list
- `GET /api/sections/{upload_id}/` - Get section performance
- `GET /api/subjects/{upload_id}/` - Get subject analysis
- `GET /api/export/excel/{upload_id}/` - Download Excel export

## Performance

- All API calls cached where possible
- Lazy loading of analytics data
- Optimized chart rendering
- Sub-100ms response times for cached data
