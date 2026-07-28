import frappe
from frappe.utils import logger

logger.set_log_level("DEBUG")
logger = frappe.logger("citizen_connect_app", allow_site=True, file_count=50)


class ErrorLogger:

    @staticmethod
    def log(error: Exception):
        frappe.log_error(
            title=str(error),
            message=frappe.get_traceback()
        )

        logger.error(
            frappe.get_traceback()
            
        )