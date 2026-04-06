## Проект DRF (деплой + CI/CD)

### Развёрнутое приложение (замени на свой адрес)

- **Публичный URL**: `http://158.160.233.15/` (пример из `.env.example`; при смене IP обнови `ALLOWED_HOSTS` в `.env` на сервере)

### Эндпоинты (через Nginx, порт 80)

- **API**: `http://<server-ip>/api/`
- **Админка**: `http://<server-ip>/admin/`
- **JWT**: `http://<server-ip>/api/token/`
- **JWT refresh**: `http://<server-ip>/api/token/refresh/`

Внутри Docker backend слушает `8000`, снаружи доступ — **только через nginx на 80**.

### Быстрый старт на сервере (Docker Compose)

1) Клонировать репозиторий и перейти в нужную ветку (для прод-обновлений обычно `develop`):

```bash
git clone <your-repo-url>
cd DRF
git checkout develop
```

2) Создать `.env` по шаблону:

```bash
cp .env.example .env
nano .env
```

3) Запуск:

```bash
docker compose up -d --build
docker ps
docker compose logs --tail=100 nginx
docker compose logs --tail=100 backend
```

Если на сервере только старая команда:

```bash
docker-compose up -d --build
```

### Безопасность (минимум по домашке)

- **SSH-ключи**: подключаться к серверу по ключу, парольный вход отключить.
- **Порты**: открыть только нужные (обычно 22/tcp, 80/tcp, 443/tcp).
- **UFW**:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

### Автозапуск деплоя (systemd)

Если нужно, чтобы приложение поднималось после перезагрузки сервера, можно создать systemd unit:

```bash
sudo nano /etc/systemd/system/drf.service
```

Содержимое:

```ini
[Unit]
Description=DRF docker-compose app
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/DRF
ExecStart=/usr/bin/docker compose up -d --build
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Далее:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now drf.service
sudo systemctl status drf.service
```

### CI/CD (GitHub Actions)

Workflow: `.github/workflows/ci_cd.yml`, запускается на **каждый push** во все ветки.

- **Tests**: `pip install -r requirements.txt`, затем `python manage.py test` (в CI выставляется `POSTGRES_DB=""`, чтобы тесты шли на SQLite без поднятия Postgres).
- **Lint (ruff)**: `ruff check .` (настройки в `pyproject.toml`).
- **Docker build**: `docker compose build` (перед сборкой создаётся временный `.env` из `.env.example` + тестовые секреты).
- **Deploy**: выполняется **только если успешно прошли tests + lint + docker build**. По SSH на сервере выполняется `git checkout develop && git pull`, затем пересборка контейнеров. То есть **код на сервере обновляется из ветки `develop`**; чтобы деплой подтянул свежие изменения, их нужно **смержить в `develop`**.

#### Secrets (GitHub → Settings → Secrets and variables → Actions)

- **SSH_HOST**: IP сервера
- **SSH_USER**: пользователь (например `ubuntu`)
- **SSH_PRIVATE_KEY**: приватный ключ (с переносами строк)
- **PROJECT_DIR**: папка проекта на сервере (например `/home/ubuntu/DRF`)

После настройки секретов пуш в `develop` (или merge PR в `develop`) обновит приложение на сервере при зелёном пайплайне.
