import frappe
from citizen_connect_app.services.service import ServiceManager
from citizen_connect_app.services.location import LocationManager


def clear_service_categories_cache(doc, method):
    """Clear service categories cache."""
    frappe.cache().delete_value(ServiceManager.CATEGORIES_CACHE_KEY)


def clear_locations_cache(doc, method):
    """Clear locations cache."""
    frappe.cache().delete_value(LocationManager.CACHE_KEY)