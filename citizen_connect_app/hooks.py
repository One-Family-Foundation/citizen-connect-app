# from apps.citizen_connect_app.citizen_connect_app.services.permission_manager import (ngo_profile_query , case_query)


app_name = "citizen_connect_app"
app_title = "Citizen Connect App"
app_publisher = "One Family Foundation"
app_description = "Citizen Connect App"
app_email = "tech@impactyaan.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "citizen_connect_app",
# 		"logo": "/assets/citizen_connect_app/logo.png",
# 		"title": "Citizen Connect App",
# 		"route": "/citizen_connect_app",
# 		"has_permission": "citizen_connect_app.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/citizen_connect_app/css/citizen_connect_app.css"
# app_include_js = "/assets/citizen_connect_app/js/citizen_connect_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/citizen_connect_app/css/citizen_connect_app.css"
# web_include_js = "/assets/citizen_connect_app/js/citizen_connect_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "citizen_connect_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "citizen_connect_app/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "citizen_connect_app.utils.jinja_methods",
# 	"filters": "citizen_connect_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "citizen_connect_app.install.before_install"
# after_install = "citizen_connect_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "citizen_connect_app.uninstall.before_uninstall"
# after_uninstall = "citizen_connect_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "citizen_connect_app.utils.before_app_install"
# after_app_install = "citizen_connect_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "citizen_connect_app.utils.before_app_uninstall"
# after_app_uninstall = "citizen_connect_app.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "citizen_connect_app.build.after_build"
after_install = "citizen_connect_app.utils.translations.install_custom_fields"
after_migrate = "citizen_connect_app.utils.translations.install_custom_fields"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "citizen_connect_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }
permission_query_conditions = {
    "Case": "citizen_connect_app.services.permission_manager.case_query",
    "Organisation" :"citizen_connect_app.services.permission_manager.ngo_profile_query",
    "Opportunity Form" : "citizen_connect_app.services.permission_manager.opportunity_form_query",
    "Scheme" : "citizen_connect_app.services.permission_manager.scheme_list_query",
    "Service" : "citizen_connect_app.services.permission_manager.service_list_query"
    
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"citizen_connect_app.tasks.all"
# 	],
# 	"daily": [
# 		"citizen_connect_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"citizen_connect_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"citizen_connect_app.tasks.weekly"
# 	],
# 	"monthly": [
# 		"citizen_connect_app.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "citizen_connect_app.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "citizen_connect_app.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "citizen_connect_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "citizen_connect_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["citizen_connect_app.utils.before_request"]
# after_request = ["citizen_connect_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["citizen_connect_app.utils.before_job"]
# after_job = ["citizen_connect_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"citizen_connect_app.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

doc_events = {
    " Category": {
        "on_update": "citizen_connect_app.services.service.clear_categories_cache",
        "after_insert": "citizen_connect_app.services.service.clear_categories_cache",
        "on_trash": "citizen_connect_app.services.service.clear_categories_cache",
    },
    "Country": {
        "on_update": "citizen_connect_app.services.location.clear_locations_cache",
        "after_insert": "citizen_connect_app.services.location.clear_locations_cache",
        "on_trash": "citizen_connect_app.services.location.clear_locations_cache",
    },
    "Geography L1": {
        "on_update": "citizen_connect_app.services.location.clear_locations_cache",
        "after_insert": "citizen_connect_app.services.location.clear_locations_cache",
        "on_trash": "citizen_connect_app.services.location.clear_locations_cache",
    },
    "Geography L2": {
        "on_update": "citizen_connect_app.services.location.clear_locations_cache",
        "after_insert": "citizen_connect_app.services.location.clear_locations_cache",
        "on_trash": "citizen_connect_app.services.location.clear_locations_cache",
    },
    "Volunteer Action": {
        "on_trash": "citizen_connect_app.services.volunteer_action_manager.on_trash",
    },
    "Case":{
        "on_trash": "citizen_connect_app.services.community_check_manager.on_trash",
        "on_trash": "citizen_connect_app.services.issue_manager.on_trash",
    },
}