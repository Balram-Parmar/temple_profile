# Copyright (c) 2026, balram and contributors
# For license information, please see license.txt



import frappe
import pandas as pd
import os

from frappe.model.document import Document


class Importer(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attach: DF.Attach | None
		name1: DF.Data | None
		target_doc_type: DF.Literal["Folk", "Donor"]
	# end: auto-generated types

	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attach: DF.Attach | None
		name1: DF.Data | None
		target_doc_type: DF.Literal["Folk", "Donor"]
	

	pass



@frappe.whitelist()
def process_csv(docname: str, target_doctype: str):

    # --- 1. Fetch Importer Document ---
    doc = frappe.get_doc("Importer", docname)
    if not doc.attach:
        return {"success": False, "error": "No CSV file attached"}

    # --- 2. Resolve File Path ---
    file_path = frappe.get_site_path(doc.attach.lstrip("/"))

    if not os.path.exists(file_path):
        return {"success": False, "error": "CSV file not found on server"}

    # --- 3. Load & Validate CSV ---
    try:
        # Read as string to preserve phone numbers/IDs
        df = pd.read_csv(file_path, dtype=str)
    except Exception as e:
        return {"success": False, "error": f"Pandas Read Error: {str(e)}"}

    # Ensure strictly required columns for ID logic exist
    required_columns = ["full_name", "mobile_number"]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        frappe.throw(f"Missing mandatory columns in CSV: {', '.join(missing)}")
    
    stats = {
        "processed": 0,
        "temple_profile_created": 0,
        "existing_tp_profile": 0,
        "target_profile_created": 0,
        "existing_target_profile_linked": 0,
        "duplicates_flagged": 0 
    }

    for index, row in df.iterrows():
        # Clean basic identifiers for logic checks
        full_name = str(row.get('full_name', '')).strip()
        mobile_number = str(row.get('mobile_number', '')).strip()

        # Skip invalid rows
        if not mobile_number or mobile_number.lower() == 'nan':
            continue
        
        stats["processed"] += 1
        temple_profile_name = None

        # --- STEP A: Handle "Temple Profile" ---
        
        # 1. Fetch ALL records with this number (not just one)
        existing_profiles = frappe.db.get_all(
            "Temple Profile", 
            filters={"mobile_number": mobile_number}, 
            fields=["name", "full_name",'mobile_number','email_id']
        )
        
        count = len(existing_profiles)

        if count == 0:
            # --- Case 0: No Record -> Create NEW ---
            try:
                new_tp = frappe.get_doc({
                    "doctype": "Temple Profile",
                    "full_name": full_name,
                    "mobile_number": mobile_number
                })
                new_tp.insert(ignore_permissions=True)
                temple_profile_name = new_tp.name
                stats["temple_profile_created"] += 1
            except Exception as e:
                frappe.log_error(f"Error creating profile for {mobile_number}: {str(e)}", "CSV Import Error")
                continue

        elif count == 1:
            # --- Case 1: Single Record -> Use Existing ---
            temple_profile_name = existing_profiles[0].name
            stats["existing_tp_profile"] += 1

        else:
            # --- Case 2: Multiple Records -> Flag in "TP Creation Request" ---
            try:
                duplicate_req = frappe.get_doc({
                    "doctype": "TP Creation Request",
                    "full_name": full_name,
                    "mobile_number": mobile_number,
                    "description": "Multiple records with same mobile number are found in tp data base",
                    "conflicting_records": [] ,
                    'source_doc_type':"Custom Importer Tool"
                })

                # frappe.msgprint(str(existing_profiles))
                for profile in existing_profiles:
                    duplicate_req.append("conflicting_records", 
                        {
                        "full_name": profile.full_name,
                        "mobile_number": profile.mobile_number,
                        "email_id":profile.email_id if profile.email_id else "Na", 
                        "temple_id":profile.name
                        
                        }
                       
                        )
                
                duplicate_req.insert(ignore_permissions=True)
                stats["duplicates_flagged"] += 1
                
                # CRITICAL: Skip linking target profile because we don't know which Temple ID to use
                continue 

            except Exception as e:
                frappe.log_error(f"Error logging duplicate request for {mobile_number}: {str(e)}", "CSV Import Error")
                continue

        # --- STEP B: Link to Target (Folk/Donor) ---
        # This code only runs if count was 0 or 1
        
        target_name = frappe.db.get_value(target_doctype, {"mobile_number": mobile_number}, "name")

        if target_name:
            # Case 1: Target exists -> Just link the Temple Profile
            frappe.db.set_value(target_doctype, target_name, "temple_id", temple_profile_name)
            stats["existing_target_profile_linked"] += 1
        else:
            # Case 2: Target does NOT exist -> Create NEW with DYNAMIC fields
            try:
                # 1. Initialize data with system requirements
                target_data = {
                    "doctype": target_doctype,
                    "temple_id": temple_profile_name
                }

                # 2. Dynamically map ALL CSV columns to this dictionary
                for col in df.columns:
                    val = str(row[col]).strip()
                    
                    # Only add valid values (skip 'nan' or empty strings)
                    if val and val.lower() != 'nan':
                        target_data[col] = val

                # 3. Create the document
                new_target = frappe.get_doc(target_data)
                new_target.flags.via_custom_importer = True
                new_target.insert(ignore_permissions=True)
                stats["target_profile_created"] += 1

            except Exception as e:
                frappe.log_error(f"Error creating target for {mobile_number}: {str(e)}", "CSV Import Error")

    # --- 5. Commit & Return ---
    frappe.db.commit()

    clean_stats = {k: int(v) for k, v in stats.items()}

    return {
        "success": True,
        "message": "CSV Processing Completed",
        "stats": clean_stats
    }










































































