FROM python:3.7

# set work directory
WORKDIR /usr/src/m2m_express

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN  python manage.py collectstatic --noinput

# copy entrypoint.sh
# COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
#ENTRYPOINT ["/usr/src/m2m_express/entrypoint.sh"]
