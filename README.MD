# Library API #
A simple CRUD API written using Python + Flask + SQLAlchemy<br>

## Endpoints ##
- Authors API<br>
  GET /api/v1/authors<br>
  GET /api/v1/authors/{id}<br>
  POST /api/v1/authors<br>
  PUT /api/v1/authors/{id}<br>
  DELETE /api/v1/authors/{id}<br>
  GET /api/v1/authors/{id}/books<br>
- Books API<br>
  GET /api/v1/books<br>
  GET /api/v1/books/{id}<br>
  POST /api/v1/books<br>
  PUT /api/v1/books/{id}<br>
  DELETE /api/v1/books<br>
- Miscellaneous API<br>
  GET /ping<br>

## Setup ##
- Create virtual environment<br>
  `python3 -m virtualenv venv <envname>`<br>
- Change directory to virtual environment created above<br>
  `cd <envname>`<br>
- Install dependency<br>
  `pip install -r requirements`<br>
- Copy application configuration from template<br>
  `make copy config`<br>
- Edit `config.yml` and adjust the configuration if necessary<br>
- Initialize database<br>
  `flask db init`<br>
  `flask db migrate`<br>
  `flask db upgrade`<br>

## Starting Server ##
`make start`<br>

## Running Unit Test ##
`make test`<br>
