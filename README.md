# Deployment Steps


Here’s a comprehensive **`django-cloudrun-deployment.md`** markdown file documenting **everything you've done step-by-step** to deploy your Django project to **Google Cloud Run** with automated deployments via **Cloud Build** and GitHub:

---

### 📘 `django-cloudrun-deployment.md`

````md
# Django Deployment to Google Cloud Run (With GitHub & Cloud Build Integration)

## 📦 Prerequisites

- Google Cloud Project created
- Billing enabled
- APIs enabled:
  - Cloud Build
  - Artifact Registry
  - Cloud Run
  - Secret Manager
- GitHub repository connected
- Docker and gcloud CLI installed

---

## 🛠️ 1. Setup Secrets in Secret Manager

Created 3 secrets in **Secret Manager** via console:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `GS_BUCKET_NAME`

These are used by Django on production to read securely.

---

## ⚙️ 2. Dockerfile for Django App

Basic production Dockerfile created:

```dockerfile
# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . /app/

RUN pip install --upgrade pip && pip install -r requirements.txt

# Required for Django on Cloud Run
ENV PORT 8080
ENV DJANGO_SETTINGS_MODULE=your_project.settings  # Replace with actual project name

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "your_project.wsgi:application"]
````

---

## 🧱 3. Cloud Build Configuration

Created `cloudbuild.yaml`:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/django-deploy-demo/django-repo/django-app:$SHORT_SHA', '.']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/django-deploy-demo/django-repo/django-app:$SHORT_SHA']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args: [
      'run', 'deploy', 'django-app',
      '--image', 'us-central1-docker.pkg.dev/django-deploy-demo/django-repo/django-app:$SHORT_SHA',
      '--region', 'us-central1',
      '--platform', 'managed',
      '--allow-unauthenticated',
      '--set-secrets', 'DJANGO_SECRET_KEY=DJANGO_SECRET_KEY:latest,DJANGO_DEBUG=DJANGO_DEBUG:latest,GS_BUCKET_NAME=GS_BUCKET_NAME:latest'
    ]

images:
  - 'us-central1-docker.pkg.dev/django-deploy-demo/django-repo/django-app:$SHORT_SHA'

options:
  logging: CLOUD_LOGGING_ONLY
```

---

## 🔁 4. Cloud Build Trigger Setup

* Connected GitHub repository under **Cloud Build > Triggers**
* Created trigger: `git-push-cai-test`

  * Repository: connected repo
  * Event: push to branch `production`
  * Build config: `cloudbuild.yaml`
  * Service account: default (or custom with minimum permission)
  * ✅ `Require approval` unchecked
  * ✅ `Send build logs to GitHub` unchecked

---

## 🌐 5. `settings.py` Production Config

Added support for secrets and GCS static/media:

```python
import os

# Static & media via GCS
GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")

if os.environ.get("K_SERVICE"):  # Only on Cloud Run
    STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/static/"
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

    MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/media/"
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DJANGO_DEBUG") == "True"
```

Also added `'storages'` to `INSTALLED_APPS`.

---

## ☁️ 6. Deployment Verification

* Confirmed Cloud Build runs after GitHub push to `production`
* Checked deployment logs in **Cloud Build > History**
* Cloud Run URL generated: `https://django-app-xxxxxxxxxx-uc.a.run.app`

---

## 🪵 7. Debugging & Logs

When facing `Service Unavailable`, checked:

* Logs in **Cloud Run > Services > Logs**
* Verified secrets were mounted
* Checked for common errors: missing env vars, missing `CMD`, incorrect port, etc.
* Fixed by:

  * Adding `ENV DJANGO_SETTINGS_MODULE`
  * Ensuring `CMD` uses gunicorn and correct WSGI path
  * Validating `STATIC_URL` and secret setup

---

## ✅ Final Verification Checklist

* [x] Push to `production` auto-triggers deployment ✅
* [x] Docker image builds and uploads to Artifact Registry ✅
* [x] Django app auto-deploys to Cloud Run ✅
* [x] Static and media files use GCS ✅
* [x] Secrets loaded securely via Secret Manager ✅
* [x] Logs visible in Cloud Logging ✅

```

---
