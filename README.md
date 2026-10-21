# ZeroDayZ
This is the source code for the *Centralized Hostel Complaint Management and Maintenance System*.

## Login database

Login reads student roll numbers and staff IDs from MySQL. Create a `users` table
with `id`, `role`, `identifier`, and `password_hash` columns. `role` must be
`student` or `staff`, and `password_hash` must contain a Werkzeug password hash.

Set `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`,
and `SECRET_KEY` before starting the Flask app. There are no database or session
credential defaults in the source code. The login query uses parameters and does
not store or log submitted passwords.

Admin login uses two additional Vercel variables:
`ADMIN_USERNAME` and `ADMIN_PASSWORD`. Admin credentials are not stored in MySQL
and do not use Firebase email verification.

Student and staff account creation uses Firebase Email/Password Authentication. In
Firebase Console, enable Authentication > Sign-in method > Email/Password and add
the local development domain and production domain under Authentication settings.

Set these Firebase web configuration variables:
`FIREBASE_API_KEY`, `FIREBASE_AUTH_DOMAIN`, `FIREBASE_PROJECT_ID`,
`FIREBASE_STORAGE_BUCKET`, `FIREBASE_MESSAGING_SENDER_ID`, and `FIREBASE_APP_ID`.
Set `FIREBASE_SERVICE_ACCOUNT_JSON` to the complete service-account JSON contents
as a single Vercel environment variable. Never commit that JSON file.

In Firebase Authentication > Settings > Authorized domains, add the exact Vercel
production hostname, such as `your-project.vercel.app`, and your custom `.app` or
`.com` domain. Add `localhost` only for local development.

Firebase creates the email/password account and sends the verification email in the
browser. Flask verifies the resulting ID token and its `email_verified` claim with
Firebase Admin before creating the MySQL account.

After an existing `users` table has been created, add the staff profile fields with
this non-destructive migration:

```bash
.venv/bin/python update_database.py
```

Run the database setup with the project's virtual environment:

```bash
.venv/bin/python create_tables.py
```

Inspect the existing tables and column structure without reading application data:

```bash
.venv/bin/python inspect_database.py
```


## 🔀 Branch Structure:

* **main** -> Contains production ready code.

* **develop** -> This is the integration branch for all other branches.

* **feature/X** -> In this branch a feature X may be bulit.

* **fix/X3** -> In this a bug X3 may be fixed.

----

### 📝 LICENSE:

Check [LICENSE.md](./LICENSE) for more details.

----

<p align = "center"> Made with 🩵 </p>