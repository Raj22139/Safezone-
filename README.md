# 🛡️ SafeZone AI
### AI-Based Crime and Area Safety Intelligence System

Django + PostgreSQL + Scikit-learn based web application

---

## 📁 Project Structure

```
safezone/
├── safezone/           # Main Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/           # User auth, registration, login, profile
├── crime/              # Core models: Area, CrimeRecord, SearchHistory
├── dashboard/          # User dashboard (search, history, saved areas)
├── admin_panel/        # Admin panel (crime CRUD, user management, analytics)
├── ml/                 # Scikit-learn risk scoring engine
│   ├── risk_engine.py
│   └── management/commands/train_model.py
├── templates/          # All HTML templates
├── static/             # CSS, JS, images
├── media/              # User uploads
├── requirements.txt
└── manage.py
```

---

## ⚙️ Setup Instructions

### 1. Clone / Extract Project
```bash
cd safezone_project
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` file:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=safezone_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Create PostgreSQL Database
```sql
CREATE DATABASE safezone_db;
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Train ML Model
```bash
python manage.py train_model
```

### 8. Seed Sample Data
```bash
python manage.py seed_data
```
This creates:
- **Admin user**: `admin` / `admin123`
- 15 sample areas (Delhi, Mumbai, Bangalore)
- 100+ crime records

### 9. Run Development Server
```bash
python manage.py runserver
```

---

## 🌐 URLs

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Landing Page |
| `http://127.0.0.1:8000/accounts/register/` | User Registration |
| `http://127.0.0.1:8000/accounts/login/` | User Login |
| `http://127.0.0.1:8000/dashboard/` | User Dashboard |
| `http://127.0.0.1:8000/admin-panel/` | Admin Panel |
| `http://127.0.0.1:8000/django-admin/` | Django Built-in Admin |

---

## 🔑 Default Login

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |

---

## 🧠 ML Risk Engine

The system uses a **RandomForest Regressor** from Scikit-learn.

**Features used:**
- Total crime incidents
- Average severity
- Count per crime type (theft, violence, traffic, fraud, burglary, assault)
- Weighted severity score

**Risk Levels:**
- 🟢 **Low** (0–35): Minimal crime
- 🟡 **Medium** (36–65): Moderate activity
- 🔴 **High** (66–100): Significant crime

---

## 🗄️ Database Models

| Model | App | Description |
|-------|-----|-------------|
| `UserProfile` | accounts | Extended user profile with phone, city, role |
| `Area` | crime | Geographic area with risk score |
| `CrimeRecord` | crime | Individual crime incidents |
| `SearchHistory` | crime | User search log |
| `SavedArea` | crime | Bookmarked areas |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, Django 4.2
- **Database**: PostgreSQL
- **ML**: Scikit-learn (RandomForestRegressor)
- **Frontend**: Bootstrap 5, Vanilla JS (AJAX)
- **Auth**: Django Session-based Authentication
- **Static Files**: WhiteNoise

---

## 📦 Production Deployment

```bash
# Collect static files
python manage.py collectstatic

# Set in .env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Run with Gunicorn
gunicorn safezone.wsgi:application --bind 0.0.0.0:8000
```
