# Copyright (c) 2026, balram and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FolkBoysAttendance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attendance_id: DF.Link | None
		date: DF.Date | None
		notes: DF.SmallText | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		status: DF.Literal["Present", "Absent"]
	# end: auto-generated types
	pass
