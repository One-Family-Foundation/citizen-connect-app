import logging
import frappe

logger = logging.getLogger(__name__)


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