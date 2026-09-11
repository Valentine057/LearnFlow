# LearnFlow

LearnFlow is a Django course platform for practical, locally relevant education across Africa.

## Quick start

```powershell
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations accounts courses enrollments
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the site and `/admin/` to add categories, instructors, courses, lessons, and coupons.

On Windows, use the standard Python installer from python.org. The MSYS2 Python build creates a `.venv/bin` layout and may not work with PowerShell's `.venv\Scripts\Activate.ps1` command.

## API

- `POST /api/token/` and `POST /api/token/refresh/` for JWT authentication
- `GET /api/courses/` for published courses
- `GET /api/courses/{id}/lessons/` for enrolled lesson access
- `POST /api/enrollments/` to simulate a purchase
- `GET /api/my-courses/` for the current student's courses
