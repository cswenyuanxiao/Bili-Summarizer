# Project Context

## Purpose
Bili-Summarizer is a Vue + FastAPI app that summarizes Bilibili videos, generates mindmaps, and provides transcript + AI follow‑up chat.

## Primary Entry Points
- **Backend**: `web_app/main.py`
- **Frontend**: `frontend/src/App.vue`
- **Docs**: `docs/system-analysis.md`, `docs/feature-roadmap.md`, `docs/implementation/three_phases_summary.md`

## Key Runtime Flows
1. **Summarize (SSE)**  
   Frontend opens `GET /api/summarize` → backend streams status + results → UI renders summary, transcript, mindmap.
2. **Mindmap**  
   Summary includes Mermaid block → `frontend/src/components/MindmapViewer.vue` renders SVG.
3. **Transcript + Video**  
   `frontend/src/components/TranscriptPanel.vue` parses timestamps → click to seek.
4. **AI Chat**  
   `POST /api/chat` (stream) → `frontend/src/components/ChatPanel.vue`.
5. **Cloud History**  
   `GET/POST/DELETE /api/history` → `frontend/src/composables/useHistorySync.ts`.
6. **Export**  
   Summary export (MD/TXT/PDF) and mindmap export (SVG/PNG) are handled in `frontend/src/App.vue`.
7. **Resummarize**  
   Summary card can trigger a re-run with `skip_cache=true` to force a fresh summary.
8. **Dashboard**  
   `GET /api/dashboard` returns credits and usage for the account panel.

## Auth & API Key
- Supabase auth (optional) lives in `frontend/src/composables/useAuth.ts`.
- API keys stored in `cache.db` (SQLite).  
- Auth entry: `web_app/auth.py` via `get_current_user`.

## Environment Variables
- `GOOGLE_API_KEY`: required for Gemini calls.
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`: optional for auth + cloud history.
- `SUPABASE_SERVICE_KEY`: optional for server‑side access.

## Legacy UI (Fallback)
If `frontend/dist` is missing, backend serves `web_app/templates/index.html` and `web_app/static/*`.  
These files are legacy and not used by the Vue app.

## Project Structure (Selected)
```
frontend/               # Vue app
  src/components/       # UI components
  src/composables/      # data flow hooks
web_app/                # FastAPI backend
  main.py               # API + SSE
  auth.py               # API key + session auth
  downloader.py         # yt-dlp + subtitles
docs/                   # planning + analysis
```

## Known Areas to Watch
- `/chat` is legacy (non‑stream); `/api/chat` is the current streaming endpoint.
- API key + subscription endpoints should be kept in sync with UI state.

## Quick Start (Dev)
```
# Backend
export GOOGLE_API_KEY="..."
uvicorn web_app.main:app --reload --port 7860

# Frontend
cd frontend
npm install
npm run dev
```
