import frappe
from frappe.utils import getdate, get_first_day, get_last_day

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "boy_name",
            "label": "Boy Name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "date",
            "label": "Date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "note",
            "label": "Note",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "present_this_month",
            "label": "Total Present This Month",
            "fieldtype": "Int",
            "width": 180
        }
    ]


def get_data(filters):
    conditions = ""
    values = {}

    selected_date = filters.get("date")

    if selected_date:
        conditions += " AND a.date = %(date)s"
        values["date"] = selected_date

    if filters.get("status"):
        conditions += " AND a.status = %(status)s"
        values["status"] = filters["status"]

    # Get month range based on selected date
    if selected_date:
        month_start = get_first_day(getdate(selected_date))
        month_end = get_last_day(getdate(selected_date))
    else:
        from frappe.utils import today
        month_start = get_first_day(getdate(today()))
        month_end = get_last_day(getdate(today()))

    # Fetch present count per boy for this month
    monthly_present = frappe.db.sql("""
        SELECT
            a.folk_boy,
            COUNT(*) AS present_count
        FROM
            `tabAttendance` a
        WHERE
            a.status = 'Present'
            AND a.date BETWEEN %(month_start)s AND %(month_end)s
        GROUP BY
            a.folk_boy
    """, {"month_start": month_start, "month_end": month_end}, as_dict=True)

    # Build a dict for quick lookup { folk_boy_id: present_count }
    monthly_map = {row["folk_boy"]: row["present_count"] for row in monthly_present}

    # Fetch boys who HAVE attendance records on selected date
    attendance_data = frappe.db.sql("""
        SELECT
            fb.name1 AS boy_name,
            a.folk_boy,
            a.date,
            a.status,
            a.note
        FROM
            `tabAttendance` a
        LEFT JOIN
            `tabFolk Boys` fb ON fb.name = a.folk_boy
        WHERE
            1=1
            {conditions}
        ORDER BY
            fb.name1 ASC
    """.format(conditions=conditions), values, as_dict=True)

    # Attach monthly present count to each row
    for row in attendance_data:
        row["present_this_month"] = monthly_map.get(row["folk_boy"], 0)

    result = list(attendance_data)

    # Show boys with NO attendance record on that date (Not Marked)
    if selected_date and not filters.get("status"):
        marked_boys = {row["folk_boy"] for row in attendance_data}

        all_boys = frappe.get_all("Folk Boys", fields=["name", "name1"])

        for boy in all_boys:
            if boy["name"] not in marked_boys:
                result.append({
                    "boy_name": boy["name1"],
                    "folk_boy": boy["name"],
                    "date": selected_date,
                    "status": "Not Marked",
                    "note": "",
                    "present_this_month": monthly_map.get(boy["name"], 0)  # ✅ still shows their monthly count
                })

        result.sort(key=lambda x: x.get("boy_name") or "")
        

    return result