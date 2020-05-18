python manage.py makemigrations bubbleworld
python manage.py sqlmigrate bubbleworld 0001
python manage.py migrate
python manage.py loaddata init.json
导入初始数据

python manage.py runserver

//外键或ManyToManyFields用pk做属性的值

