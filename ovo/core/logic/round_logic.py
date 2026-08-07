from ovo import db, get_username
from ovo.core.database.models import Project, Round

ARCHIVED_ROUND_NAME = "Archived"


def get_or_create_project_rounds(project_id: str) -> dict[str, Round]:
    project_rounds = db.select(Round, project_id=project_id, order_by="created_date_utc")
    if not project_rounds:
        project_round = Round(project_id=project_id, name="Round 1", author=get_username())
        db.save(project_round)
        project_rounds = [project_round]
    return {r.id: r for r in project_rounds}


def get_or_create_archived_round(project_id: str) -> Round:
    """Get the project's "Archived" round, creating it if it doesn't exist.

    The archived round is created with the same created date as the project so that it
    sorts before all other rounds.
    """
    existing = db.select(Round, project_id=project_id, name=ARCHIVED_ROUND_NAME, limit=1)
    if existing:
        return existing[0]

    project = db.get(Project, id=project_id)
    archived_round = Round(
        project_id=project_id,
        name=ARCHIVED_ROUND_NAME,
        author=get_username(),
        created_date_utc=project.created_date_utc,
    )
    db.save(archived_round)
    return archived_round
