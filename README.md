# Phinder Challenge API

## Overview

This project is a **containerized REST API** implemented with FastAPI that enables
users to upload files and scan them for malware using **VirusTotal v3 API**.

While the original challenge specification referenced the v2 API, which returns
immediate scan results, VirusTotal v3 instead returns only an **analysis ID**.
Accommodating this difference required a **non-trivial redesign** of the workflow:
an **in-memory store** was implemented to track uploaded files, their SHA256 hash,
and continuously poll for analysis completion in the background. This design ensures
correct handling of multiple concurrent uploads and proper caching of results,
which goes beyond the straightforward v2 behavior.

To run the API locally, the `uv` CLI must be installed, along with `just` for
convenient task execution and management of environment variables and Docker commands.

- [uv: Python project manager](https://github.com/astral-sh/uv)
- [just: a better Makefile](https://github.com/casey/just)

---

## Features

- Upload files (max 32 MB) via `POST /update`
- Automatically calculate SHA256 hash and file size
- Prevent duplicate uploads by returning cached analysis
- Fetch analysis results by VirusTotal ID via `GET /analysis/{vt_id}`
- List all uploaded files with metadata via `GET /list_files`
- Standardized API response format with `success`, `timestamp`, and `data` fields
- Swagger UI documentation available at `/docs`
- Containerized with Docker
- `Justfile` for easy development and Docker management

---

## Installation

### 1. Clone Repository

```bash
git clone <repo-url>
cd phinder-api
```

### 2. Copy `.env.example` to `.env` and fill in:

```dotenv
PORT=8080
APIKEY_VIRUSTOTAL=<YOUR_VIRUSTOTAL_API_KEY>
APIURL_VIRUSTOTAL=https://www.virustotal.com/api/v3
```

### 3. Run Locally with Justfile

```make
# Start the API
just run

# Kill the port if blocked
just kill-port

# Format and lint the project
just format
```

## API Endpoints

### POST /update — Upload File

Summary: Upload a file to be scanned by VirusTotal.

Request:

- Form field: file (multipart/form-data)
- Maximum file size: 32 MB

```json
{
  "success": true,
  "timestamp": "2025-10-17T17:32:00",
  "data": {
    "vt_id": "Njk2MzBlNDU3NGVj...",
    "cached": false
  }
}
```

### GET /list_files — List Uploaded Files

Summary: Returns a dictionary of all uploaded files with metadata.

```json
{
  "success": true,
  "timestamp": "2025-10-17T17:35:00",
  "data": {
    "abcd1234...": {
      "size": "34.2 Mb",
      "uploaded_at": "2025-10-17T17:32:00",
      "analysis_id": "Njk2MzBlNDU3NGVj...",
      "analysis_status": "queued"
    }
  }
}
```

### GET /analysis/{vt_id} — Get Analysis Result

Summary: Fetch the current status and results of a VirusTotal analysis.

```json
{
  "success": true,
  "timestamp": "2025-10-17T17:36:00",
  "data": {
    "date": 1697548567,
    "results": { ... },
    "stats": { ... },
    "status": "completed"
  }
}
```

## Docker Usage

```make
# Build Image
just docker-build

# Run container
just docker-run
```

## Notes

- Files are stored temporarily in memory; no persistent database.
- Duplicate uploads are checked via SHA256 hash.
- VirusTotal v3 API returns an analysis ID, requiring a background task to periodically fetch results.
- Maximum file size: 32 MB.
- API responses are always in the APIResponse format: { success, timestamp, data, error }.
