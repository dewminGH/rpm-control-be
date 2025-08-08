FROM python:3.12


WORKDIR /django-model-api

# COPY  requirements.txt /django-model-api/

COPY  . /django-model-api/

RUN  pip install  -r /django-model-api/requirements.txt

EXPOSE 8000
                                                     
CMD [ "python manage.py", "python manage.py runserver","0.0.0.0:8000" ]

#--no-cache-dir