# Deploy TNEA Backend to Render

## Prerequisites
- GitHub account
- Render account (sign up at https://render.com)
- Your code pushed to a GitHub repository

## Step-by-Step Deployment

### 1. Push Your Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Set Up Redis on Render (Optional - if you need Redis)

1. Go to Render Dashboard
2. Click "New +" → "Redis"
3. Name it: `tnea-redis`
4. Choose the Free plan
5. Click "Create Redis"
6. Copy the "Internal Redis URL" (looks like: `redis://red-xxxxx:6379`)

### 3. Deploy the Web Service

#### Option A: Using render.yaml (Recommended)

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Click "Apply"

#### Option B: Manual Setup

1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `tnea-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app -k uvicorn.workers.UvicornWorker --workers 2 --bind 0.0.0.0:$PORT`
   - **Plan**: Choose your plan (Free tier available)

### 4. Set Environment Variables

In your Render service settings, add these environment variables:

1. **DATABASE_URL**
   ```
   postgresql+psycopg://neondb_owner:npg_BTs9xzZhSd3a@ep-fragrant-base-aikpveve-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   ```

2. **REDIS_URL** (if using Redis)
   ```
   redis://red-xxxxx:6379
   ```
   Or use Upstash Redis URL if you prefer

### 5. Deploy

- Click "Create Web Service" or "Manual Deploy"
- Wait for the build to complete (usually 2-5 minutes)
- Your API will be available at: `https://tnea-backend.onrender.com`

## Testing Your Deployment

Once deployed, test your API:

```bash
curl https://tnea-backend.onrender.com/
```

Expected response:
```json
{"Hello": "Tnea Backend"}
```

## Important Notes

### Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds (cold start)
- 750 hours/month free

### Database Connection
- Your Neon PostgreSQL database is already configured
- Tables will be created automatically on first startup
- All 512K+ rows are already migrated

### Monitoring
- View logs in Render Dashboard → Your Service → Logs
- Monitor health at: `https://tnea-backend.onrender.com/`

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is properly formatted
- Ensure Python version is 3.11 or compatible

### Database Connection Issues
- Verify DATABASE_URL environment variable is set correctly
- Check Neon database is active and accessible

### Service Won't Start
- Check logs in Render Dashboard
- Verify gunicorn command is correct
- Ensure port binding uses `$PORT` variable

## Updating Your Deployment

Push changes to GitHub:
```bash
git add .
git commit -m "Update description"
git push
```

Render will automatically redeploy on push (if auto-deploy is enabled).

## Custom Domain (Optional)

1. Go to your service settings
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records as instructed

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
