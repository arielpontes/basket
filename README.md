# Basketball API

## Spinning up the app

In order to spin up the API, just run:

    docker compose up -d

You should be able to access the API at localhost:8000.

## API Authentication

You can log into the Django admin as a superuser using the following credentials:

    user: root
    pass: root

In order to use the API, you just have to create a Token for your user and then use it when making requests. You can create a Token [here](http://localhost:8000/admin/authtoken/tokenproxy/add/).

## Admin actions

As an admin user, you can perform the following actions in the Django admin interface:

- Assign games to normal users (game change page)
- Unassign games from normal users (game change page)
- Edit/remove games (game change page)
- Add/remove countries from a normal user’s permissions (user change page)

## Endpoint actions

### GET /games/

As an admin user, you should be able to see all games in this endpoint. If you don't see anything, make sure to use `?refresh=True`. This will fetch data from RapidAPI and populate the local database.

As a normal user, you should be able to see all games that are associated to a country that is assigned to you and that are not assigned to any other user.

### GET /games/<pk>/

As an admin user, you should be able to see the details of any game.

As a normal user, you should only be able to see the details of games that are associated to your countries and not assigned to any other user. Otherwise, you get a 404.

### GET /games/assigned/

This endpoint returns all games that are assigned to you. Only games that are associated to one of your countries can be assigned to you.

### GET /games/unassigned/

This endpoint returns all games that associated to one of your countries but not assigned to anybody.

### PATCH /games/<pk>/assign/

This endpoint assigns a specific game to your user, if it is assignable (associated to one of your countries and not assigned to anybody else).