FROM python:3.10.12-slim as build

ENV PATH="/home/python/.local/bin:${PATH}"
ENV PATH="/app/.venv/bin:${PATH}"
ENV VIRTUAL_ENV="/app/.venv"

WORKDIR /app
COPY requirements.txt .
RUN python -m venv .venv && pip install -r requirements.txt

FROM python:3.10.12-slim as runtime

RUN groupadd -g 1000 python && useradd -c python -g python -m -u 1000 python

ENV PATH="/home/python/.local/bin:${PATH}"
ENV PATH="/app/.venv/bin:${PATH}"
ENV VIRTUAL_ENV="/app/.venv"

COPY --from=build --chown=python:python ${VIRTUAL_ENV} ${VIRTUAL_ENV}/
COPY --chown=python:python . /app/

USER python

ENTRYPOINT ["python"]
CMD ["/app/main.py"]