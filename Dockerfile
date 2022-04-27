FROM python:3.7-alphine

EXPOSE 5000/tcp

WORKDIR /yt_app
COPY requirements.txt ./
RUN pip install --np-cache-dir -r requirements.txt
COPY . .

RUN rm -r .env

CMD ['python', './wsgi.py']