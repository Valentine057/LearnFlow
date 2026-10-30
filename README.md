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

Open `http://127.0.0.1:8000/` for the site. Create a Django administrator with `python manage.py createsuperuser`, then sign in at `/admin/`. To assign the separate School Owner role, open School Owner Profiles and create a profile for the trusted user's account. A School Owner can manage course books from the website's Library without needing Django admin access. Django staff and the course's instructor can also manage books; students can download books for courses they have paid enrollment in.

The public `/courses/library/` page lists books for published courses. Owners and instructors can add, edit, and delete books there; instructor access is limited to books attached to their own courses. Use the book's course detail or learning page to reach that course's books. PDF and EPUB uploads are supported.

On Windows, use the standard Python installer from python.org. The MSYS2 Python build creates a `.venv/bin` layout and may not work with PowerShell's `.venv\Scripts\Activate.ps1` command.

## API

- `POST /api/token/` and `POST /api/token/refresh/` for JWT authentication
- `GET /api/courses/` for published courses
- `GET /api/courses/{id}/lessons/` for enrolled lesson access
- `POST /api/enrollments/` to simulate a purchase
- `GET /api/my-courses/` for the current student's courses
