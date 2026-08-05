import frappe

logger = frappe.logger(
    "citizen_connect_app",
    allow_site=True,
    file_count=50
)

logger.setLevel("DEBUG")


class ErrorLogger:

    @staticmethod
    def log(error: Exception):
        frappe.db.rollback()
        traceback = frappe.get_traceback()
        frappe.log_error(title=str(error)[:140], message=traceback)
        frappe.db.commit()
        logger.error(traceback)
