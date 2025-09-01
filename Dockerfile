FROM python:3.13

ENV PATH=/home/app/.local/bin:${PATH}

COPY lunch-voting /home/app/lunch-voting

WORKDIR /home/app/lunch-voting

# Install and build
RUN pip install ".[test]"

# Make sure everything still works
RUN pytest

CMD ["fastapi", "run", "build/lib/app/app.py", "--port", "80"]
