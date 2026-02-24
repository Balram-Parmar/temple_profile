frappe.ui.form.on("Importer", {
	refresh(frm) {
		// 1. Existing Logic: Toggle visibility/readonly
		let is_new = frm.is_new();
		frm.toggle_display(["download", "attach"], !is_new);
		frm.set_df_property("target_doc_type", "read_only", is_new ? 0 : 1);
		frm.set_df_property("name", "read_only", is_new ? 0 : 1);

		// 2. Existing Logic: Process CSV Button
		if (!is_new) {
			frm.add_custom_button(__("Process CSV"), () => {
				frappe.call({
					method: "temple_profile.temple_profile.doctype.importer.importer.process_csv",
					args: {
						docname: frm.doc.name,
						target_doctype: frm.doc.target_doc_type,
					},
					callback: function (r) {
						if (!r.exc && r.message) {
							let stats = r.message.stats;
							if (stats) {
								let msg = `
                                    <h5>Import Summary</h5>
                                    <table class="table table-bordered table-condensed">

                                        <tr><td>Rows Processed</td> <td><strong>${stats.processed}</strong></td></tr>
                                        <tr><td>Temple Profiles Created</td> <td>${stats.temple_profile_created}</td></tr>
                                        <tr><td>Existing Temple Profiles</td> <td>${stats.existing_tp_profile}</td></tr>
                                        <tr><td>Target Profiles Created</td> <td>${stats.target_profile_created}</td></tr>
										<tr><td>Existing Targets Linked</td> <td>${stats.existing_target_profile_linked}</td></tr>
										<tr><td>Conflict request Created</td> <td>${stats.temple_creation_req_created}</td></tr>
	
                                    </table>`;
								frappe.msgprint({
									title: __("Success"),
									message: msg,
									indicator: "green",
								});
							} else {
								frappe.msgprint("Process Complete");
							}
						}
					},
				});
			});
		}

		// 3. NEW: Load preview if file exists on refresh
		if (frm.doc.attach) {
			frm.trigger("preview_csv");
		}
	},

	// 4. NEW: Trigger preview when file is uploaded/changed
	attach: function (frm) {
		frm.trigger("preview_csv");
	},

	// 5. NEW: Function to fetch, parse, and render the CSV table
	preview_csv: function (frm) {
		let field_wrapper = frm.fields_dict.table_data.$wrapper;

		// Reset if no file
		if (!frm.doc.attach) {
			field_wrapper.html('<div class="text-muted">No file attached.</div>');
			return;
		}

		let file_url = frm.doc.attach;
		let file_extension = file_url.split(".").pop().toLowerCase();
		let supported_extensions = ["csv", "xls", "xlsx"];

		if (!supported_extensions.includes(file_extension)) {
			field_wrapper.html(
				'<div class="text-warning">Unsupported file type for preview. Please attach a CSV or Excel file.</div>',
			);
			return;
		}

		if (typeof XLSX === "undefined") {
			field_wrapper.html(
				'<div class="text-danger">SheetJS library is not loaded. Cannot generate preview.</div>',
			);
			return;
		}

		// Show loading state
		field_wrapper.html('<div class="text-muted">Loading preview...</div>');

		// Fetch the file as an ArrayBuffer so SheetJS can read both text and binary formats
		fetch(file_url)
			.then((response) => {
				if (!response.ok) throw new Error("Network response was not ok");
				return response.arrayBuffer();
			})
			.then((buffer) => {
				// Read the buffer using SheetJS
				let wb = XLSX.read(buffer, { type: "array" });

				// Get the first worksheet
				let first_sheet_name = wb.SheetNames[0];
				let worksheet = wb.Sheets[first_sheet_name];

				// Convert worksheet to an Array of Arrays (header: 1)
				// defval: "" ensures empty cells aren't skipped
				let data = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: "" });

				// Remove any completely empty rows from the end
				while (data.length > 0 && data[data.length - 1].join("").trim() === "") {
					data.pop();
				}

				if (data.length === 0) {
					field_wrapper.html('<div class="text-muted">File is empty.</div>');
					return;
				}

				// Get Header + 10 Data Rows
				let preview_rows = data.slice(0, 11);

				// Build HTML Table
				let html = `
                <div style="overflow-x: auto;">
                    <table class="table table-bordered table-condensed table-striped">
                        <thead>`;

				preview_rows.forEach((row, index) => {
					if (index === 0) {
						// Header Row
						html += "<tr>";
						row.forEach((col) => {
							html += `<th>${col}</th>`;
						});
						html += "</tr></thead><tbody>";
					} else {
						// Data Rows
						html += "<tr>";
						row.forEach((col) => {
							html += `<td>${col}</td>`;
						});
						html += "</tr>";
					}
				});

				html += `</tbody></table></div>`;

				// Add "Showing X of Y rows" text
				if (data.length > 11) {
					html += `<p class="text-muted small">Showing first 10 rows of ${data.length - 1} total records.</p>`;
				}

				// Inject into the "table_data" field wrapper
				field_wrapper.html(html);
			})
			.catch((error) => {
				console.error("Error loading file:", error);
				field_wrapper.html(
					`<div class="text-danger">Error loading file preview: ${error.message}</div>`,
				);
			});
	},

	// 6. Existing Logic: Download Button
	download: function (frm) {
		let target_doctype = frm.doc.target_doc_type;

		if (!target_doctype) {
			frappe.msgprint("Please select a Target Doc Type first.");
			return;
		}

		frappe.model.with_doctype(target_doctype, function () {
			let meta = frappe.get_meta(target_doctype);

			let valid_fields = meta.fields.filter((df) => {
				return (
					![
						"Section Break",
						"Column Break",
						"HTML",
						"Button",
						"Table",
						"temple_id",
					].includes(df.fieldtype) && df.fieldname != "temple_id"
				);
			});

			let dynamic_options = valid_fields.map((df) => {
				let is_mandatory = ["mobile_number", "full_name"].includes(df.fieldname);
				return {
					label: df.label,
					value: df.fieldname,
					checked: is_mandatory ? 1 : 1,
					danger: is_mandatory ? 1 : 0,
				};
			});

			let d = new frappe.ui.Dialog({
				title: `Export ${target_doctype} Template`,
				fields: [
					{
						label: "File Type",
						fieldname: "file_type",
						fieldtype: "Select",
						options: "CSV\nExcel",
						default: "CSV",
						reqd: 1,
					},
					{
						fieldtype: "Section Break",
						label: "Select Fields",
					},
					{
						fieldname: "columns",
						fieldtype: "MultiCheck",
						columns: 2,
						options: dynamic_options,
					},
				],
				primary_action_label: "Download",
				primary_action(values) {
					let selected = values.columns || [];
					let missing_mandatory = [];

					if (!selected.includes("full_name")) missing_mandatory.push("Full Name");
					if (!selected.includes("mobile_number"))
						missing_mandatory.push("Mobile Number");

					if (missing_mandatory.length > 0) {
						frappe.msgprint({
							title: "Missing Fields",
							message: `The following fields are mandatory:<br><b>${missing_mandatory.join(", ")}</b>`,
							indicator: "red",
						});
						return;
					}

					if (values.file_type === "CSV") {
						let csv_content = values.columns.join(",");
						let blob = new Blob([csv_content], { type: "text/csv;charset=utf-8;" });
						let link = document.createElement("a");
						let url = URL.createObjectURL(blob);
						link.setAttribute("href", url);
						link.setAttribute("download", `${target_doctype}_Template.csv`);
						link.style.visibility = "hidden";
						document.body.appendChild(link);
						link.click();
						document.body.removeChild(link);
						frappe.show_alert({ message: "Template downloaded", indicator: "green" });
					} else {
						if (typeof XLSX === "undefined") {
							frappe.msgprint(
								"SheetJS library is not loaded. Check your hooks.py CDN link.",
							);
						} else {
							let ws_data = [values.columns];
							let ws = XLSX.utils.aoa_to_sheet(ws_data);
							let wb = XLSX.utils.book_new();
							XLSX.utils.book_append_sheet(wb, ws, "Template");

							XLSX.writeFile(wb, `${target_doctype}_Template.xlsx`);
							frappe.show_alert({
								message: "Excel Template downloaded",
								indicator: "green",
							});
						}
					}
					d.hide();
				},
			});
			d.show();
		});
	},
});
