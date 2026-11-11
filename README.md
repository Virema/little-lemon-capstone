# Little Lemon Restaurant – Django REST API Capstone Project

Little Lemon serves a restaurant homepage, a menu API, a table booking API,
and account registration and token authentication.

See [Readme.txt](Readme.txt) for installation, MySQL grants, API examples,
tests, and instructions for importing the [request collection](insomnia/LittleLemon.postman_collection.json) into Insomnia.

| URL | Access |
| --- | --- |
| `/` | Public homepage |
| `/restaurant/menu/` | Public reads, staff writes |
| `/restaurant/booking/tables/` | Authenticated users |
| `/auth/users/` and `/auth/token/login/` | Public registration and login |
| `/auth/users/me/` and `/auth/token/logout/` | Authenticated users |
