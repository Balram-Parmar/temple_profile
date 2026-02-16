# Copyright (c) 2026, balram and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TempleProfileRelatives(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		full_name: DF.Data | None
		mobile_number: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		relation: DF.Literal["Father", "Mother", "Husband", "Wife", "Son", "Daughter", "Brother", "Sister", "Grandfather", "Grandmother", "Grandson", "Granddaughter", "Great-Grandfather", "Great-Grandmother", "Great-Grandson", "Great-Granddaughter", "Uncle", "Aunt", "Nephew", "Niece", "Cousin", "Brother-in-law", "Sister-in-law", "Father-in-law", "Mother-in-law", "Son-in-law", "Daughter-in-law", "Stepfather", "Stepmother", "Stepson", "Stepdaughter", "Stepbrother", "Stepsister", "Half-Brother", "Half-Sister", "Godfather", "Godmother", "Godson", "Goddaughter", "Guardian", "Ward", "Ancestor", "Descendant", "Partner", "Spouse", "Fianc\u00e9", "Fianc\u00e9e", "Boyfriend", "Girlfriend", "Parent", "Child", "Sibling", "Relative"]
	# end: auto-generated types

	pass
