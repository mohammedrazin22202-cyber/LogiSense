# 🚛 TRACK FLEET COMMAND
**Real-time Fleet Management System** — Rebuilt from scratch with live data from `orders_master.xlsx`

---

## Architecture

```
fleet-command/
├── backend/
│   ├── server.py        # Flask REST API + SSE real-time stream
│   ├── database.py      # SQLite layer (all tables, indexes)
│   ├── simulation.py    # Vehicle movement engine (every 5s)
│   └── seed.py          # Loads orders_master.xlsx into DB
├── frontend/
│   ├── index.html       # Shell (no data hardcoded)
│   ├── style.css        # Dark industrial UI
│   └── script.js        # All data from API, SSE-driven
└── data/
    ├── fleet.db         # SQLite database (auto-created)
    └── fleet.log        # Server log file
```

---

## Quick Start

```bash
# 1. Install Python dependencies (only openpyxl needed for seeding)
pip install flask openpyxl --break-system-packages

# 2. Seed the database from Excel
python3 backend/seed.py

# 3. Start the server
python3 backend/server.py
```

Then open: **http://localhost:1996**

---

## What's Implemented

### ✅ Real Data (no hardcoding)
- 47 vehicles from `orders_master.xlsx`
- 47 shipments with full customer/goods/route info
- All vehicles, drivers, routes come from backend API

### ✅ Real-time Updates (every 5 seconds)
- **Server-Sent Events (SSE)** push vehicle positions to all clients instantly
- Map markers move automatically
- Speed, heading, status update live
- Auto-reconnects on disconnect

### ✅ Persistent Storage (SQLite)
- `vehicles` — full profile: id, type, plate, driver, status, lat/lng, speed
- `orders` — complete shipment data
- `vehicle_positions` — full history (every 5s tick recorded)
- `alerts` — with severity, acknowledge support
- `temperature_logs` — cold chain tracking
- `system_logs` — all events logged

### ✅ Vehicle Status Tracking
States: **moving** | **idle** | **stopped** | **offline** | **maintenance**
- Status changes broadcast to all clients via SSE
- Can update manually via Fleet page → "Status" button
- External PUT endpoint: `PUT /api/vehicles/{id}/status`

### ✅ Timestamp Tracking
- Every position update has `recorded_at` timestamp (ISO 8601)
- Map shows "Last update" time
- Vehicle list shows last seen time

### ✅ Vehicle History
- All movement stored in `vehicle_positions` table
- Accessible: `GET /api/vehicles/{id}/history?limit=200`
- Trail lines shown on map (toggle with route button)

### ✅ Vehicle Identity
Each vehicle has: `id`, `vehicle_type`, `plate_number`, `driver_name`, `driver_contact`, `assigned_route`, `current_order_id`

### ✅ Alerts & Notifications
- Toast notifications on new alerts
- Alerts page with severity colors
- Acknowledge individual or all alerts
- Auto-alerts when vehicle unexpectedly stops or delivers

### ✅ Analytics (from real data)
- KPIs: active vehicles, deliveries, on-time %, avg speed, revenue, distance
- Route bar charts
- Vehicle status breakdown
- Top vehicles by speed
- Alert breakdown

### ✅ Logging
- Every vehicle update, user action, delivery, GPS update logged
- Viewable in Logs page with type filter
- Written to `data/fleet.log` file

### ✅ Error Handling
- API error responses (400, 404, 500) with JSON messages
- Frontend shows toast on network failure
- SSE auto-reconnects in 5 seconds

### ✅ GPS Device Support (future)
Real GPS devices can POST locations directly:
```bash
POST /api/vehicles/{id}/location
{
  "lat": 12.9716,
  "lng": 77.5946,
  "speed": 52.3,
  "heading": 180,
  "status": "moving",
  "timestamp": "2026-02-20T12:00:00Z"
}
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vehicles` | All vehicles |
| GET | `/api/vehicles/{id}` | Vehicle + history |
| PUT | `/api/vehicles/{id}/status` | Update status |
| POST | `/api/vehicles/{id}/location` | Ingest GPS |
| GET | `/api/orders?search=&status=&page=` | Paginated orders |
| GET | `/api/orders/{id}` | Full order detail |
| GET | `/api/alerts?unread=true` | Alerts |
| PUT | `/api/alerts/{id}/acknowledge` | Ack alert |
| GET | `/api/analytics/summary` | All KPIs |
| GET | `/api/logs?type=&limit=` | System logs |
| GET | `/api/stream` | SSE real-time stream |

---

## Scalability Notes
- SQLite WAL mode enabled (concurrent reads)
- Indexes on all foreign keys and timestamp columns
- SSE clients stored in memory list (swap for Redis pub/sub at scale)
- Simulation engine is threaded (won't block HTTP serving)
- For 1000s of vehicles: replace SQLite with PostgreSQL, SSE with WebSocket + message broker
