frappe.ui.form.on("Importer", {
	refresh(frm) {
		// 1. Existing Logic: Toggle visibility/readonly
		let is_new = frm.is_new();
		frm.toggle_display(["download", "attach"], !is_new);
		frm.set_df_property("target_doc_type", "read_only", is_new ? 0 : 1);
		frm.set_df_property("name", "read_only", is_new ? 0 : 1);

		// 2. Clear buttons on refresh; preview_csv will handle adding it back if valid
		frm.clear_custom_buttons();

		// 3. Load preview if file exists
		if (frm.doc.attach) {
			frm.trigger("preview_csv");
		} else {
			frm.fields_dict.table_data.$wrapper.html("");
		}
	},

	attach: function (frm) {
		frm.trigger("preview_csv");
	},

	preview_csv: function (frm) {
		let field_wrapper = frm.fields_dict.table_data.$wrapper;

		if (!frm.doc.attach) {
			field_wrapper.html('<div class="text-muted">No file attached.</div>');
			frm.clear_custom_buttons();
			return;
		}

		field_wrapper.html('<div class="text-muted">Loading preview...</div>');

		fetch(frm.doc.attach)
			.then((response) => response.text())
			.then((text) => {
				let lines = text.split(/\r\n|\n/).filter((line) => line.trim() !== "");

				if (lines.length === 0) {
					field_wrapper.html('<div class="text-muted">File is empty.</div>');
					return;
				}

				let headers = lines[0].split(",");
				let mobile_idx = headers.findIndex((h) => h.trim() === "mobile_number");
				let invalid_entries = [];

				if (mobile_idx !== -1) {
					for (let i = 1; i < lines.length; i++) {
						let row_data = lines[i].split(",");
						if (row_data.length > mobile_idx) {
							let mobile_val = row_data[mobile_idx].trim();
							// Validation: Only digits, min 10
							let isValid = /^\d{10,}$/.test(mobile_val);
							if (!isValid) {
								invalid_entries.push(`Row ${i + 1}: ${mobile_val}`);
							}
						}
					}
				}

				// --- VALIDATION FAILED ---
				if (invalid_entries.length > 0) {
					// Remove the button so they can't process bad data
					frm.clear_custom_buttons();

					// Limit display to at most 10 invalid numbers to keep UI clean
					let display_invalids = invalid_entries.slice(0, 10);
					let error_list = display_invalids.join("<br>");
					let extra_msg =
						invalid_entries.length > 10
							? `<br>...and ${invalid_entries.length - 10} more errors.`
							: "";

					let error_html = `
                        <div class="alert alert-danger">
                            <h4 class="alert-heading">Validation Error</h4>
                            <p>Mobile numbers must be at least 10 digits (no spaces or symbols). <b>Process button disabled until fixed.</b></p>
                            <hr>
                            <strong>Invalid Numbers Found (showing top 10):</strong>
                            <div style="margin-top: 10px; background: #fff; padding: 10px; border: 1px solid #d1d1d1; font-family: monospace;">
                                ${error_list}
                                ${extra_msg}
                            </div>
                        </div>`;

					field_wrapper.html(error_html);
					return;
				}

				// --- VALIDATION PASSED ---
				// 1. Add the "Process CSV" button now that we know data is clean
				frm.clear_custom_buttons();
				frm.add_custom_button(__("Process CSV"), () => {
					frm.trigger("process_csv_logic");
				}).addClass("btn-primary");

				// 2. Render Table Preview
				let preview_rows = lines.slice(0, 11);
				let html = `<div style="overflow-x: auto;"><table class="table table-bordered table-condensed table-striped"><thead>`;

				preview_rows.forEach((row, index) => {
					let columns = row.split(",");
					html += "<tr>";
					columns.forEach((col) => {
						html += index === 0 ? `<th>${col}</th>` : `<td>${col}</td>`;
					});
					html += index === 0 ? "</tr></thead><tbody>" : "</tr>";
				});

				html += `</tbody></table></div>`;
				if (lines.length > 11) {
					html += `<p class="text-muted small">Showing first 10 rows of ${lines.length - 1} total records.</p>`;
				}
				field_wrapper.html(html);
			})
			.catch((error) => {
				field_wrapper.html(`<div class="text-danger">Error: ${error.message}</div>`);
			});
	},

	process_csv_logic: function (frm) {
		frappe.call({
			method: "temple_profile.temple_profile.doctype.importer.importer.process_csv",
			args: {
				docname: frm.doc.name,
				target_doctype: frm.doc.target_doc_type,
			},
			callback: function (r) {
				if (!r.exc && r.message) {
					// ... (Your existing Success Message logic)
					frappe.msgprint({
						title: __("Success"),
						message: "Import Complete",
						indicator: "green",
					});
				}
			},
		});
	},
});
