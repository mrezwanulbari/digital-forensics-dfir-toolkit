# Containerized case-tracker CLI — no local Python setup required.
# Build:  docker build -t dfir-case-tracker -f docker/Dockerfile .
# Run:    docker run --rm -v dfir_case_data:/root/.dfir_case_tracker dfir-case-tracker list-cases

FROM python:3.12-slim

LABEL maintainer="Shakil Md. Rezwanul Bari"
LABEL description="DFIR case tracker CLI — stdlib-only, containerized for portable use"

WORKDIR /app
COPY tooling/case-tracker/case_tracker.py /app/case_tracker.py

# Volume mount point for evidence files needing --file access from the host
VOLUME ["/evidence"]

ENTRYPOINT ["python3", "/app/case_tracker.py"]
CMD ["--help"]
