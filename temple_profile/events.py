import frappe

def global_temple_profile_handler(doc, method):
    """
    Main entry point. 
    1. Checks if this DocType is enabled for syncing.
    2. If yes, runs the profile linking logic.
    """
    # GATEKEEPER: Stop immediately if this DocType is not in your allowed list
    if not is_doctype_enabled(doc.doctype):
        return

    # If allowed, run your logic
    process_temple_profile_link(doc)

def is_doctype_enabled(doctype_name):
    """
    Checks if the DocType is checked in 'CD Sync Doctype'.
    Uses cache to ensure this runs instantly.
    """
    cache_key = "enabled_sync_doctypes"
    enabled_doctypes = frappe.cache().get_value(cache_key)

    if enabled_doctypes is None:
        # Fetch from DB if not in cache
        enabled_doctypes = frappe.get_all(
            "DocType Toggle Item", 
            filters={"parent": "CD Sync Doctype", "enabled": 1}, 
            pluck="doctype_link"
        )
        frappe.cache().set_value(cache_key, enabled_doctypes)

    return doctype_name in enabled_doctypes


def process_temple_profile_link(doc):
    # 1. Standard Flag Check
    if doc.flags.via_custom_importer:
        return

    try:
        # 2. Validation: Ensure we actually have a mobile number
        if not doc.get("mobile_number"):
            return

        # Fetch matching profiles
        profile_data = frappe.db.get_all(
            'Temple Profile', 
            filters={'mobile_number': doc.mobile_number}, 
            fields=["name", "full_name", 'mobile_number', 'email_id']
        )
        
        length = len(profile_data)

        # --- Case 1: Exactly One Match ---
        if length == 1:
            existing_profile = profile_data[0]
            doc.temple_id = existing_profile.name
            frappe.msgprint(f"Linked to existing Temple Profile: {existing_profile.name}", alert=True)

        # --- Case 2: No Match (Create New) ---
        elif length == 0:
            if not doc.get("full_name"):
                frappe.throw("Cannot create Temple Profile: Field 'Full Name' is missing.")

            new_temple_profile = frappe.get_doc({
                "doctype": "Temple Profile",
                "full_name": doc.full_name,
                "mobile_number": doc.mobile_number,
                "email_id": doc.email_id if doc.email_id else "NaN"
            })
            
            new_temple_profile.insert(ignore_permissions=True)
            doc.temple_id = new_temple_profile.name
            frappe.msgprint(f'Created new Temple Profile: {new_temple_profile.name}', alert=True)

        # --- Case 3: Multiple Matches (Create Request & STOP) ---
        else:
            duplicate_rec = frappe.get_doc({
                "doctype": "TP Creation Request",
                "full_name": doc.full_name,
                "mobile_number": doc.mobile_number,
                "description": f"Multiple conflicting records found in 'Temple Profile' while entering data for {doc.doctype}. Please review and resolve the duplicates manually to ensure accurate data entry. A creation request has been initiated to address the issue, but manual intervention is recommended to maintain data integrity.",
                "source_doc_type": doc.doctype,
                "conflicting_records": [] 
            })

            for row in profile_data:
                duplicate_rec.append("conflicting_records", {
                    "full_name": row.full_name,
                    "mobile_number": row.mobile_number,
                    "email_id": row.email_id if row.email_id else "NaN",
                    'temple_id': row.name
                })
            
            duplicate_rec.insert(ignore_permissions=True)
            frappe.db.commit()
            
            # This throw raises a ValidationError
            frappe.throw(f'Duplicate detected. Created Request: {duplicate_rec.name}')

    # --- CRITICAL FIX START ---
    except frappe.exceptions.ValidationError:
        # If the error is a ValidationError (caused by frappe.throw), 
        # we MUST re-raise it so Frappe knows to stop the save.
        raise
    # --- CRITICAL FIX END ---

    except frappe.exceptions.DuplicateEntryError:
        frappe.msgprint("Warning: Duplicate Entry Error occurred.", alert=True)

    except Exception as e:
        frappe.log_error(f"Temple Profile Link Error: {str(e)}")
        if not frappe.flags.in_test:
            frappe.msgprint("Error linking Temple Profile. Check Error Log.", alert=True)