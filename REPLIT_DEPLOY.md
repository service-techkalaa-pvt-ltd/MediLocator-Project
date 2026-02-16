# 🚀 Deploying Medilocator to Replit

This guide will help you deploy the Medilocator project on Replit.

## 📋 Prerequisites

- A Replit account (free or paid)
- This project directory ready to upload

## 🎯 Quick Start

### Step 1: Create a New Repl

1. Go to [Replit](https://replit.com)
2. Click "Create Repl"
3. Choose "Import from GitHub" or "Upload files"
4. If uploading files, drag and drop this entire project folder

### Step 2: Configure Environment Variables

1. In your Repl, click on the "Secrets" tool (🔒 icon in left sidebar)
2. Add the following secrets:
   ```
   SECRET_KEY=your-super-secret-key-here-change-this
   DEBUG=True
   ALLOWED_HOSTS=*
   ```

3. **Important**: Generate a secure SECRET_KEY in Python:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

### Step 3: Initial Setup

Once your Repl is created, it should automatically:
- Install dependencies from `requirements.txt`
- Set up the Nix environment from `replit.nix`

If not, run these commands in the Shell:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 4: Create Superuser (Admin Account)

Run in the Shell:
```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 5: Load Initial Data (Optional)

If you have pharmacy data to load:
```bash
python load_pharmacy_data.py
```

### Step 6: Run the Application

Click the green "Run" button at the top, or run:
```bash
python manage.py runserver 0.0.0.0:3000
```

Your application should now be live! Replit will provide a URL like:
`https://your-repl-name.your-username.repl.co`

## 🔧 Configuration Files Created for Replit

### `.replit`
- Configures how Replit runs your application
- Sets up port forwarding (3000 → 80)
- Defines deployment commands

### `replit.nix`
- Installs system dependencies (Python, Tesseract OCR, etc.)
- Uses Nix package manager for reproducible builds

### `requirements.txt`
- All Python dependencies
- Includes Django, OCR libraries, ML libraries (optional)

### `.env.example`
- Template for environment variables
- Copy to `.env` or use Replit Secrets

### `.gitignore`
- Prevents committing sensitive files
- Excludes large ML models and cached files

## 🎨 Features Configured

✅ **Django 3.2.25** - Updated from 3.0.3 for security
✅ **WhiteNoise** - Serves static files efficiently
✅ **Gunicorn** - Production WSGI server
✅ **Environment Variables** - Secure configuration
✅ **Static Files** - Automatic collection and compression
✅ **Database** - SQLite (included, no setup needed)
✅ **OCR Support** - Tesseract included in Nix environment
✅ **Media Files** - Upload handling configured

## 📦 What's Included

- **Prescription Scanner** - OCR for medical prescriptions
- **Pharmacy Locator** - Find nearby pharmacies
- **Medicine Search** - Search pharmacy inventory
- **Admin Dashboard** - Manage data
- **User Profiles** - Patient accounts
- **ML Models** - Optional prescription detection (large files excluded)

## 🔒 Security Considerations

### For Production Deployment:

1. **Change SECRET_KEY**: Use Replit Secrets, never hardcode
2. **Set DEBUG=False**: In production
3. **Configure ALLOWED_HOSTS**: Set to your domain
4. **Use PostgreSQL**: For production (Replit supports it)
5. **Enable HTTPS**: Replit provides this automatically
6. **Review CSRF settings**: Ensure proper configuration

### Update Settings for Production:

In Replit Secrets, set:
```
DEBUG=False
ALLOWED_HOSTS=your-repl-name.your-username.repl.co
SECRET_KEY=your-very-secure-key
```

## 🗄️ Database Management

### SQLite (Default)
- Good for development and small deployments
- Stored in `db.sqlite3`
- Automatically backed up by Replit

### PostgreSQL (Recommended for Production)
1. Enable PostgreSQL in your Repl
2. Update `settings.py` DATABASES configuration:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': config('DB_NAME'),
           'USER': config('DB_USER'),
           'PASSWORD': config('DB_PASSWORD'),
           'HOST': config('DB_HOST'),
           'PORT': config('DB_PORT', default='5432'),
       }
   }
   ```
3. Add to requirements.txt: `psycopg2-binary==2.9.9`

## 🖼️ Static Files

Static files are handled by WhiteNoise:
- CSS, JavaScript, Images are served efficiently
- Automatically compressed
- Run `python manage.py collectstatic` after changes

## 📱 Testing the Application

1. **Home Page**: `https://your-repl-url/`
2. **Admin Panel**: `https://your-repl-url/admin/`
3. **User Dashboard**: `https://your-repl-url/dashboard/`
4. **Prescription Scanner**: `https://your-repl-url/scanner/`

## 🐛 Troubleshooting

### Issue: "Module not found"
**Solution**: Run `pip install -r requirements.txt`

### Issue: "No such table"
**Solution**: Run `python manage.py migrate`

### Issue: "Static files not loading"
**Solution**: 
```bash
python manage.py collectstatic --noinput
```

### Issue: "Tesseract not found"
**Solution**: Replit.nix should handle this. If not, verify `replit.nix` includes `tesseract`

### Issue: "Port already in use"
**Solution**: Replit handles ports automatically. Use `0.0.0.0:3000`

### Issue: ML Models not working
**Solution**: ML models are optional and large. For full ML features:
1. Uncomment ML dependencies in `requirements.txt`
2. Upload trained models to `ml_models/prescription_detector/`
3. Note: This may require Replit Hacker plan for more storage

## 📊 Resource Usage

### Free Tier:
- ✅ Basic Django application
- ✅ SQLite database
- ✅ OCR functionality
- ❌ Large ML models (size limits)

### Hacker/Pro Tier:
- ✅ All features
- ✅ Always-on deployment
- ✅ More storage for ML models
- ✅ Faster performance

## 🔄 Continuous Deployment

Replit automatically deploys when you:
1. Click "Deploy" button
2. Push to connected GitHub repo (if configured)

## 🌐 Custom Domain

1. Go to Deploy tab in your Repl
2. Click "Add custom domain"
3. Follow Replit's instructions
4. Update `ALLOWED_HOSTS` in Secrets

## 📞 Support

- **Django Documentation**: https://docs.djangoproject.com/
- **Replit Docs**: https://docs.replit.com/
- **Project Issues**: Check project README.md

## 🎉 Success!

Your Medilocator application is now deployed on Replit!

Remember to:
- ✅ Set secure environment variables
- ✅ Create admin account
- ✅ Load initial data
- ✅ Test all features
- ✅ Monitor resource usage

Happy coding! 🚀
