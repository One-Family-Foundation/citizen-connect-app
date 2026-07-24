import frappe
from frappe.utils.logger import get_logger

logger = get_logger("citizen_connect")


class ErrorLogger:

    @staticmethod
    def log(error: Exception):
        frappe.log_error(
            title=str(error),
            message=frappe.get_traceback()
        )

        logger.error(
            message=frappe.get_traceback(),
            stacktrace=frappe.get_traceback()
        )