# Copyright (c) 2026, balram and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TPCreationRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from temple_profile.temple_profile.doctype.conflicting_records.conflicting_records import conflicting_records

		conflicting_records: DF.Table[conflicting_records]
		description: DF.SmallText | None
		full_name: DF.Data | None
		mobile_number: DF.Data | None
		source_doc_type: DF.Data | None
	# end: auto-generated types

	pass
