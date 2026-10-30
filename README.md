# TubeFlow - Modern MySQL-Powered YouTube Alternative 🎥🚀

TubeFlow is a full-featured, high-performance video-sharing platform modeled after YouTube, engineered natively with **MySQL** as its primary relational database and powered by a **Python FastAPI** backend.

---

## 🌟 Key Features

### 1. 🗄️ Native MySQL Architecture & Explorer
- **Production Relational Schema**: 12 relational tables (`users`, `channels`, `categories`, `videos`, `comments`, `video_reactions`, `comment_reactions`, `subscriptions`, `playlists`, `playlist_items`, `watch_history`, `watch_later`) with InnoDB engine, foreign keys, and indexes.
- **Dual-Engine Auto-Fallback**: If MySQL server is not currently running or configured, TubeFlow automatically boots up seamlessly in SQLite mirror mode without crashing, showing a status pill in the UI.
- **One-Click Live Migration**: Connect your MySQL database via the built-in `/database` manager page; TubeFlow provisions the schema and migrates all existing records into MySQL with zero server downtime.
- **Live SQL Query Console**: Test and run raw SQL queries (`SELECT * FROM videos;`, `SHOW TABLES;`) right inside the browser with milliseconds query execution timer.

### 2. 🎬 Streaming Video Player (HTTP 206 Partial Content)
- Custom HTML5 player supporting **byte-range streaming (HTTP 206)** for instantaneous scrubbing and seeking.
- **Theater Mode**, Fullscreen, and Playback Speed selector (0.5x, 1x, 1.25x, 1.5x, 2x).
- Autoplay next, animated video previews, and duration badges.

### 3. 👍 Social Engagement & Community
- **Likes & Dislikes**: Live counters and toggling with reaction persistence in MySQL.
- **Channels & Subscriptions**: Subscribe/unsubscribe with dynamic subscriber counter updates.
- **Comments System**: Post comments, delete your own comments, and like comments.
- **Active User Switcher**: Easily test multi-user interactions (switch between Alex Rivers, Maya Lin, Dave Miller, Sarah Jenkins, Chef Kevin, or new users) with one click from the avatar menu.

### 4. 📤 Video Upload Studio
- Drag-and-drop or browse video files (`.mp4`, `.webm`, `.mov`).
- Direct video URL / CDN stream support.
- Custom thumbnail upload or auto-generated high-resolution vector thumbnails.
- Category selection, tags, title, and description with instant publication into MySQL.

### 5. 📚 Library, Watch History & Liked Videos
- Automatically tracks watch duration and records view history into the `watch_history` table.
- "Clear All Watch History" feature.
- Dedicated feeds for **Subscriptions**, **Liked Videos**, and **Watch History**.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
Double-click `start.bat` or run:
```bash
python run.py
```
This automatically opens your default browser at:
**[http://localhost:8000](http://localhost:8000)**

---

## 🐬 Connecting to MySQL

TubeFlow is designed to work with **any** MySQL server:
- **XAMPP / WAMP / MAMP** (Default: host `127.0.0.1`, port `3306`, user `root`, no password)
- **Official MySQL Server 5.7 / 8.0+**
- **MariaDB 10.3+**
- **Docker MySQL container**

### Option A: Using the In-App Database Manager (Recommended)
1. Navigate to **[http://localhost:8000/database](http://localhost:8000/database)**.
2. Enter your MySQL Host, Port, User, and Password.
3. Click **"Test Connection"**.
4. Click **"Connect & Switch to MySQL"** (checks "Automatically migrate existing data into MySQL" to transfer all videos, users, and comments).

### Option B: Using Environment Variables / `.env`
Set environment variables before starting:
```bash
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
set MYSQL_DB=tubeflow_db
python run.py
```

### Option C: Standalone MySQL CLI or phpMyAdmin
You can also import the provided `schema.sql` directly into your MySQL server:
```bash
mysql -u root -p < schema.sql
```

---

## 📁 Project Structure

```
├── app/
│   ├── config.py           # Database & server configuration
│   ├── database.py         # MySQL connection manager & dual-engine fallback
│   ├── models.py           # SQLAlchemy MySQL relational ORM models
│   ├── crud.py             # Database CRUD (videos, comments, likes, subscriptions)
│   ├── streaming.py        # HTTP 206 Partial Content range request streaming
│   ├── seed_data.py        # Realistic initial channels, users, videos, comments
│   ├── routes/
│   │   ├── api.py          # RESTful JSON endpoints
│   │   ├── db_admin.py     # MySQL diagnostics & raw SQL query runner
│   │   └── views.py        # HTML template renderers
│   └── main.py             # FastAPI entrypoint & static mount
├── static/
│   ├── css/style.css       # YouTube-accurate dark theme CSS
│   ├── js/
│   │   ├── app.js          # User switcher, navigation, upload modal
│   │   ├── player.js       # Video player, like/dislike, comments, theater mode
│   │   └── db_admin.js     # MySQL test, live switcher & SQL table viewer
│   └── uploads/            # Videos, thumbnails, banners, and avatars
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html          # Feed & category chips
│   ├── watch.html          # Video player & watch page
│   ├── channel.html        # Channel profile page
│   ├── subscriptions.html  # Subscriptions feed
│   ├── history.html        # Watch history page
│   ├── liked.html          # Liked videos page
│   └── database.html       # MySQL Database Console & Explorer
├── schema.sql              # Pure MySQL DDL schema script
├── run.py                  # Server launcher with auto-port & browser open
├── start.bat               # 1-click Windows starter
└── requirements.txt
```

---

## ⚡ API Endpoints (OpenAPI / Swagger)
Visit **[http://localhost:8000/docs](http://localhost:8000/docs)** to test the interactive Swagger UI:
- `GET /api/videos` - Filter by category, query, sort
- `GET /api/videos/{id}` - Video details, channel info, user reactions
- `POST /api/upload` - Upload video file or stream URL
- `POST /api/videos/{id}/reaction` - Like / dislike toggle
- `POST /api/videos/{id}/comments` - Post comment
- `POST /api/channels/{id}/subscribe` - Toggle subscription
- `POST /api/db/test-connection` - Test MySQL credentials
- `POST /api/db/query` - Execute raw SQL in MySQL
