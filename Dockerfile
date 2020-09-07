FROM python:alpine
WORKDIR /app
EXPOSE 80

ENV BTV_STORAGE_PATH "/app/storage"

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup -g 1000 -S btv && \
  adduser -u 1000 -S btv -G btv && \
  chown -R btv:btv /app
USER btv

# Make the directories so that ownership is correct
RUN mkdir -p "${BTV_STORAGE_PATH}"
VOLUME ["${BTV_STORAGE_PATH}"]

COPY --chown=btv . /app
CMD [ "python", "-u", "-m", "btv_on_demand" ]
