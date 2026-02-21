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

		// Fetch the file content
		fetch(frm.doc.attach)
			.then((response) => response.text())
			.then((text) => {
				// Split into lines (handle Windows \r\n and Unix \n)
				let lines = text.split(/\r\n|\n/);

				// Get Header + 10 Data Rows
				let preview_rows = lines.slice(0, 11);

				if (preview_rows.length === 0) return;

				// Build HTML Table
				let html = `
                    <div style="overflow-x: auto;">
                        <table class="table table-bordered table-condensed table-striped">
                            <thead>`;

				preview_rows.forEach((row, index) => {
					if (row.trim() === "") return;

					// Basic CSV split by comma (Note: Does not handle commas inside quotes)
					let columns = row.split(",");

					if (index === 0) {
						// Header Row
						html += "<tr>";
						columns.forEach((col) => (html += `<th>${col}</th>`));
						html += "</tr></thead><tbody>";
					} else {
						// Data Rows
						html += "<tr>";
						columns.forEach((col) => (html += `<td>${col}</td>`));
						html += "</tr>";
					}
				});

				html += `</tbody></table></div>`;

				// Add "Showing X of Y rows" text
				if (lines.length > 11) {
					html += `<p class="text-muted small">Showing first 10 rows of ${lines.length - 1} total records.</p>`;
				}

				// Inject into the "table_data" field wrapper
				field_wrapper.html(html);
			})
			.catch((error) => {
				console.error("Error loading CSV:", error);
				field_wrapper.html(
					`<div class="text-danger">Error loading CSV preview: ${error.message}</div>`,
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
						frappe.msgprint("Excel download requires server-side implementation.");
					}
					d.hide();
				},
			});
			d.show();
		});
	},
});
