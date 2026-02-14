# Copyright (c) 2026, balram and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CDSyncDoctype(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from temple_profile.temple_profile.doctype.doctype_toggle_item.doctype_toggle_item import DocTypeToggleItem

		doctype_sync_list: DF.Table[DocTypeToggleItem]


	def on_update(self):
		frappe.cache().delete_value("enabled_sync_doctypes")
		frappe.msgprint("Sync Configuration Updated. New DocTypes will now be processed.")

	def before_save(self):
    
		required_fields = {'mobile_number', 'full_name', 'temple_id'}

		for row in self.doctype_sync_list:
			# 1. Skip if the row isn't enabled or the link is empty
			if not row.enabled or not row.doctype_link:
				continue

			# 2. Get the meta of the LINKED DocType (e.g., "Customer" or "Lead")
			meta = frappe.get_meta(row.doctype_link)
			
			# 3. Get all fieldnames present in that target DocType
			existing_fields = {f.fieldname for f in meta.fields}

			# 4. Find which required fields are missing using set subtraction
			missing = required_fields - existing_fields

			# 5. Throw error if any are missing
			if missing:
				frappe.throw(
					f"The DocType <b>{row.doctype_link}</b> is missing mandatory fields : "
					f"{' | '.join(missing)}. Please add them before enabling sync."
				)
					

		