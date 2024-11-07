from fastapi import BackgroundTasks

def send_notification(email: str, message: str):
    # Logic to send an email notification (could be an external service)
    print(f"Sending notification to {email}: {message}")

def notify_user_on_event(user_email: str, event_type: str, background_tasks: BackgroundTasks):
    message = f"You have a new {event_type}!"
    background_tasks.add_task(send_notification, user_email, message)
