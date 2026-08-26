from fastapi import APIRouter
import os

router = APIRouter()


@router.get("/status")
def get_status():
    """Return health and basic metadata for the UI status panel."""
    try:
        db_path = os.path.join(os.path.dirname(__file__), "vector_db")
        documents = 0
        last_update = "N/A"

        if os.path.isdir(db_path):
            files = [f for f in os.listdir(db_path) if os.path.isfile(os.path.join(db_path, f))]
            documents = len(files)
            mtimes = [os.path.getmtime(os.path.join(db_path, f)) for f in files]
            if mtimes:
                import datetime
                last_update = datetime.datetime.fromtimestamp(
                    max(mtimes), tz=datetime.timezone.utc
                ).strftime("%Y-%m-%d")
    except Exception:
        documents = 0
        last_update = "N/A"

    return {
        "ready": True,
        "documents": documents,
        "last_update": last_update
    }
