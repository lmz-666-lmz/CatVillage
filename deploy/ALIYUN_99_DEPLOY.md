# CatVillage Aliyun 99 元服务器部署说明

目标配置：1 核 2G 左右低配服务器，MySQL 单机，前端静态文件由 Nginx 托管，后端 FastAPI 使用 1 个 Uvicorn worker。

## 1. 系统准备

```sh
sudo apt update
sudo apt install -y nginx mysql-server python3-venv python3-pip curl
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

前端可以在本地构建后只上传 `frontpoint/dist`。如果要在服务器构建，需安装 Node.js 20.19+ 或 22.12+：

```sh
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

## 2. 初始化 MySQL

先修改 `backend/sql/mysql_init.sql` 里的 `replace-password`，再执行：

```sh
sudo mysql < backend/sql/mysql_init.sql
```

创建业务表并按 `.env` 中的 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 初始化管理员：

```sh
cd backend
python scripts/init_mysql.py
```

生产 `.env` 示例：

```env
DATABASE_URL=mysql+pymysql://catvillage_user:你的强密码@127.0.0.1:3306/catvillage?charset=utf8mb4
DB_POOL_SIZE=3
DB_MAX_OVERFLOW=2
DB_POOL_RECYCLE=1800
UPLOAD_MAX_BYTES=10485760
CORS_ORIGINS=http://你的域名,https://你的域名
SECRET_KEY=至少32位随机字符串
AI_API_KEY=你的DeepSeekKey
AI_BASE_URL=https://api.deepseek.com
```

## 3. 后端

```sh
cd /opt/catvillage/backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
```

确认启动无误后：

```sh
sudo mkdir -p /opt/catvillage/backend/uploads /opt/catvillage/backend/app/storage/emotion_audio
sudo chown -R www-data:www-data /opt/catvillage/backend/uploads /opt/catvillage/backend/app/storage
sudo cp /opt/catvillage/deploy/catvillage-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now catvillage-backend
```

## 4. 前端

```sh
cd /opt/catvillage/frontpoint
npm ci
npm run build
```

部署 Nginx：

```sh
sudo cp /opt/catvillage/deploy/nginx-catvillage.conf /etc/nginx/sites-available/catvillage
sudo ln -s /etc/nginx/sites-available/catvillage /etc/nginx/sites-enabled/catvillage
sudo nginx -t
sudo systemctl reload nginx
```

## 5. 低配服务器建议

- 后端保持 `--workers 1`，避免音频模型和 AI SDK 复制占用内存。
- MySQL 连接池保持 `DB_POOL_SIZE=3`、`DB_MAX_OVERFLOW=2`。
- 上传文件限制 10MB，Nginx 与后端保持一致。
- 模型文件会占内存，建议保留 2GB swap。
- 不要把 `.env` 提交到仓库；生产密钥只放服务器。
