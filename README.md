# URL Alias Service

A minimal URL shortening REST API built with FastAPI and SQLite

Provides:

- Public endpoint for redirecting short URLs to original URLs
- Private endpoints (protected by Basic Auth) to create/manage short URLs and view click statistics
- Automatic Swagger/OpenAPI documentation

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/0then0/impulse-url-alias-service
cd impulse-url-alias-service
```

### 2. Create a Python virtual environment

#### macOS / Linux / Git Bash

```bash
python3.10 -m venv venv
source venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

1. Copy or create a file named `.env` in the project root.
2. Add at least the following variables:

   ```env
   DATABASE_URL=sqlite:///./shortener.db
   SECRET_KEY=your-random-secret-string
   ACCESS_TOKEN_EXPIRE_SECONDS=86400
   BASIC_AUTH_USERNAME=admin
   BASIC_AUTH_PASSWORD_HASH=placeholder-hash
   ```

   - `DATABASE_URL`: SQLite file URL (relative path).
   - `SECRET_KEY`: Any random string (unused by BasicAuth but reserved).
   - `ACCESS_TOKEN_EXPIRE_SECONDS`: Default TTL (in seconds) for new short URLs (e.g., 86400 = 1 day).
   - `BASIC_AUTH_USERNAME`: The username for Basic Authentication.
   - `BASIC_AUTH_PASSWORD_HASH`: A placeholder—actual password hashing is done via the `create_admin.py` script.

> **Note:** You do not need to pre-compute `BASIC_AUTH_PASSWORD_HASH` if you will create an admin user via the script below.

## Database Migrations

```bash
alembic upgrade head
```

This will create `shortener.db` and all required tables (`users`, `urls`, `click_stats`).

## Create an Admin User

To create a Basic Auth user (e.g., “admin”), run:

```bash
python app/scripts/create_admin.py
```

- You will be prompted for a username and password.
- The script will hash the password and insert a record into the `users` table.
- After successful creation, use these credentials when accessing any private endpoints.

## Run the Server

With the virtual environment active and the `.env` file in place:

```bash
uvicorn app.main:app --reload
```

The API server listens on `http://127.0.0.1:8000` by default.

## Testing the Service

### 1. Health Check

```bash
curl http://127.0.0.1:8000/ping
```

Expected response:

```json
{ "pong": "ok" }
```

### 2. Authenticate in Swagger UI

1. Open your browser at `http://127.0.0.1:8000/docs`.
2. Click **Authorize** in the top-right.
3. Enter the username and password you created via `create_admin.py`.
4. Close the dialog. All private endpoints now send Basic Auth headers automatically.

### 3. Create a Short URL

- **Endpoint:** `POST /api/v1/urls/` (Private)

- **Request Body (JSON):**

  ```json
  {
  	"original_url": "https://example.com/some/long/path",
  	"expire_seconds": 3600
  }
  ```

- **Response (JSON):**

  ```json
  {
  	"id": 1,
  	"original_url": "https://example.com/some/long/path",
  	"short_path": "Ab3XyZ12",
  	"created_at": "2025-06-02T10:23:45.123456",
  	"expires_at": "2025-06-02T11:23:45.123456",
  	"is_active": true
  }
  ```

### 4. List Your URLs

- **Endpoint:** `GET /api/v1/urls/` (Private)
- **Response:** Array of URL objects (same fields as above).

### 5. Redirect via Short URL

- In your browser or via curl, visit:

  ```
  http://127.0.0.1:8000/{short_path}
  ```

  Example:

  ```bash
  curl -v http://127.0.0.1:8000/Ab3XyZ12
  ```

- The service will:

1. Look up `Ab3XyZ12` in the `urls` table.
2. If found and still active & unexpired, log a click and return a 307/308 redirect to the original URL.
3. If inactive or expired, return an error (HTTP 400 or HTTP 410).

### 6. Deactivate a Short URL

- **Endpoint:** `PATCH /api/v1/urls/{url_id}/deactivate` (Private)
- **URL Parameter:** `url_id` (integer ID from the “List Your URLs” response)
- **Response:** The updated URL object, with `"is_active": false`.

### 7. View Click Statistics

- **Endpoint:** `GET /api/v1/stats/` (Private)
- **Response:** Array of objects sorted by `total_clicks DESC`:

  ```json
  [
    {
      "id": 1,
      "short_path": "Ab3XyZ12",
      "original_url": "https://example.com/some/long/path",
      "total_clicks": 5,
      "last_clicked_at": "2025-06-02T12:34:56.789012",
      "is_active": true,
      "expires_at": "2025-06-02T11:23:45.123456"
    },
  ]
  ```
