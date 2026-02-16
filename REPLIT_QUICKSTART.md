# 🚀 Replit Quick Reference Card

## Essential Commands

### First Time Setup
```bash
bash setup_replit.sh
python manage.py createsuperuser
```

### Run Application
```bash
python manage.py runserver 0.0.0.0:3000
```

### Database Commands
```bash
python manage.py makemigrations  # Create migrations
python manage.py migrate         # Apply migrations
python manage.py dbshell         # Access database shell
```

### Static Files
```bash
python manage.py collectstatic --noinput  # Collect static files
```

### Load Data
```bash
python load_pharmacy_data.py         # Load pharmacy data
python load_medicines.py             # Load medicine data
python add_pharmacy_inventory.py     # Add inventory
```

## Environment Variables (Replit Secrets)

Required secrets to add in Replit:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*
```

## File Structure (New Files for Replit)

```
📁 Project Root
├── .replit              # Replit configuration
├── replit.nix           # System dependencies
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── setup_replit.sh      # Quick setup script
├── start.sh             # Startup script
└── REPLIT_DEPLOY.md     # Full deployment guide
```

## URLs

- **Home**: `/`
- **Admin**: `/admin/`
- **Admin ML Dashboard**: `/admin-ml/`
- **Prescription Scanner**: `/scanner/`
- **Search**: `/search/`
- **User Profile**: `/profile/`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | `pip install -r requirements.txt` |
| No such table | `python manage.py migrate` |
| Static files 404 | `python manage.py collectstatic --noinput` |
| Tesseract error | Check `replit.nix` includes `tesseract` |
| Port in use | Use `0.0.0.0:3000` |

## Important Settings Changed

- ✅ `SECRET_KEY` now uses environment variables
- ✅ `DEBUG` configurable via environment
- ✅ `ALLOWED_HOSTS` configurable
- ✅ WhiteNoise middleware added for static files
- ✅ `STATIC_ROOT` changed to `staticfiles/`
- ✅ Tesseract paths support Linux/Windows

## Admin Access

1. Create superuser: `python manage.py createsuperuser`
2. Access admin: `https://your-repl-url/admin/`
3. Login with created credentials

## Deployment Checklist

- [ ] Upload project to Replit
- [ ] Add environment variables in Secrets
- [ ] Run `bash setup_replit.sh`
- [ ] Create superuser
- [ ] Load initial data
- [ ] Test all URLs
- [ ] Enable "Always On" (optional, requires paid plan)
- [ ] Add custom domain (optional)

## Resource Limits

**Free Tier:**
- RAM: Limited
- Storage: ~500MB
- Always-on: No
- Good for: Development, testing

**Hacker/Pro Tier:**
- RAM: More
- Storage: More
- Always-on: Yes
- Good for: Production

## Support Resources

- 📖 Full Guide: `REPLIT_DEPLOY.md`
- 🐛 Django Docs: https://docs.djangoproject.com/
- 💡 Replit Docs: https://docs.replit.com/

---
**Made for Replit deployment** | Last updated: 2026
