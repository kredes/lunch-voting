# lunch-voting

## Task

Implement voting REST API for choosing where to go to lunch. Imagine that this API will be consumed by a front-end developer to create UI on top of it. Approach this task as you would approach a real assignment when you are at work. Use this assignment to show us what you care about in terms of code quality, architecture, tests, etc.

Basic business rules/requirements:
1. Everyone can add/remove/update restaurants
2. Every user gets X (hardcoded, but "configurable") votes per
day. Each vote has a "weight". First user vote on the same restaurant counts as 1, second as 0.5, 3rd and all subsequent votes as 0.25.
2.1. If a voting result is the same on multiple restaurants, the winner is the one who got more distinct users to vote on it.
3. Every day vote amounts are reset. Unused previous day votes are lost.
4. Show the history of selected restaurants per time period. For example, the front-end should be able to query which restaurant won the vote on a specific day.
5. Do not forget that frontend dev will need a way to show which restaurants users can vote on and which restaurant is a winner
6. Readme on how to use the API, launch the project, etc.

---

## Stack

This project uses the following libraries:

- **FastAPI** for the API/server. Chosen because of its simplicity and flexibility, and because 
  I'm not all that familiar with Django.
- **SQLite** for the database. It's far from an ideal engine, but should be more than enough for 
  prototyping purposes.
- **SQLAlchemy** for accessing the database within the code.
- **Pydantic** for data parsing/validation/handling and settings management (**pydantic-settings**).


## Running locally

### Prerequisites

This project has been built and tested with Python 3.13. That is the only version guaranteed to 
work.

Note that it uses features introduced in Python 3.12 (in particular, [type parameter 
lists](https://docs.python.org/3/reference/compound_stmts.html#type-parameter-lists)) so any 
earlier versions won't work at all. It *should* run just fine on Python 3.12, but I haven't 
tested it explicitly.

It uses `uv` for dependency management. Official installation instructions [here](https://docs.astral.sh/uv/getting-started/installation/).

To install all requirements:

```shell
cd ~/path/to/lunch-voting

uv sync
```

With all dependencies installed, you first need to run a small script to set up the local database. 
You'll need to set `PYTHONPATH` manually for this:

```shell
PYTHONPATH=./src uv run poe init_db
```

You can then run the FastAPI development server with:

```shell
uv run poe serve
```


## Running the docker container

Everything should work out of the box with the provided docker setup with just `docker compose 
up --build` from the repository root.

The server running within the docker container can be reached locally at `http://localhost:8000`. You 
can test that it's up and running by opening the documentation page at `http://localhost:8000/docs`.


## Running the tests

You can validate that all tests are passing by running `pytest` from within the `lunch-voting` 
directory:

```
pytest
```

## API documentation

You can find the documentation for all the endpoints on `http://localhost:8000/docs`.
