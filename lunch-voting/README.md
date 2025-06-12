## Stack

This project uses the following libraries:

- **FastAPI** for the API/server. Chosen because of its simplicity and flexibility, and because 
  I'm not all that familiar with Django.
- **SQLite** for the database. It's far from an ideal engine, but should be more than enough for 
  prototyping purposes.
- **SQLAlchemy** for accessing the database within the code.
- **Pydantic** for data parsing/validation/handling and settings management (**pydantic-settings**).


## Prerequisites

This project has been built and tested with Python 3.13. That is the only version guaranteed to 
work.

Note that it uses features introduced in Python 3.12. In particular, [type parameter 
lists](https://docs.python.org/3/reference/compound_stmts.html#type-parameter-lists), so any 
earlier versions won't work at all. It *should* run just fine on Python 3.12, but I haven't 
tested it explicitly.


## Running locally

From the repository root, running the server locally should be as simple as:

```
fastapi run src/app/app.py
```

For full debugging capabilities, you can run it with `fastapi dev` instead.


## Running the docker container

Everything should work out of the box with the provided docker setup with just `docker compose 
up --build` from the repository root.

The server running within the docker container can be reached locally on `http://localhost:8000`. You 
can test that it's up and running by opening the documentation page on `http://localhost:8000/docs`.


## Running the tests

You can validate that all tests are passing by running `pytest` from within the `lunch-voting` 
directory:

```
cd lunch-voting
pytest
```

## API documentation

You can find the documentation for all the endpoints on `http://localhost:8000/docs`.