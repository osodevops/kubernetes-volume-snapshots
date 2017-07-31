FROM python:2.7.13-wheezy
ADD . /app
ENV PYTHONPATH=/app
RUN pip install -r /app/requirements.txt
CMD ["python", "-m", "kube_volume_snapshots"]