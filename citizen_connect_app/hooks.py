doc_events = {
    "Service Category": {
        "on_update": "citizen_connect_app.utils.cache.clear_service_categories_cache",
        "after_insert": "citizen_connect_app.utils.cache.clear_service_categories_cache",
        "on_trash": "citizen_connect_app.utils.cache.clear_service_categories_cache",
    },
    "Country": {
        "on_update": "citizen_connect_app.utils.cache.clear_locations_cache",
        "after_insert": "citizen_connect_app.utils.cache.clear_locations_cache",
        "on_trash": "citizen_connect_app.utils.cache.clear_locations_cache",
    },
    "Geography L1": {
        "on_update": "citizen_connect_app.utils.cache.clear_locations_cache",
        "after_insert": "citizen_connect_app.utils.cache.clear_locations_cache",
        "on_trash": "citizen_connect_app.utils.cache.clear_locations_cache",
    },
    "Geography L2": {
        "on_update": "citizen_connect_app.utils.cache.clear_locations_cache",
        "after_insert": "citizen_connect_app.utils.cache.clear_locations_cache",
        "on_trash": "citizen_connect_app.utils.cache.clear_locations_cache",
    },
}