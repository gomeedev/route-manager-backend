# Supabase + Django + DRF + MySQL

[![Supabase](https://img.shields.io/badge/Supabase-%23000000.svg?logo=supabase&logoColor=3ECF8E)](https://supabase.com/)
[![Django](https://img.shields.io/badge/Django-5.2.x-092E20?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.x-a30000)](https://www.django-rest-framework.org/)
[![Railway](https://img.shields.io/badge/Railway-Deployed-0B0D0E?logo=railway)](https://railway.app)

> This is a backend project for a logistics process management system for courier companies in Colombia.


## Live Demo

- **API Base**: [https://route-manager-backend-production.up.railway.app](https://route-manager-backend-production.up.railway.app)
- **API Documentation**: [Swagger UI](https://route-manager-backend-production.up.railway.app/api/schema/swagger-ui/)
- **Frontend**: [Route Manager Frontend](https://route-manager-frontend.vercel.app)


### Prerequisites
- [Supabase](https://supabase.com) - Free account
- [Python](https://www.python.org/) >= 3.10
- [MySQL](https://www.mysql.com/) > 8.0.11 **or** [MariaDB](https://mariadb.org/) > 10.5
- [GROQ API Key](https://groq.com) for AI-powered assistant
- [LocationIQ API Key](https://locationiq.com) for geocoding services
- Package manager of your choice.

> [!IMPORTANT]
> If you use Xampp, consider that it includes versions of MariaDB greater than 10.5, since Django is not compatible with versions lower than 10.5. <br />
> As an alternative you can use the official DBMS from [Oracle](https://oracle.com) (MySQL) on a different port, for example: 3307.


## Installation

### Clone repository
Don't forget to clone the repository before navigating to any directory:
```sh
git clone https://github.com/gomeedev/route-manager-backend.git
cd route-manager-backend
```

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

> [!TIP]
> Generate a secure `SECRET_KEY` with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

The API will be available at http://localhost:8000


## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **Django Admin**: http://localhost:8000/admin/


## Environment Variables
The project has _.env_ files for project configuration in production and development, you can safely ignore that configuration and leave only one global _.env_.

### Environment Configuration

The project supports multiple environments through separate settings files:

- `config/settings/base.py` - Shared settings
- `config/settings/development.py` - Development-specific settings
- `config/settings/production.py` - Production-specific settings

Environment is controlled by the `ENVIRONMENT` variable in `.env`:
```env
# For development
ENVIRONMENT=development

# For production
ENVIRONMENT=production
```


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

# Geocoding
GEOCODING_KEY=your-geocoding-key

# Módel from AI
GROQ_API_KEY=your-model-key

# State 
ENVIRONMENT=development
```


## External Services Setup

### Supabase Configuration
1. Create a project at [supabase.com](https://supabase.com)
2. Go to **Project Settings** → **API**
3. Copy your `URL` and `service_role` key
4. Create a storage bucket named `images` for file uploads

### GROQ API Setup
1. Sign up at [groq.com](https://groq.com)
2. Generate an API key from your dashboard
3. Add it to your `.env` file

### LocationIQ Setup
1. Create an account at [locationiq.com](https://locationiq.com)
2. Get your API token from the dashboard
3. Add it to your `.env` file


## Deployment

### Deploy to Railway

1. Push your code to GitHub
2. Connect your repository to [Railway](https://railway.app)
3. Add a MySQL database service
4. Configure environment variables in Railway dashboard
5. Railway will automatically deploy your application


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Authors
- **Johann Gómez** - [GitHub Profile](https://github.com/gomeedev)


<div align="center">
  <p><strong>Academic project created with ❤️ for Colombian logistics companies</strong></p>
  <p><em>Last update: [11/12/2024]</em></p>
</div>
