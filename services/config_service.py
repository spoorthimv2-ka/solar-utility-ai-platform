from database import get_config, set_config, get_all_config


def is_enabled(config_key, default=True):
    """
    Return True/False for a boolean configuration.
    """

    value = get_config(
        config_key,
        "true" if default else "false"
    )

    return str(value).lower() == "true"


def get_alert_threshold():
    """
    Return the configured utility alert threshold.
    """

    value = get_config("alert_threshold", "80")

    try:
        return float(value)
    except (TypeError, ValueError):
        return 80.0


def get_app_config():
    """
    Return all application configuration values.
    """

    return {
        "ai_enabled": is_enabled("ai_enabled"),
        "daily_reports_enabled": is_enabled(
            "daily_reports_enabled"
        ),
        "monthly_reports_enabled": is_enabled(
            "monthly_reports_enabled"
        ),
        "data_upload_enabled": is_enabled(
            "data_upload_enabled"
        ),
        "user_registration_enabled": is_enabled(
            "user_registration_enabled"
        ),
        "alert_threshold": get_alert_threshold(),
    }


def update_config(config_key, config_value):
    """
    Update an existing configuration setting.
    """

    set_config(
        config_key,
        config_value,
        "Updated from Admin Configuration"
    )


def get_all_settings():
    """
    Return all settings stored in PostgreSQL.
    """

    return get_all_config()