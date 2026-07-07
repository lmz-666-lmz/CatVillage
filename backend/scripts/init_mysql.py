from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database.bootstrap import ensure_schema, seed_admin_user
from app.database.session import SessionLocal


def main() -> None:
    ensure_schema()
    db = SessionLocal()
    try:
        created_or_updated = seed_admin_user(db)
    finally:
        db.close()

    if created_or_updated:
        print("MySQL tables are ready and admin user is enabled.")
    else:
        print("MySQL tables are ready. Admin user was not created because ADMIN_USERNAME/ADMIN_PASSWORD is not configured.")


if __name__ == "__main__":
    main()
