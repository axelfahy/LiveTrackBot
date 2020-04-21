FROM python:3.8-alpine

WORKDIR /code

# Copy the project.
COPY . .

# Install dependencies for the cryptography package.
RUN apk add --no-cache \
        gcc \
        musl-dev \
        python3-dev \
        libffi-dev \
        openssl-dev

# Install the program.
RUN pip install -e .

# Run it.
CMD ["livetrackbot"]
