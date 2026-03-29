from sqlalchemy.exc import NoResultFound

from ovo import db, get_username
from ovo.core.database.models import UserSettings


def get_or_create_user_settings(username: str = None) -> UserSettings:
    if username is None:
        username = get_username()

    try:
        user_settings = db.get(UserSettings, username=username)
    except NoResultFound:
        user_settings = UserSettings(username=username)
        db.save(user_settings)
    return user_settings


def set_user_setting(key: str, value, username: str = None):
    """Set a user setting property to given value"""
    user_settings = get_or_create_user_settings(username)
    user_settings.props = user_settings.props.copy() if user_settings.props else {}
    user_settings.props[key] = value
    db.UserSettings.save_value("props", user_settings.props, username=user_settings.username)
