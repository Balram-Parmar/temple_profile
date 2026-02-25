frappe.query_reports["Folk Boys Attendance Report"] = {
	filters: [
		{
			fieldname: "date",
			label: __("Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nPresent\nAbsent\nLate\nNot Marked",
			default: "",
		},
	],

	// Color code rows based on status
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (data) {
			if (data.status === "Present") {
				value = `<span style="color: green; font-weight: bold;">${value}</span>`;
			} else if (data.status === "Absent") {
				value = `<span style="color: red; font-weight: bold;">${value}</span>`;
			} else if (data.status === "Late") {
				value = `<span style="color: orange; font-weight: bold;">${value}</span>`;
			} else if (data.status === "Not Marked") {
				value = `<span style="color: grey;">${value}</span>`;
			}
		}

		return value;
	},
};
