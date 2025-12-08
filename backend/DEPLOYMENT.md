# Deployment Guide - Hetzner Setup

## PostgreSQL Database on Hetzner

### Initial Setup

1. **Create Hetzner Server/Database**
   - Hetzner Cloud: Create a server or use managed database
   - Recommended: Use Hetzner Cloud with PostgreSQL 14+

2. **Configure PostgreSQL Access**

   SSH into your Hetzner server:
   ```bash
   ssh root@your-hetzner-ip
   ```

   Install PostgreSQL (if self-hosting):
   ```bash
   apt update
   apt install postgresql postgresql-contrib
   ```

3. **Create Database and User**

   ```bash
   sudo -u postgres psql
   ```

   In PostgreSQL shell:
   ```sql
   CREATE DATABASE friction_db;
   CREATE USER friction_user WITH PASSWORD 'your-secure-password';
   GRANT ALL PRIVILEGES ON DATABASE friction_db TO friction_user;
   \q
   ```

4. **Configure Remote Access**

   Edit PostgreSQL config:
   ```bash
   nano /etc/postgresql/14/main/postgresql.conf
   ```

   Change:
   ```
   listen_addresses = '*'
   ```

   Edit pg_hba.conf:
   ```bash
   nano /etc/postgresql/14/main/pg_hba.conf
   ```

   Add:
   ```
   host    friction_db    friction_user    0.0.0.0/0    md5
   ```

   Restart PostgreSQL:
   ```bash
   systemctl restart postgresql
   ```

### Security Hardening

1. **Firewall Configuration**
   ```bash
   # Allow only your application server IP
   ufw allow from YOUR_APP_SERVER_IP to any port 5432
   ufw enable
   ```

2. **Use SSL Connections**

   Update DATABASE_URL:
   ```env
   DATABASE_URL=postgresql://friction_user:password@hetzner-ip:5432/friction_db?sslmode=require
   ```

3. **Strong Password**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

### Backend Deployment Options

#### Option 1: Deploy Backend on Same Hetzner Server

**Advantages:**
- Lowest latency to database
- No external database traffic
- Simpler networking

**Setup:**
```bash
# Install Python and dependencies
apt install python3.11 python3-pip python3-venv

# Clone repository
git clone https://github.com/Nardo758/Project-Spark.git
cd Project-Spark/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
nano .env
# DATABASE_URL=postgresql://friction_user:password@localhost:5432/friction_db

# Initialize database
python init_db.py

# Run with systemd
sudo nano /etc/systemd/system/friction-api.service
```

Add systemd service:
```ini
[Unit]
Description=Friction FastAPI Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/root/Project-Spark/backend
Environment="PATH=/root/Project-Spark/backend/venv/bin"
ExecStart=/root/Project-Spark/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
systemctl enable friction-api
systemctl start friction-api
```

#### Option 2: Deploy Backend on Different Server

Use DATABASE_URL with Hetzner server IP:
```env
DATABASE_URL=postgresql://friction_user:password@HETZNER_DB_IP:5432/friction_db?sslmode=require
```

### Nginx Reverse Proxy

Install Nginx:
```bash
apt install nginx certbot python3-certbot-nginx
```

Configure:
```bash
nano /etc/nginx/sites-available/friction-api
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and get SSL:
```bash
ln -s /etc/nginx/sites-available/friction-api /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
certbot --nginx -d api.yourdomain.com
```

### Environment Variables for Production

```env
# Database
DATABASE_URL=postgresql://friction_user:STRONG_PASSWORD@hetzner-ip:5432/friction_db?sslmode=require

# Security (generate new keys!)
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Scraper API Key (change this!)
SCRAPER_API_KEY=your-scraper-api-key-change-from-default
```

### Database Backups

Set up automated backups:
```bash
# Create backup script
nano /root/backup-friction-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/root/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U friction_user friction_db > $BACKUP_DIR/friction_db_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -name "friction_db_*.sql" -mtime +7 -delete
```

```bash
chmod +x /root/backup-friction-db.sh
# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /root/backup-friction-db.sh
```

### Monitoring

Install monitoring tools:
```bash
apt install htop iotop postgresql-contrib
```

Monitor database connections:
```sql
SELECT * FROM pg_stat_activity WHERE datname = 'friction_db';
```

### Performance Tuning

Edit PostgreSQL config for better performance:
```bash
nano /etc/postgresql/14/main/postgresql.conf
```

Recommended settings for 4GB RAM server:
```
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 5242kB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Testing Connection

Test database connection:
```bash
# From application server
psql "postgresql://friction_user:password@hetzner-ip:5432/friction_db"
```

Test API:
```bash
curl https://api.yourdomain.com/health
```

### Troubleshooting

**Connection Refused:**
- Check firewall: `ufw status`
- Check PostgreSQL is listening: `netstat -an | grep 5432`
- Check PostgreSQL logs: `tail -f /var/log/postgresql/postgresql-14-main.log`

**Slow Queries:**
- Enable query logging in postgresql.conf
- Check indexes: Run `EXPLAIN ANALYZE` on slow queries
- Monitor with: `SELECT * FROM pg_stat_statements;`

**Authentication Errors:**
- Verify credentials in .env
- Check pg_hba.conf settings
- Check user permissions: `\du` in psql

## Cost Optimization

**Hetzner Pricing (as of 2024):**
- CX11 (2GB RAM): ~€4/month - Good for development
- CPX11 (2GB RAM + dedicated CPU): ~€5/month - Minimum for production
- CPX21 (4GB RAM): ~€10/month - Recommended for production
- CPX31 (8GB RAM): ~€19/month - For higher traffic

**Database Server Recommendations:**
- Development: CX11 or CPX11
- Production (< 1000 users): CPX21
- Production (< 10000 users): CPX31
- Production (> 10000 users): Consider managed database or dedicated server

## Next Steps

1. ✅ Set up Hetzner server
2. ✅ Install and configure PostgreSQL
3. ✅ Update .env with connection string
4. ✅ Run database initialization
5. ✅ Deploy FastAPI backend
6. ✅ Set up Nginx reverse proxy
7. ✅ Configure SSL with Let's Encrypt
8. ✅ Set up automated backups
9. ✅ Configure monitoring
10. ✅ Test scraper endpoints

## Support

- Hetzner Docs: https://docs.hetzner.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- FastAPI Docs: https://fastapi.tiangolo.com/
