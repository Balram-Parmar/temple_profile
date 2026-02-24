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
    pass


@frappe.whitelist()
def process_csv(docname: str, target_doctype: str):
    # --- 1. Fetch Importer Document ---
    doc = frappe.get_doc("Importer", docname)
    if not doc.attach:
        return {"success": False, "error": "No file attached"}

    # --- 2. Resolve File Path ---
    file_path = frappe.get_site_path(doc.attach.lstrip("/"))

    if not os.path.exists(file_path):
        return {"success": False, "error": "File not found on server"}

    # --- 3. Load & Validate File ---
    try:
        # Read as string based on file extension, fill NaNs with empty strings, and handle literal "nan" texts
        ext = file_path.lower()
        if ext.endswith('.csv'):
            df = pd.read_csv(file_path, dtype=str)
        elif ext.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path, dtype=str)
        else:
            return {"success": False, "error": "Unsupported file format. Please attach a CSV or Excel file."}
            
        df.fillna('', inplace=True)
        df = df.replace({'nan': '', 'NaN': ''})
    except Exception as e:
        return {"success": False, "error": f"Pandas Read Error: {str(e)}"}

    # Ensure strictly required columns for ID logic exist
    required_columns = ["full_name", "mobile_number"]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        frappe.throw(f"Missing mandatory columns in File: {', '.join(missing)}")
    
    stats = {
        "processed": 0,
        "temple_profile_created": 0,
        "existing_tp_profile": 0,
        "target_profile_created": 0,
        "existing_target_profile_linked": 0,
        "temple_creation_req_created": 0 
    }
   

    # --- 4. Pre-fetch existing data to prevent N+1 queries ---
    all_mobiles = [str(m).strip() for m in df['mobile_number'].unique() if str(m).strip()]
    
    # Pre-fetch Temple Profiles
    existing_tps = frappe.db.get_all(
        "Temple Profile", 
        filters={"mobile_number": ("in", all_mobiles)}, 
        fields=["name", "full_name", "mobile_number", "email_id"]
    )
    tp_map = {}
    for tp in existing_tps:
        tp_map.setdefault(tp.mobile_number, []).append(tp)

    # Pre-fetch Target Profiles
    existing_targets = frappe.db.get_all(
        target_doctype, 
        filters={"mobile_number": ("in", all_mobiles)}, 
        fields=["name", "mobile_number"]
    )
    target_map = {t.mobile_number: t.name for t in existing_targets}

    # --- 5. Process Rows ---
    for row in df.to_dict('records'):
        full_name = str(row.get('full_name', '')).strip()
        mobile_number = str(row.get('mobile_number', '')).strip()
        email_id = str(row.get('email_id', '')).strip()

        # Skip invalid rows
        if not mobile_number:
            continue
        
        stats["processed"] += 1
        temple_profile_name = None

        # --- STEP A: Handle "Temple Profile" ---
        existing_profiles = tp_map.get(mobile_number, [])
        count = len(existing_profiles)

        if count == 0:
            # --- Case 0: No Record -> Create NEW ---
            try:
                new_tp = frappe.get_doc({
                    "doctype": "Temple Profile",
                    "full_name": full_name,
                    "mobile_number": mobile_number,
                    "email_id": email_id
                })
                new_tp.insert(ignore_permissions=True)
                temple_profile_name = new_tp.name
                stats["temple_profile_created"] += 1
                
                # Add to local map so duplicates in the same CSV are caught
                tp_map[mobile_number] = [{"name": new_tp.name, "full_name": full_name, "mobile_number": mobile_number, "email_id": email_id}]
              
            except Exception as e:
                frappe.log_error(f"Error creating profile for {mobile_number}: {str(e)}", "CSV Import Error")
                continue

        elif count == 1:
            # --- Case 1: Exact Match -> Flag in "TP Creation Request" ---
            try:
                prof = existing_profiles[0]
                duplicate_req = frappe.get_doc({
                    "doctype": "TP Creation Request",
                    "full_name": full_name,
                    "mobile_number": mobile_number,
                    "description" : 
                                    f"""
                                🚫 Duplicate Entry Attempt Detected

                                📌 User Attempted To Add:
                                • Full Name      : {full_name}
                                • Mobile Number  : {mobile_number}

                                📂 Existing Record Found In Temple Profile:
                                • Full Name      : {prof.get('full_name')}
                                • Mobile Number  : {prof.get('mobile_number')}
                                • Doctype Name   : {prof.get('name')}

                                ⚠️ This record already exists in the system.
                                """,


                    "source_doc_type": "Custom Importer Tool"
                })
                duplicate_req.insert(ignore_permissions=True)
                stats["temple_creation_req_created"] += 1
                # Skipping Target Profile creation/linking as requested
                continue

            except Exception as e:
                frappe.log_error(f"Error logging single duplicate request for {mobile_number}: {str(e)}", "CSV Import Error")
                continue
                
        else:
            # --- Case 2: Multiple Records -> Flag in "TP Creation Request" ---
            try:
                duplicate_req = frappe.get_doc({
                    "doctype": "TP Creation Request",
                    "full_name": full_name,
                    "mobile_number": mobile_number,
                    "description": f"Multiple records with same mobile number are found in Temple Profile database please resolve it and manually enter data in target doc type which is {target_doctype}",
                    "source_doc_type": "Custom Importer Tool"
                })

                for profile in existing_profiles:
                    duplicate_req.append("conflicting_records", {
                        "full_name": profile.get('full_name'),
                        "mobile_number": profile.get('mobile_number'),
                        "email_id": profile.get('email_id') or "Na", 
                        "temple_id": profile.get('name')
                    })
                
                duplicate_req.insert(ignore_permissions=True)
                stats["temple_creation_req_created"] += 1
                
                # CRITICAL: Skip linking target profile because we don't know which Temple ID to use
                continue 

            except Exception as e:
                frappe.log_error(f"Error logging multiple duplicate request for {mobile_number}: {str(e)}", "CSV Import Error")
                continue

        # --- STEP B: Link to Target (Folk/Donor) ---
        target_name = target_map.get(mobile_number)

        if target_name:
            # Case 1: Target exists -> Just link the Temple Profile
            frappe.db.set_value(target_doctype, target_name, "temple_id", temple_profile_name)
            stats["existing_target_profile_linked"] += 1
        else:
            # Case 2: Target does NOT exist -> Create NEW with DYNAMIC fields
            try:
                target_data = {
                    "doctype": target_doctype,
                    "temple_id": temple_profile_name
                }

                # Map cleaned CSV/Excel columns directly
                for col, val in row.items():
                    val = str(val).strip()
                    if val:
                        target_data[col] = val

                new_target = frappe.get_doc(target_data)
                new_target.flags.via_custom_importer = True
                new_target.insert(ignore_permissions=True)
                stats["target_profile_created"] += 1
                
                # Add to local map to prevent creating multiple targets for duplicates inside the same file
                target_map[mobile_number] = new_target.name

            except Exception as e:
                frappe.log_error(f"Error creating target for {mobile_number}: {str(e)}", "CSV Import Error")

    # --- 6. Commit & Return ---
    frappe.db.commit()

    return {
        "success": True,
        "message": "File Processing Completed",
        "stats": {k: int(v) for k, v in stats.items()}
    }