## api and websoket tests for custom api
api specifications in `server/openapi3.yaml` <br>

## requirements
* `docker` <br>
* `.env` file in project root directory with mongo connection string: <br>
```dotenv
MONGO_CONNECTION_STRING=mongodb+srv://user:password@your.db.mongodb.net
```

## how to run server + tests:
`docker compose up`

## where reports?
in `tests/reports` folder

## Run example:
![Image](https://github.com/user-attachments/assets/677a84d8-6fc3-4a7d-a5ef-d57aa189a3fa)

## Improve points
* allure reporting
* local mongo container