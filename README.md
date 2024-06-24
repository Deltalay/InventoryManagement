# Inventory Management System

## Setup

Create a virtual enviroment

```shell
python -m venv .venv
```

Activate the virtual enviroment
For Windows(Powershell):

```shell
./.venv/Scripts/Activate.ps1
```

For Windows(CMD):

```shell
cd .venv/Scripts
activate
```

For Linux:

```bash
source .venv/bin/activate
```

After create the virtual environemt and activate it we can install the neccessary dependecies in requirement.txt

```bash
pip install -r requirements.txt
```

After that change `.env.example` to `.env` and place your database connection insde and put random string in `SECRET`. After you have finish it you can change the assets directory in the `main.py` file and don't forget to run the `database.sql`. Please note that in order to create admin account you have to insert your own account. We use bcrypt hash as our password hasher.
