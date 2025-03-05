# Copyright (c) 2025, cinnamonlabs.io and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TabbyPaymentLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		name: DF.Int | None
		request_data: DF.Code | None
		response_data: DF.Code | None
		status: DF.Literal["Success", "Error"]
	# end: auto-generated types
	pass
