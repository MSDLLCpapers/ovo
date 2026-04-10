import warnings

from sqlalchemy.exc import NoResultFound

from ovo import db, get_username, config
from ovo.core.database.models import UserSettings


def get_or_create_user_settings(username: str = None) -> UserSettings:
    if username is None:
        username = get_username()

    try:
        user_settings = db.get(UserSettings, username=username)
    except NoResultFound:
        user_settings = UserSettings(username=username)
        if not config.props.read_only:
            db.save(user_settings)
    return user_settings


def set_user_setting(key: str, value, username: str = None):
    """Set a user setting property to given value"""
    if config.props.read_only:
        warnings.warn(f"Not setting user setting {key} to {value} because app is in read-only mode.")
        return
    user_settings = get_or_create_user_settings(username)
    user_settings.props = user_settings.props.copy() if user_settings.props else {}
    user_settings.props[key] = value
    db.UserSettings.save_value("props", user_settings.props, username=user_settings.username)


def update_last_project_id(last_project_id: str):
    user_settings = get_or_create_user_settings()
    recent_project_ids = user_settings.props.get("ovo.recent_project_ids", []).copy()
    if last_project_id in recent_project_ids:
        recent_project_ids.remove(last_project_id)
    recent_project_ids = [last_project_id] + recent_project_ids
    set_user_setting("ovo.last_project_id", last_project_id)
    set_user_setting("ovo.recent_project_ids", recent_project_ids[:10])
