# Supabase + Django + DRF + MySQL

[![Supabase](https://img.shields.io/badge/Supabase-%23000000.svg?logo=supabase&logoColor=3ECF8E)](https://supabase.com/)
[![Django](https://img.shields.io/badge/Django-5.2.x-092E20?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.x-a30000)](https://www.django-rest-framework.org/)

> This is a backend project for a logistics process management system for courier companies in Colombia.


### Prerequisites
- [Supabase](https://supabase.com) - Free account
- [Python](https://www.python.org/) >= 3.10
- [MySQL](https://www.mysql.com/) > 8.0.11 **or** [MariaDB](https://mariadb.org/) > 10.5
- Package manager of your choice.

> [!IMPORTANT]
> If you use Xampp, consider that it includes versions of MariaDB greater than 10.5, since Django is not compatible with versions lower than 10.5. <br />
> As an alternative you can use the official DBMS from [Oracle](https://oracle.com) (MySQL) on a different port, for example: 3307.


### Clone repository
Don't forget to clone the repository before navigating to any directory:
```sh
git clone https://github.com/gomeedev/route-manager-backend.git
cd route-manager-backend
```

## Installation

Create virtual environment.
```sh
python -m venv venv
```

Activate virtual environment.
```sh
# Windows:
venv\Scripts\activate

Linux/Mac:
source venv/bin/activate
```

Install dependencies.
```
pip install -r requirements.txt
```

Create Database.
```
CREATE DATABASE route_manager;
```

Run migrations.
```
python manage.py migrate
```

Start server.
```
python manage.py runserver
```

> [!NOTE]
> Don't forget to create a .env file in the root directory.


## Environment Variables
The project has _.env_ files for project configuration in production and development, you can safely ignore that configuration and leave only one global _.env_.

Create _.env_ file in the root directory with the following environment variables:

**.env**
```env
# --Settings--
SECRET_KEY=YOUR_SECRET_KEY
DEBUG=True

# Cors
ALLOWED_HOSTS=localhost,127.0.0.1,route-manager-frontend.vercel.app
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://route-manager-frontend.vercel.app

# BD
DB_ENGINE=django.db.backends.mysql
DB_NAME=route_manager
DB_USER=root
DB_PASSWORD=0202
DB_HOST=localhost
DB_PORT=3307

# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_BUCKET=images

# State 
ENVIRONMENT=development
```
