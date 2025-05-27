# Shavon
Savon is a starting point for asynchronous web development. It builds upon the
Sanic framework and provides a few blueprints common to most web applications,
such as onboarding, authentication, and profile management.

## Setup and Launch

It is recommended that you use Python 3.12 or above.

In a terminal, switch to your project directory (where you cloned the
repository to) and run the following commands based on your system.

### Linux
```sh
$ python3 -m venv .venv
$ source .venv/bin/activate
```

### Windows
```
> python3 -m venv .venv
> .\.venv\Scripts\activate
```

### Launching
Launching is done the same across all systems using the 
`python -m shavon.launch` command. Without any changes, this will launch a
bare-bones sanic server on https://localhost:8000

### Notes:
- In its current state, the default settings used in `shavon.settings` are
sufficient to run the site. Shavon is not currently connecting to a database, 
nor is it creating a cookie.

## Project Structure

- **`shavon/models`** is a directory where datamodels are stored. These models
are built using SQLAlchemy's ORM features. It is important to point out that
because this is an asyncronous environment, true ORM is impossible. Because of
this we must ensure that the data is freshly pulled from database just before 
making changes. For example if we are to edit a user:

    ```py
    async with db.session() as session:
        # Obtain a refreshed User model
        user = await User.refresh(session, user_id=request.ctx.user.id)
        user.set_password(form.new_password)

        # Persist the user data
        session.add(user)
        await session.flush()
        await session.commit()
    ```
- **`shavon/utilities`** contain helper classes and functions used throughout.
- **`shavon/templates`** contains all the jinja2 based html files.
- **`shavon/validators`** contains all the Pydantic data models (validators).
- **`shavon/blueprints`** contains all the system endpoints