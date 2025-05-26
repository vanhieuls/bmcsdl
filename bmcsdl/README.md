### How to run
1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Remove all content from the 'migrations' folder if the database hasn't been created yet. This is to ensure that the migrations are created from scratch.
   - Navigate to the `migrations` folder in your Django app directory and delete all files except for `__init__.py`.
   - If you have an existing database, you can skip this step.
3. Check the `settings.py` file to ensure the database connection settings are correct.
   - If you are using SQLite, ensure that the database file is created in the same directory as your Django project.
   - If you are using PostgreSQL or another database, ensure that the database is created and the connection settings in `settings.py` are correct.
4. Run the following command to create migrations for the models defined in your Django application:
   ```bash
   python manage.py makemigrations
   ```
5. Apply the migrations to the database:
   ```bash
    python manage.py migrate
    ```
6. Create a superuser account to access the Django admin interface:
   ```bash
   python manage.py createsuperuser
   ```
7. Start the Django development server:
   ```bash
    python manage.py runserver localhost:8000
    ```
8. Open your web browser and navigate to `http://localhost:8000/admin` to access the Django admin interface.
9. Log in using the superuser account you created in step 6.
10. You can now manage your models through the Django admin interface.