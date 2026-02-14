# Copyright (c) 2026, balram and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class conflicting_records(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		email_id: DF.Data | None
		full_name: DF.Data | None
		mobile_number: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		temple_id: DF.Link | None
	# end: auto-generated types

	pass
