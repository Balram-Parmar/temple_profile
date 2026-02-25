import frappe
from frappe.model.document import Document

class FolkBoys(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from temple_profile.folk_nirma.doctype.folk_boys_attendance.folk_boys_attendance import FolkBoysAttendance

        attendance: DF.Table[FolkBoysAttendance]
        name1: DF.Data | None
        rounds_chanting_daily: DF.Int
    # end: auto-generated types

    def before_save(self):
        if self.flags.ignore_attendance_sync:
            return
        self.sync_attendance_to_doctype()

    def sync_attendance_to_doctype(self):
        for row in self.attendance:
            if row.attendance_id:
                if frappe.db.exists("Attendance", row.attendance_id):
                    att_doc = frappe.get_doc("Attendance", row.attendance_id)
                    att_doc.date = row.date
                    att_doc.status = row.status
                    att_doc.notes = row.notes
                    att_doc.flags.ignore_attendance_sync = True
                    att_doc.save(ignore_permissions=True)
                else:
                    self._create_attendance_record(row)
            else:
                self._create_attendance_record(row)

        self.remove_deleted_attendance_records()

    def _create_attendance_record(self, row):
        att_doc = frappe.get_doc({
            "doctype": "Attendance",
            "folk_boy": self.name,   # ✅ fixed field name
            "date": row.date,
            "status": row.status,
            "notes": row.notes,
        })
        att_doc.flags.ignore_attendance_sync = True
        att_doc.insert(ignore_permissions=True)
        row.attendance_id = att_doc.name

    def remove_deleted_attendance_records(self):
        existing_ids = {
            row.attendance_id
            for row in self.attendance
            if row.attendance_id
        }

        all_linked = frappe.get_all(
            "Attendance",
            filters={"folk_boy": self.name},   # ✅ fixed field name
            pluck="name"
        )

        for att_name in all_linked:
            if att_name not in existing_ids:
                frappe.delete_doc(
                    "Attendance", att_name,
                    ignore_permissions=True,
                    force=True
                )

    def onload(self):
        attendance_records = frappe.get_all(
            "Attendance",
            filters={"folk_boy": self.name},   # ✅ fixed field name
            fields=["name", "date", "status", "note"],
            order_by="date asc"
        )

        existing_ids = {row.attendance_id for row in self.attendance}

        for rec in attendance_records:
            if rec["name"] not in existing_ids:
                self.append("attendance", {
                    "date": rec["date"],
                    "status": rec["status"],
                    "note": rec["note"],
                    "attendance_id": rec["name"]
                })