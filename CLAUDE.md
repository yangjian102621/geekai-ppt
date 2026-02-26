# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered PPT generation platform called "极客学长 docs.geekai.me". It consists of a FastAPI backend and a React/TypeScript frontend that uses the GeekAI API (Google Gemini models) to generate presentation slides with modern tech aesthetics.

## Development Commands

### Backend (Python/FastAPI)

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server (with hot reload)
python main.py
# Or using uvicorn directly:
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Server runs on http://localhost:8002
```

### Frontend (React/Vite)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
# Server runs on http://localhost:3000

# Build for production
npm run build
# Output directory: build/
```

## Architecture

### Backend Architecture

The backend follows a modular service-oriented architecture:

- **main.py** - FastAPI application entry point with all API routes
  - Session management endpoints (`/sessions`, `/session/*`)
  - PPT planning and generation (`/ppt/plan`, `/ppt/generate_slide`)
  - API key management (`/api/key/*`)
  - File upload handling (`/upload/doc`)
  - Static file serving for generated images (`/images`)

- **session_manager.py** - Handles session persistence and slide version control
  - Sessions stored as JSON files in `storage/sessions/`
  - Each slide supports multiple versions with version IDs
  - Tracks chat history and slide context
  - Supports slide insertion, deletion, and reordering

- **llm_planner.py** - LLM-based PPT outline generation
  - Uses `google/gemini-3-pro-preview` for logical planning
  - Generates structured JSON outlines with visual prompts
  - Enforces "Modern Tech/Internet Style" aesthetic
  - Supports insertion mode for adding slides mid-presentation

- **image_gen.py** - Image generation using Gemini vision models
  - Uses `google/gemini-3-pro-image-preview` for slide rendering
  - Two modes: creation (new slides) and modification (edit existing)
  - Implements retry logic with 3 attempts
  - Supports custom style templates

- **file_handler.py** - Document text extraction
  - Supports PDF, DOCX, TXT, MD formats
  - Extracts text for context (max 32k chars)
  - Uses PyPDF2 and python-docx libraries

- **utils.py** - Utility functions for image handling

### Frontend Architecture

React-based SPA with component-driven architecture:

- **components/login/** - Landing page with API key setup and project history
- **components/editor/** - Main PPT editor with canvas, filmstrip, and version control
- **components/ui/** - Radix UI component library (50+ components)
- **services/api.ts** - API client for backend communication
- **types/** - TypeScript type definitions

### Key Design Patterns

1. **Session-based workflow**: Each PPT project is a session with persistent state
2. **Version control per slide**: Every slide maintains a history of generated versions
3. **Two-phase generation**:
   - Phase 1: LLM plans the outline with visual prompts
   - Phase 2: Image model renders each slide based on prompts
4. **Style consistency**: Previous slide prompts are passed as reference for visual coherence
5. **Middleware for CORS**: Custom middleware ensures image serving works cross-origin

## Environment Configuration

### Backend `.env` (backend/.env)

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://api.geekai.pro
MODEL_LOGIC=google/gemini-3-pro-preview
MODEL_IMAGE=google/gemini-3-pro-image-preview
PORT=8002
```

The API key can be set via the frontend UI, which calls `/api/key/save` to update the `.env` file.

### Frontend Configuration

Frontend uses Vite with default port 3000. Backend API URL is hardcoded in `services/api.ts` (typically `http://localhost:8002`).

## Important Implementation Details

### Image Storage and Serving

- Generated images are saved to `storage/images/` with session-based organization
- Images are served via FastAPI's StaticFiles mount at `/images`
- Custom middleware adds CORS headers and disables caching for image routes
- Image paths in session data are stored as relative paths (e.g., `/images/session_id/filename.png`)

### Slide Generation Modes

1. **Creation Mode** (`is_insertion=false, is_modification=false`):
   - Generates new slide from scratch
   - Uses previous slide prompt for style consistency

2. **Modification Mode** (`is_modification=true`):
   - Requires `base_image_url` parameter
   - Converts local image to base64 for vision model input
   - Maintains slide history context

3. **Insertion Mode** (`is_insertion=true`):
   - Calls `plan_insertion_prompts()` to determine how many slides to insert
   - Generates multiple slides in sequence
   - Adjusts indices of subsequent slides

### Version Control Logic

- Each slide has a `current_version_id` pointer
- Versions cannot be deleted if it's the only version remaining
- When deleting the current version, pointer automatically moves to the latest version
- Version IDs are 8-character UUIDs

### Error Handling

- Image generation has 3-retry logic with 2-second delays
- API key validation via `/api/key/test` endpoint (calls the GeekAI API `models.list()` or equivalent)
- File extraction errors return empty string rather than failing

## Common Workflows

### Adding a New API Endpoint

1. Define Pydantic model in `backend/main.py` if needed
2. Add route handler with appropriate HTTP method decorator
3. Use `SessionManager` for state persistence
4. Return JSON responses with proper error handling

### Modifying Slide Generation Prompts

The visual style is controlled by:
- `DEFAULT_STYLE_PROMPT` constant in `image_gen.py`
- System prompt in `llm_planner.py` (lines 28-79)
- Custom style templates can be passed via `style_template` parameter

### Testing API Key Changes

After modifying API key handling:
1. Test GET `/api/key` - should return current key
2. Test POST `/api/key/save` - should update `.env` file
3. Test POST `/api/key/test` - should validate the key with the GeekAI API
4. Verify `update_env_file()` function updates both file and `os.environ`

## Dependencies

### Backend
- fastapi, uvicorn - Web framework
- openai - GeekAI-compatible API client
- pypdf, python-docx, PyPDF2, pdf2image - Document processing
- python-dotenv - Environment variable management

### Frontend
- React 18.x with TypeScript
- Vite 6.x for build tooling
- Radix UI component library (extensive set of primitives)
- jspdf for PDF export
- Tailwind CSS for styling

## Storage Structure

```
storage/
├── sessions/           # Session JSON files
│   └── {uuid}.json    # Each session's state
└── images/            # Generated slide images
    └── {session_id}/  # Images organized by session
```

## Notes for Future Development

- The frontend expects backend at `http://localhost:8002` - update `services/api.ts` if deploying
- Image generation can fail silently - check retry logic in `_call_with_retry()`
- Session files grow with chat history - consider implementing cleanup/archival
- The system uses Chinese comments in some files - maintain consistency when adding code
- Custom style templates are optional - system falls back to `DEFAULT_STYLE_PROMPT`
