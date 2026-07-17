import frappe
from frappe.utils.logger import get_logger

logger = get_logger("citizen_connect")


class ErrorLogger:

    @staticmethod
    def log(message: str, details: str, stacktrace: str):
        frappe.log_error(
            title=message,
            traceback=stacktrace
        )

        logger.error(
            "%s\nDetails: %s\nStacktrace:\n%s",
            message,
            details,
            stacktrace
        )