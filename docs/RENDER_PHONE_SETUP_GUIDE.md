# JobGuard Render + Phone Setup Guide

This guide takes the current JobGuard backend and Android app from local-only mode to a hosted Render backend that your phone can use from anywhere.

## What you will get
- A Django backend deployed on Render
- A public API URL such as `https://your-service.onrender.com/api/v1`
- An Android APK that points to that hosted backend

## Before you start
Make sure you already have:
- a GitHub account
- a Render account
- this project pushed or ready to push to GitHub
- Flutter working on your machine
- the Android app already building locally

## Step 1: Push the project to GitHub
From the project root, make sure all recent changes are committed and pushed to a GitHub repository.

Render deploys from Git, so this step is required.

## Step 2: Create the backend on Render
In Render:
1. Click `New`
2. Choose `Blueprint`
3. Select your GitHub repository
4. Let Render read the included `render.yaml`

The repo already contains:
- `render.yaml`
- `build.sh`

These tell Render how to build and run the Django backend.

## Step 3: Set the environment variables in Render
Open the created web service and make sure these variables exist:

- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY=<use a strong random value>`
- `DJANGO_ALLOWED_HOSTS=<your-render-service>.onrender.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-render-service>.onrender.com`
- `JOBGUARD_PRELOAD_MODEL=False`

Recommended:
- `DATABASE_URL=<Render Postgres connection string>`

Optional:
- `TESSERACT_CMD=<only if you later deploy with a Tesseract-enabled environment>`

## Step 4: Choose the database
You have two paths:

### Fast demo path
- Let the app use SQLite
- This is okay for quick testing, but not ideal for real hosted usage

### Better hosted path
- Create a Render Postgres database
- Copy its external connection string
- Set it as `DATABASE_URL` in the backend service

If you want the safer path, use Postgres from the beginning.

## Step 5: Deploy and wait for the first build
Render will run:
- the build command from `build.sh`
- Django migrations
- static file collection
- Gunicorn to serve Django

The first deploy may take a while because this backend has heavier Python dependencies.

## Step 6: Verify the backend is live
When the deploy finishes, open this URL in your browser:

```text
https://<your-render-service>.onrender.com/api/v1/health
```

You should see:

```json
{
  "status": "ok",
  "service": "jobguard-api"
}
```

If that endpoint works, the app can talk to the backend.

## Step 7: Rebuild the Android app with the hosted API URL
From `mobile_app`, build the APK with your Render URL baked in:

```bash
flutter build apk --dart-define=JOBGUARD_API_BASE_URL=https://<your-render-service>.onrender.com/api/v1
```

If you prefer running directly to a connected phone instead of building an APK:

```bash
flutter run --dart-define=JOBGUARD_API_BASE_URL=https://<your-render-service>.onrender.com/api/v1
```

## Step 8: Install the updated APK on your phone
Install the newly built APK on the phone.

This is important: if the phone still has an older APK built against `10.0.2.2` or your local Wi-Fi IP, it will continue trying to use the old backend URL.

## Step 9: Test from the phone
Open the app and test these first:
- text scan
- URL scan
- scam reporting

These are the most likely features to work first on Render.

## Known limitations on free hosting
This backend is heavier than a normal Django app because it uses:
- `torch`
- `transformers`
- OCR-related dependencies
- scraping logic

That means free hosting may have slow cold starts or memory pressure.

## Important feature warning
### Image OCR
The image scanning flow depends on Tesseract.

Render standard Python services do not automatically include the Tesseract system binary, so image OCR may fail unless you later switch to a Docker-based deployment that installs it.

### URL scraping
Some websites may block hosted scraping or behave differently on cloud infrastructure.

## If deployment fails
Check these in Render:
- build logs
- start logs
- environment variables
- whether the health endpoint responds

The most common causes are:
- missing env vars
- heavy dependency install time
- OCR or browser dependencies not available on the host

## Best first production target
For the first hosted version, aim for:
- text scan working
- URL scan working when scraping succeeds
- scam reporting working

Treat image OCR as a second deployment step if needed.
