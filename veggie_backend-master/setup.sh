export PYTHONPATH=$PWD
export DJANGO_SETTINGS_MODULE=veggies_service.db.settings.local
python manage.py makemigrations
python manage.py migrate