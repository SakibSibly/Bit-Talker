from plyer import notification


def create_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_icon="../pictures/main_icon.ico",
        timeout=2
    )
