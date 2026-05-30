from apscheduler.schedulers.background import BackgroundScheduler
from app.services.smart_reminder_service import generate_smart_nudges_for_all_users


scheduler = BackgroundScheduler()


def run_smart_reminders(app):
    with app.app_context():
        try:
            total_generated = generate_smart_nudges_for_all_users()
            app.logger.info(
                f"Smart reminder job completed. Generated {total_generated} notification(s)."
            )
        except Exception as e:
            app.logger.error(
                f"Smart reminder job failed: {str(e)}"
            )


def start_scheduler(app):
    if scheduler.running:
        return

    scheduler.add_job(
        func=lambda: run_smart_reminders(app),
        trigger="interval",
        minutes=1,
        id="smart_reminder_job",
        replace_existing=True
    )

    scheduler.start()
    app.logger.info("APScheduler started for smart reminders.")
