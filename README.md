# netizen
FastAPI app that aims to recreate the backend for a simple social-network website. Uses SQLModel and SQLAlchemy for database access. Containerized with Docker and secured with JWT.

## Tech stack
* FastAPI `0.78.0`
* SQLModel `0.0.6`
* SQLAlchemy `1.4.35`
* Alembic `1.7.7`
* PostgreSQL `14.2`
* Docker

## Functionality
SwaggerUI docs available at `localhost:8000/api/v1/docs`
### Users:
* Implemented authentication using JWT.
* Users can register, login, view their profile.
* After registration, an email is sent to the user with account activation link.
### Friends:
* Users can send friend requests to each user, if they're not already friends.
* Friend requests can be cancelled by sender and responded to by receiver.
### Groups:
* Users can create new groups and request membership to existing ones.
* Closed groups are 'hidden' so that their members and posts are not visible to non-members.
* Private groups allow viewing members but not posts.
* Public groups allow viewing both members and posts.
### Posts:
* Post can be created either as a UserPost or GroupPost. User posts are visible by anyone, while group posts access is restricted as stated above.
* Posts can be reacted to (liked or disliked) or commented by user.

## Setup
1. Clone repository:
`$ git clone https://github.com/amadeuszklimaszewski/fastapi-async-template`
2. Run in root directory:
`$ make build-dev`
3. Provide `AUTHJWT_SECRET_KEY` in .env file
4. Run template: `$ make up-dev`


## Migrations
Register new models in `./src/settings/alembic.py` by importing your `models.py` file.  
Run `$ make migrations` to migrate.


## Tests
`$ make test`


## Makefile
`Makefile` contains useful command aliases


## TODOs
* User invites to groups.
* Messaging system.
