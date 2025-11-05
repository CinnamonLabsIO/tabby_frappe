# Copyright (c) 2025, cinnamonlabs.io and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TabbyWebhookLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		headers: DF.JSON | None
		output: DF.JSON | None
		status: DF.Data | None
	# end: auto-generated types
	pass
