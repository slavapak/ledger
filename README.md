# Tiny Token

This repository is a solution to the following problem:

## Requirements:

1. Create a simple server application using TypeScript, Rust, or Python (you're welcome to choose any language from these three based on their comfort level). You can use any libraries or frameworks that you deem suitable.
2. The server application should use a simple data store (preferably MongoDB or Postgres) to maintain the list of users and data on their respective tokens. 
3. Implement the following API endpoints:
   - `POST /users`: Create a new user with an initial balance of tokens.
   - `GET /users/{id}`: Retrieve details of a user.
   - `POST /transactions`: Perform a transaction between two users. The body of the request should include the ID of the sender, the ID of the receiver, the amount of tokens to be transferred and any other pertinent details.
4. Each API request should perform necessary validation. For example, a transaction should not be allowed if the sender does not have sufficient tokens.
5. Write tests to verify the correctness of your server application.
6. Document your design choices, how to run your application, and how to run the tests.
7. Use Docker to containerize your application.
8. Add a simple front-end using React or NextJS to visualize the users and transactions.

## How to Run:

First clone this repo.

### Run Demo Using Docker:

1. In terminal cd to repo root if not there

2. In terminal
```sh
$ docker compose --profile prod up -d
```
3. In browser navigate to [http://localhost]()

Backend unit tests run during the build

### Run Integration Tests Using Docker:

1. In terminal cd to repo root if not there
2. In terminal
```sh
$ docker compose --profile tests up --abort-on-container-exit test_quart && docker compose stop test_postgres
```

### Run Backend Locally:

In terminal cd to repo root if not there

#### Set Up venv:
1. In terminal
```sh
$ python3 -m venv .venv
$ . .venv/bin/activate
$ pip install -r quart/requirements.txt
```

After that you can run app and tests locally.

#### Integration Tests:
1. In terminal cd to repo root if not there
2. In terminal
```sh
$ docker compose up -d test_postgres && pytest --envfile=integration.env quart/integration && docker compose stop test_postgres
```

#### App
1. In terminal cd to repo root if not there
2. In terminal:
```sh
$ docker compose up -d ledger_postgres
$ uvicorn --app-dir quart/src/ --env-file .env ledger.app:app --port 4001
```

To test it, in terminal
```sh
$ curl http://localhost:4001/users/1
```

#### Unit Tests:
1. In terminal cd to repo root if not there
2. In terminal
```sh
$ pytest quart/test
```

### To run API frontend locally:
1. In terminal cd to repo root if not there
2. In terminal
```sh
$ docker compose up -d ledger_quart
$ cd nextjs
$ npm install nextjs
$ echo "NEXT_PUBLIC_API_URL=http://localhost:4000" > .env.local
$ echo "NEXT_PUBLIC_DEFAULT_BALANCE=100" >> .env.local
$ npm run dev
```
3. In browser navigate to [http://localhost:3000]()