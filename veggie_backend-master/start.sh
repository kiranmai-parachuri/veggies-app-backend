  kill -9 $(netstat -nlp|grep 2009| awk '{split($7,a,"/"); print a[1]}')
  kill -9 $(netstat -nlp|grep 2009| awk '{split($7,a,"/"); print a[1]}')
export PYTHONPATH=$PWD
export DJANGO_SETTINGS_MODULE=veggies_service.db.settings.local
python veggies_service/conf/service_app.py