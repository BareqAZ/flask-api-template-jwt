# Flask API Template JWT

Welcome to the Flask API Template, a versatile foundation for rapidly developing API backends.
Managing and accessing projects remotely through APIs has become a common need in software development. However, crafting APIs from scratch for every project can be time-consuming. To address this issue, I have created this Flask API template, enabling you to expedite development and deployment for any project.

## Features

- **Role-Based Access Control:** Simplify access control by supporting user and admin roles. Leverage decorators to manage who can access specific endpoints easily.

- **User Management:** Easily add, remove, and manage API users with built-in functionality.

- **Log Management:** Basic logging is already integrated, with syslog handling.

- **Gunicorn:** Enjoy the benefits of a production-ready server with Gunicorn, ensuring reliability and performance.

- **Encryption:** Hashed API keys Even in the event of a database breach, the keys are hashed, significantly increasing their resistance to unauthorized access.

- **JWT:** Support for JSON Web Tokens (JWT), along with pre-existing routes for authentication, token refreshing, and logging out.

## Demo

1. Configure the settings by copying the default settings from `./src/settings.toml.default` to `./src/settings.toml`. Customize the new settings file as needed.

2. Set up a Python virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements_dev.txt
   ```
3. Start the debug server:
`./run_debug_server.sh`

4. Explore the available routes at 'src/app/v1/' and use the superuser credentials from the settings TOML file to test the API.

## Development Workflow

1. Run the debug server:
`./run_debug_server.sh`

2. Make code changes and test them in real-time.

3. When you've made your changes, run tests using `pytest ./tests`, and add new tests as needed.

4. Run linters for code quality checks:
`./run_linters.sh`

5. Done!

## Project Structure
```
src
├── app
│   ├── __init__.py    # Flask configuration
│   │
│   ├── v1             # Contains all the API V1 routes
│   │
│   ├── libs           # Houses helper libraries, tools, and functions
│   │
│   └── models.py      # SQLite database models
│
├── settings.toml      # Holds all configurable settings and credentials
│
└── bin                # holds executables for starting both the debug and production servers
```

