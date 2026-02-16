# Copyright (c) 2026, balram and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TempleProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from temple_profile.temple_profile.doctype.temple_profile_relatives.temple_profile_relatives import TempleProfileRelatives

		email_id: DF.Data | None
		full_name: DF.Data | None
		mobile_number: DF.Data | None
		relatives: DF.Table[TempleProfileRelatives]
	# end: auto-generated types

	pass
