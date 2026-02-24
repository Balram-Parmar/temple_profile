app_name = "temple_profile"
app_title = "Temple Profile"
app_publisher = "balram"
app_description = "this will make connections between new profiles"
app_email = "thcoc460@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "temple_profile",
# 		"logo": "/assets/temple_profile/logo.png",
# 		"title": "Temple Profile",
# 		"route": "/temple_profile",
# 		"has_permission": "temple_profile.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/temple_profile/css/temple_profile.css"
app_include_js = [
    "https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js"
]
# include js, css files in header of web template
# web_include_css = "/assets/temple_profile/css/temple_profile.css"
# web_include_js = "/assets/temple_profile/js/temple_profile.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "temple_profile/public/scss/website"

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
# app_include_icons = "temple_profile/public/icons.svg"

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
# 	"methods": "temple_profile.utils.jinja_methods",
# 	"filters": "temple_profile.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "temple_profile.install.before_install"
# after_install = "temple_profile.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "temple_profile.uninstall.before_uninstall"
# after_uninstall = "temple_profile.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "temple_profile.utils.before_app_install"
# after_app_install = "temple_profile.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "temple_profile.utils.before_app_uninstall"
# after_app_uninstall = "temple_profile.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "temple_profile.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

# In your app's hooks.py

doc_events = {
    "*": {
        "before_insert": "temple_profile.events.global_temple_profile_handler"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"temple_profile.tasks.all"
# 	],
# 	"daily": [
# 		"temple_profile.tasks.daily"
# 	],
# 	"hourly": [
# 		"temple_profile.tasks.hourly"
# 	],
# 	"weekly": [
# 		"temple_profile.tasks.weekly"
# 	],
# 	"monthly": [
# 		"temple_profile.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "temple_profile.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "temple_profile.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "temple_profile.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "temple_profile.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["temple_profile.utils.before_request"]
# after_request = ["temple_profile.utils.after_request"]

# Job Events
# ----------
# before_job = ["temple_profile.utils.before_job"]
# after_job = ["temple_profile.utils.after_job"]

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
# 	"temple_profile.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# Require all whitelisted methods to have type annotations
require_type_annotated_api_methods = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

