# Architecture

This document describes the system architecture, data flow, and deployment topology for Bili‑Summarizer.

## 1) System Components
```mermaid
flowchart LR
  U[User Browser] --> FE[Vue Frontend]
  FE -->|SSE| API[FastAPI Backend]
  FE -->|REST| API
  API --> YT[yt-dlp / Bilibili]
  API --> G[Gemini API]
  API --> DB[(SQLite cache.db)]
  API --> FS[(videos/)]
```

## 2) Core Data Flow (Summarize)
```mermaid
sequenceDiagram
  participant U as User
  participant FE as Frontend
  participant BE as Backend
  participant YT as yt-dlp
  participant GM as Gemini
  U->>FE: 提交视频 URL
  FE->>BE: GET /api/summarize (SSE)
  BE->>BE: Cache check
  alt cache hit
    BE-->>FE: transcript_complete + summary_complete
  else cache miss
    BE->>YT: Download/Subtitle
    BE->>GM: Upload (if needed)
    BE->>GM: Summarize + Transcript
    BE-->>FE: progress/status stream
    BE-->>FE: transcript_complete + summary_complete
    BE->>BE: cache save
  end
```

## 3) Auth & API Key
```mermaid
flowchart LR
  C[Client] --> B[Backend]
  B --> K{Has x-api-key?}
  K -->|Yes| V[Verify key_hash]
  K -->|No| S{Has Bearer token?}
  S -->|Yes| T[Verify Supabase session]
  S -->|No| E[401]
  V -->|Valid| OK[Attach user_id]
  T -->|Valid| OK
```

## 4) Cloud History Sync
```mermaid
flowchart TD
  FE[Frontend] --> HGET[GET /api/history]
  HGET --> DB[(Supabase summaries)]
  FE --> HPOST[POST /api/history]
  HPOST --> DB
  FE --> MERGE[Merge local + cloud]
```

## 5) Deployment Topology

### Local Dev (Vite + Uvicorn)
```
Browser -> http://localhost:5173 (Vite)
Vite proxy -> http://localhost:7860 (FastAPI)
```

### Docker Compose
```
Browser -> Nginx (frontend)
Nginx -> FastAPI (backend)
FastAPI -> Gemini / yt-dlp / cache.db / videos/
```

### Render (Single Service)
```
Browser -> FastAPI (serves /api + SPA from frontend/dist)
FastAPI -> Gemini / yt-dlp / cache.db / videos/
```

## 6) Storage
- `cache.db`: summary/transcript cache + API keys + usage_daily.
- `videos/`: downloaded media for playback.
- Supabase: cloud history (optional).

## 7) Legacy UI
If `frontend/dist` is missing, backend serves `web_app/legacy_ui/index.html` and `web_app/legacy_ui/static/`.
