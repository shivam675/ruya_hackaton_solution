# Deployment Guide

## Docker Deployment (Recommended)

### Prerequisites
- Docker 20+
- Docker Compose 2+
- Ollama running on host machine

### Steps

1. **Configure Environment**
   ```powershell
   cd E:\ruya_hackaton_solution\admin_dashboard\backend
   # Edit .env with your credentials
   ```

2. **Build and Start All Services**
   ```powershell
   cd E:\ruya_hackaton_solution\admin_dashboard
   docker-compose up --build
   ```

3. **Access Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8001/docs
   - MongoDB: localhost:27017

4. **Stop Services**
   ```powershell
   docker-compose down
   ```

5. **Clean Restart**
   ```powershell
   docker-compose down -v
   docker-compose up --build
   ```

## Manual Deployment

### Production Checklist

- [ ] MongoDB production instance configured
- [ ] SMTP credentials (Gmail App Password or SendGrid)
- [ ] Secret key generated (32+ characters random)
- [ ] Ollama running with required models
- [ ] Storage directories created
- [ ] Environment variables configured
- [ ] CORS origins updated for production domain

### Server Setup (Ubuntu Example)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3.11 python3-pip nodejs npm mongodb

# Clone repository
git clone <your-repo>
cd admin_dashboard

# Backend setup
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/hr-backend.service
```

**systemd service file:**
```ini
[Unit]
Description=HR Backend
After=network.target mongodb.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/admin_dashboard/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Reverse Proxy

```nginx
# Frontend
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Security Recommendations

1. **Change Default Credentials**
   - Update default user passwords in database
   - Delete demo accounts

2. **Environment Variables**
   - Never commit `.env` to git
   - Use secure random strings for SECRET_KEY
   - Use app-specific passwords for SMTP

3. **Firewall Rules**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

4. **HTTPS with Let's Encrypt**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

## Monitoring

### Docker Logs
```powershell
docker-compose logs -f backend
docker-compose logs -f interview_agent
```

### Health Checks
- Backend: http://localhost:8001/docs
- MongoDB: `docker exec hr_mongodb mongosh`

## Backup Strategy

### MongoDB Backup
```bash
# Backup
docker exec hr_mongodb mongodump --out /backup/$(date +%Y%m%d)

# Restore
docker exec hr_mongodb mongorestore /backup/20260214
```

### Storage Backup
```bash
# Backup entire storage folder
tar -czf storage_backup_$(date +%Y%m%d).tar.gz storage/
```

## Scaling Considerations

1. **MongoDB Replica Set** for high availability
2. **Load Balancer** for multiple backend instances
3. **Redis** for session management
4. **S3/MinIO** for file storage
5. **Kubernetes** for orchestration

## Troubleshooting

### Container Won't Start
```powershell
docker-compose logs <service-name>
docker-compose restart <service-name>
```

### Database Connection Issues
```powershell
docker exec -it hr_mongodb mongosh
# Check database
show dbs
use hr_recruitment_db
db.users.find()
```

### Permission Issues
```bash
# Fix storage permissions
sudo chown -R www-data:www-data storage/
sudo chmod -R 755 storage/
```

## Performance Tuning

### MongoDB Indexes
```javascript
db.candidates.createIndex({ "job_posting_id": 1, "status": 1 })
db.interviews.createIndex({ "candidate_id": 1, "status": 1 })
db.job_postings.createIndex({ "is_active": 1, "created_at": -1 })
```

### Uvicorn Workers
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

## CI/CD Pipeline Example

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@server 'cd /app && git pull && docker-compose up -d --build'
```
