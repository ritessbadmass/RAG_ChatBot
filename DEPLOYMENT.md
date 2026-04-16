# Deployment Guide: Render Backend + Vercel Frontend

This guide explains how to deploy the Mutual Fund FAQ Assistant with:
- **Backend**: Render (FastAPI)
- **Frontend**: Vercel (Next.js)

## Project Structure

```
Rag_ChatBot/
├── backend/          # FastAPI backend for Render
│   ├── app/         # Application code
│   ├── scripts/     # Utility scripts
│   ├── requirements.txt
│   └── render.yaml
├── frontend/        # Next.js frontend for Vercel
│   ├── app/        # Next.js app router
│   ├── components/ # React components
│   ├── lib/        # API client
│   └── package.json
└── DEPLOYMENT.md   # This file
```

## Prerequisites

- GitHub account
- Render account (https://render.com)
- Vercel account (https://vercel.com)
- Groq API key
- Chroma Cloud credentials

## Step 1: Deploy Backend to Render

### 1.1 Push Code to GitHub

```bash
git add .
git commit -m "Reorganize for Render + Vercel deployment"
git push origin main
```

### 1.2 Create Render Web Service

1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `mutual-fund-faq-api`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 1.3 Set Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
CHROMA_CLOUD_TOKEN=your_chroma_token
CHROMA_CLOUD_TENANT=your_chroma_tenant
CHROMA_CLOUD_DATABASE=your_chroma_database
CHROMA_COLLECTION_NAME=mutual_fund_docs
MAX_QUERY_LENGTH=500
RATE_LIMIT_PER_MINUTE=30
FRONTEND_URL=    # Will update after Vercel deployment
```

### 1.4 Deploy

Click **Create Web Service**. Render will:
1. Install dependencies
2. Start the FastAPI server
3. Provide a URL like `https://mutual-fund-faq-api.onrender.com`

### 1.5 Verify Deployment

Visit `https://your-render-url.onrender.com/` to see:
```json
{
  "name": "Mutual Fund FAQ Assistant",
  "version": "1.0.0",
  "docs": "/docs"
}
```

## Step 2: Deploy Frontend to Vercel

### 2.1 Install Dependencies (Local)

```bash
cd frontend
npm install
```

### 2.2 Test Locally

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Visit http://localhost:3000

### 2.3 Create Vercel Project

1. Go to https://vercel.com/dashboard
2. Click **Add New...** → **Project**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 2.4 Set Environment Variables

In Vercel dashboard, go to **Settings** → **Environment Variables**:

```
NEXT_PUBLIC_API_URL=https://your-render-url.onrender.com
```

### 2.5 Deploy

Click **Deploy**. Vercel will:
1. Build the Next.js app
2. Deploy to a URL like `https://your-project.vercel.app`

### 2.6 Update Backend CORS

After Vercel deployment, copy your frontend URL and update Render environment:

```
FRONTEND_URL=https://your-project.vercel.app
```

Redeploy the backend to apply CORS changes.

## Step 3: Verify End-to-End

1. Visit your Vercel frontend URL
2. Type a test query: "What is the expense ratio of SBI Bluechip Fund?"
3. You should see a response from the backend

## Troubleshooting

### CORS Errors

If you see CORS errors in browser console:
1. Check `FRONTEND_URL` is set correctly in Render
2. Redeploy backend after updating env vars
3. Verify the URL includes `https://`

### Backend Not Responding

1. Check Render logs for errors
2. Verify all environment variables are set
3. Test health endpoint: `https://your-render-url.onrender.com/admin/health`

### Frontend Build Failures

1. Check Vercel build logs
2. Ensure `next.config.js` has `output: 'export'`
3. Verify all imports are correct

## Local Development

### Backend Only

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Only

```bash
cd frontend
npm install
npm run dev
```

### Full Stack

```bash
# Terminal 1
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend
npm run dev
```

Visit http://localhost:3000

## Environment Variables Summary

### Backend (Render)

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key | Yes |
| `CHROMA_CLOUD_TOKEN` | Chroma Cloud API key | Yes |
| `CHROMA_CLOUD_TENANT` | Chroma Cloud tenant ID | Yes |
| `CHROMA_CLOUD_DATABASE` | Chroma Cloud database name | Yes |
| `FRONTEND_URL` | Vercel frontend URL | After deploy |

### Frontend (Vercel)

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Render backend URL | Yes |

## Maintenance

### Updating Backend

1. Push changes to GitHub
2. Render auto-deploys

### Updating Frontend

1. Push changes to GitHub
2. Vercel auto-deploys

### Adding New Mutual Funds

1. Update URLs in `backend/scripts/ingest_data.py`
2. Run ingestion script locally or via GitHub Actions
3. Upload new data to Chroma Cloud

## Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs
