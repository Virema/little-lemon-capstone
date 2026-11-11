Little Lemon Restaurant – Django REST API Capstone Project

OVERVIEW
Django serves the restaurant homepage and its CSS. Django REST Framework
provides menu and booking APIs. Djoser registers users and issues DRF tokens.
The API uses MySQL by default. Menu reads are public. Staff users manage the
menu. Any authenticated user can manage bookings in this course demo.
Use synthetic booking names when testing.

INSTALLATION
Open a terminal in the project directory. Use Python 3.10–3.14 and MySQL 8.4.

Windows PowerShell:
  python -m venv .venv
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  Copy-Item .env.example .env

macOS / Linux:
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install -r requirements.txt
  cp .env.example .env

In commands below, use the virtual environment's Python. On Windows,
replace python with .\.venv\Scripts\python.exe if it is not activated.

MYSQL
On Windows, open PowerShell as Administrator and run
  winget search MySQL
  winget install --id Oracle.MySQL --exact
Complete the MySQL installation and server configuration, and start the
server. If the package is unavailable, use the MySQL Community Server
installer at https://dev.mysql.com/downloads/mysql/ and add its bin folder
to PATH or use the full path to mysql.exe.

Connect as the MySQL administrator using mysql -u root -p and run the
following statements. Substitute a strong local password for the example
password before executing the CREATE USER statement.

  CREATE DATABASE littlelemon CHARACTER SET utf8mb4;
  CREATE USER 'littlelemon'@'127.0.0.1' IDENTIFIED BY 'REPLACE_WITH_LOCAL_PASSWORD';
  GRANT ALL PRIVILEGES ON littlelemon.* TO 'littlelemon'@'127.0.0.1';
  GRANT ALL PRIVILEGES ON test_littlelemon.* TO 'littlelemon'@'127.0.0.1';

Set DB_PASSWORD in .env to the password you chose. Set DJANGO_SECRET_KEY
to a private value (generate with the following command and paste into .env).
Keep .env and passwords out of Git.

  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  python manage.py check
  python manage.py migrate
  python manage.py shell -c "from django.db import connection; c = connection.cursor(); c.execute('SELECT DATABASE(), VERSION()'); print(c.fetchone())"
  python manage.py createsuperuser
  python manage.py test
  python manage.py runserver

The test suite creates and drops test_littlelemon. The application database
is littlelemon. For an optional local smoke test without MySQL, set
DB_ENGINE=sqlite in .env and run migrations. Switch DB_ENGINE back to mysql
for MySQL verification.

Open http://127.0.0.1:8000/ for the homepage and
http://127.0.0.1:8000/static/restaurant/site.css for CSS.

AUTHENTICATION
Base URL: http://127.0.0.1:8000
Send Content-Type: application/json for requests with JSON bodies.
POST /auth/users/ returns 201 and creates a regular account.
  {"username":"reviewer","email":"reviewer@example.com","password":"YOUR_CHOSEN_STRONG_PASSWORD"}
Example response:
  {"email":"reviewer@example.com","username":"reviewer","id":2}

POST /auth/token/login/ returns 200 with an authentication token.
  {"username":"reviewer","password":"YOUR_CHOSEN_STRONG_PASSWORD"}
Example response:
  {"auth_token":"YOUR_TOKEN"}

Send Authorization: Token YOUR_TOKEN for authenticated requests.
GET /auth/users/me/ returns 200 with the current user.
POST /auth/token/logout/ returns 204 and revokes the token.

MENU
GET, POST                 /restaurant/menu/
GET, PUT, PATCH, DELETE   /restaurant/menu/{id}/

Log in using the username/password from createsuperuser for menu writes.
Example HTTP request:
  POST /restaurant/menu/
  Content-Type: application/json
  Authorization: Token YOUR_STAFF_TOKEN

  {"title":"Greek salad","price":"12.50","inventory":20}
Example 201 response:
  {"id":1,"title":"Greek salad","price":"12.50","inventory":20}

BOOKINGS
GET, POST                 /restaurant/booking/tables/
GET, PUT, PATCH, DELETE   /restaurant/booking/tables/{id}/

Example HTTP request:
  POST /restaurant/booking/tables/
  Content-Type: application/json
  Authorization: Token YOUR_TOKEN

  {"name":"Taylor","no_of_guests":4,"booking_date":"2027-05-10T18:30:00Z"}
Example 201 response:
  {"id":1,"name":"Taylor","no_of_guests":4,"booking_date":"2027-05-10T18:30:00Z"}

GET returns 200 with an array for a list or an object for a detail.
PUT replaces all writable fields. PATCH changes supplied fields.
Both return 200. DELETE returns 204. Invalid payloads return 400.
Missing or invalid tokens on protected endpoints return 401.
Regular users attempting menu writes receive 403.
Missing records return 404 for callers authorized for the operation.

INSOMNIA
Import insomnia/LittleLemon.postman_collection.json using Import > File.
Set the base_url, username and password in the imported environment or
replace the corresponding request variables. For staff, also set
staff_username and staff_password. Keep credentials and tokens local.
Register, log in, and copy the auth_token value into user_token.
For menu writes, log in as staff and put that token into staff_token.
Create an item or booking and set menu_id or booking_id to the returned
id before trying the detail, update or delete requests.
Log out and repeat a protected request to confirm that it returns 401.
