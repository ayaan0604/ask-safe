# Ask Safe — Local Setup Guide

This guide explains how to configure and run Ask Safe locally.

Ask Safe consists of a FastAPI backend, a React frontend, a PostgreSQL database with pgvector, Supabase Storage for PDF files, and the Google Gemini API for AI-generated answers.

## Prerequisites

Install the following before starting:

- Python 3.11 or later, compatible with the project's dependencies.
- Node.js 20 LTS or another version supported by the frontend's Vite version.
- npm, included with Node.js.
- Git.
- Accounts on [Neon](https://neon.tech/), [Google AI Studio](https://aistudio.google.com/), and [Supabase](https://supabase.com/).

You do not need to install PostgreSQL locally if you use Neon for your database.

## 1. Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/ayaan0604/ask-safe
cd ask-safe
```



## 2. Configure the Backend Environment

Navigate to the backend directory:

```bash
cd backend
```

Create a local environment file by copying the provided example:

**macOS / Linux**

```bash
cp .env.example .env
```

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

Open `backend/.env` and replace the placeholder values with your own credentials.

### Environment Variables

#### `DATABASE_URL`

**Purpose:** Connects the backend to your PostgreSQL database.

How to obtain it:

1. Sign in to [Neon Console](https://console.neon.tech/).
2. Create a project, or select an existing project.
3. Open the **Connect** dialog.
4. Select the appropriate branch, database, and database role.
5. Copy the PostgreSQL connection string and paste it into `DATABASE_URL`.

It should resemble:

```env
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

Keep the connection string exactly as provided by Neon, including its SSL parameters.

Documentation: [Connect to Neon](https://neon.tech/docs/connect/connect-from-any-app)

#### `GEMINI_API_KEY`

**Purpose:** Authenticates requests to the Google Gemini API.

How to obtain it:

1. Open [Google AI Studio](https://aistudio.google.com/).
2. Navigate to the API Keys section.
3. Create or select a Gemini API key.
4. Copy the key into your `.env` file.

```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

API availability and rate limits depend on the model and your Google AI Studio project.

Documentation: [Gemini API Keys](https://ai.google.dev/gemini-api/docs/api-key)

#### `JWT_SECRET_KEY`

**Purpose:** Signs authentication tokens used by the backend.

Generate a strong random secret locally. For example, run:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated value into your `.env` file:

```env
JWT_SECRET_KEY=your_generated_random_secret
```

Do not use a predictable value such as `secret`, and do not reuse an API key as your JWT secret.

#### `ACCESS_TOKEN_EXPIRE_MINUTES`

**Purpose:** Defines how long an access token remains valid, in minutes.

The example configuration uses 30 minutes:

```env
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

You can keep this value unless you have a specific reason to change it.

#### `ALLOWED_ORIGINS`

**Purpose:** Specifies which frontend origins are allowed to make cross-origin requests to the backend.

For the default local frontend:

```env
ALLOWED_ORIGINS=http://localhost:5173
```

If your frontend runs on a different origin, update this value to match it. To add multiple origins, use commas to separate them

Do not add spaces around the equals sign.

#### `SUPABASE_URL`

**Purpose:** Identifies the Supabase project used for PDF storage.

How to obtain it:

1. Sign in to [Supabase](https://supabase.com/dashboard).
2. Open your project.
3. Navigate to the project's API settings or Connect dialog.
4. Copy the project URL.

It generally resembles:

```env
SUPABASE_URL=https://your-project-id.supabase.co
```

#### `SUPABASE_SERVICE_ROLE_KEY`

**Purpose:** Allows the backend to interact with Supabase Storage using server-side credentials.

How to obtain it:

1. Open your Supabase project.
2. Navigate to the API Keys section.
3. Locate the server-side secret key supported by your project's Supabase client integration.
4. Copy it into your backend `.env` file.

The existing implementation may expect the legacy `service_role` key. Use the compatible server-side key for the version of the Supabase client used by this project.

**Security warning:** This credential is highly privileged. Never put it in frontend code, expose it through a public API response, or commit it to GitHub.

Documentation: [Supabase API Keys](https://supabase.com/docs/guides/getting-started/api-keys)

#### `SUPABASE_BUCKET_NAME`

**Purpose:** Specifies the Supabase Storage bucket where original policy PDFs are stored.

How to configure it:

1. Open your Supabase project.
2. Navigate to **Storage**.
3. Create a bucket for the policy PDFs.
4. Keep it private, since the files may contain confidential information.
5. Set the environment variable to the exact bucket name.

For example, if your bucket is named `PDFs`:

```env
SUPABASE_BUCKET_NAME=PDFs
```

Bucket names must match exactly.

## 3. Prepare the Database

Ask Safe uses PostgreSQL with the pgvector extension for vector similarity search.

1. Ensure your Neon project and database are available.
2. Confirm that pgvector is enabled. If it is not, run the following in the Neon SQL Editor, provided your database role has permission:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Ensure the application's database schema is initialized using the project's existing table-creation or migration process.

If the repository includes database migration instructions or initialization scripts, follow those before starting the application.

The backend cannot run successfully until its database tables and vector support are available.

## 4. Install and Start the Backend

From the `backend/` directory, create a virtual environment.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the project's dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start the FastAPI application from the backend directory.

If the application instance is defined as `app` in `main.py`, run:

```bash
uvicorn app.main:app --reload
```


The backend should now be available at:

`http://127.0.0.1:8000`

FastAPI's interactive API documentation is normally available at:

`http://127.0.0.1:8000/docs`

Leave this terminal running.

## 5. Configure the Frontend

Open a second terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the dependencies:

```bash
npm install
```

Open `frontend/src/api.js` and locate the API base URL.

Set it to the address where your local backend is running:

```javascript
const API_BASE_URL = "http://127.0.0.1:8000";
```

If the file already contains a different variable name or uses an environment variable, update the existing configuration rather than creating a duplicate.

The frontend's API base URL must match the backend's address and port.

## 6. Start the Frontend

From the `frontend/` directory, run:

```bash
npm run dev
```

Vite will print the local development URL. With the default configuration, it is usually:

`http://localhost:5173`

Open that address in your browser.

Keep both the backend and frontend terminals running while using the application.

## 7. Verify the Setup

Before testing the complete workflow, confirm the following:

- [ ] The backend starts without environment or database errors.
- [ ] The frontend loads in the browser.
- [ ] Signup and login work.
- [ ] The backend can retrieve and store database records.
- [ ] Gemini generates answers to policy questions.
- [ ] Authorized users can access and download their permitted documents.
- [ ] Restricted users cannot retrieve confidential document content.
- [ ] HR administrators can upload and manage documents.
- [ ] Privileged account approvals work as expected.

To test document retrieval, upload a sample policy PDF through the HR administrator dashboard and ask a question whose answer appears in that document.

Use separate accounts for different roles when testing authorization.

## Troubleshooting

**Database connection errors**

Check `DATABASE_URL`, confirm that your Neon project is available, and verify that the connection string includes the required SSL parameters.

**Gemini API errors**

Verify `GEMINI_API_KEY`, check that the configured model is available to your project, and inspect the API's quota and rate-limit information.

**CORS errors**

Ensure `ALLOWED_ORIGINS` matches the actual frontend origin, including the protocol and port. Restart the backend after changing environment variables.

**PDF upload or download failures**

Check the Supabase project URL, server-side key, exact bucket name, bucket privacy settings, and the backend logs.

**Vector search errors**

Verify that pgvector is enabled and that the project's schema initialization process has completed successfully.

**Frontend cannot reach the backend**

Confirm that Uvicorn is running and that `frontend/src/api.js` points to the correct backend address and port.

## Security Notes

- Never commit `.env` files or real API keys.
- Keep `SUPABASE_SERVICE_ROLE_KEY` exclusively on the backend.
- Use private storage for confidential PDFs.
- Do not rely on frontend visibility controls to enforce document authorization.
- Test access permissions through the backend, not only through the user interface.
- Use synthetic or non-sensitive documents when experimenting with a local setup.

You're ready to run Ask Safe locally once both servers are running and the database, Gemini API, and Supabase Storage are correctly configured.
