# Copyright (c) 2025, cinnamonlabs.io and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TabbyMonthlyInstallments(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		due_date: DF.Date
		name: DF.Int | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		principal: DF.Currency
		service_fee: DF.Currency
	# end: auto-generated types
	pass
