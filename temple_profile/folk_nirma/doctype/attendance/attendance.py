import frappe
from frappe.model.document import Document

class Attendance(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        date: DF.Data | None
        folk_boy: DF.Link | None
        note: DF.SmallText | None
        status: DF.Literal["Present", "Absent"]
    # end: auto-generated types

    def after_insert(self):
        self.sync_to_folk_boys()

    def on_update(self):
        self.sync_to_folk_boys()

    def on_trash(self):
        if not self.folk_boy:
            return

        boy_doc = frappe.get_doc("Folk Boys", self.folk_boy)
        rows_to_remove = [
            row for row in boy_doc.attendance
            if row.attendance_id == self.name
        ]

        for row in rows_to_remove:
            boy_doc.attendance.remove(row)

        boy_doc.flags.ignore_attendance_sync = True
        boy_doc.save(ignore_permissions=True)

    def sync_to_folk_boys(self):
        if not self.folk_boy:
            return

        boy_doc = frappe.get_doc("Folk Boys", self.folk_boy)

        existing_row = None
        for row in boy_doc.attendance:
            if row.attendance_id == self.name:
                existing_row = row
                break

        if existing_row:
            existing_row.date = self.date
            existing_row.status = self.status
            existing_row.note = self.note        # ✅ note not notes
        else:
            boy_doc.append("attendance", {
                "date": self.date,
                "status": self.status,
                "note": self.note,               # ✅ note not notes
                "attendance_id": self.name
            })

        boy_doc.flags.ignore_attendance_sync = True
        boy_doc.save(ignore_permissions=True)