# Copyright (c) 2025, cinnamonlabs.io and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document


class TabbyPaymentRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		amount: DF.Currency
		currency_code: DF.Link | None
		customer_address: DF.Data | None
		customer_dob: DF.Data | None
		customer_email: DF.Data | None
		customer_name: DF.Data | None
		customer_phone: DF.Data | None
		customer_reference: DF.Data | None
		ref_docname: DF.DynamicLink | None
		ref_doctype: DF.Link | None
		refund_id: DF.Data | None
		refunded_at: DF.Datetime | None
		status: DF.Literal["PENDING", "CREATED", "AUTHORIZED", "CLOSED", "REJECTED", "EXPIRED", "FAILURE", "REFUND"]
		tabby_order_ref: DF.Data | None
		tabby_order_url: DF.LongText | None
		tabby_payment_id: DF.Data | None
	# end: auto-generated types

	@property
	def tabby_settings(self):
		return frappe.get_cached_doc("Tabby Settings")

	@property
	def headers(self):
		key_secret = self.tabby_settings.get_password("key_secret")
		return {
			"Authorization": f"Bearer {key_secret}",
			"Content-Type": "application/json",
		}

	@property
	def tabby_base_url(self):
		return "https://api.tabby.ai/"

	def before_save(self):
		if not self.tabby_order_ref:
			self.create_order_on_tabby()

	def create_order_on_tabby(self):
		tabby_settings = frappe.get_cached_doc("Tabby Settings")
		address = None
		if self.customer_address:
			address_doc = frappe.get_cached_doc("Address", self.customer_address)
			address = {
				"address": address_doc.address_line1,
				"city": address_doc.city,
				"zip": address_doc.pincode,
			}
		buyer = {
			"phone": self.customer_phone or "",
			"email": self.customer_email or "",
			"name": self.customer_name or "",
			"dob": self.customer_dob or "",
		}

		checkout_data = tabby_settings.create_session(
			amount=self.amount,
			reference_id=str(self.name),
			currency_code=self.currency_code,
			buyer=buyer,
			address=address,
		)

		self.tabby_order_url = checkout_data["configuration"]["available_products"][
			"installments"
		][0]["web_url"]
		self.tabby_order_ref = checkout_data["id"]
		self.tabby_payment_id = checkout_data["payment"]["id"]
		self.status = checkout_data["status"].upper()

	@frappe.whitelist()
	def capture_payment(self):
		response = self.tabby_settings.capture_payment(
			self.tabby_payment_id, self.amount
		)
		status = response["status"]
		self.status = status
		self.save()

	@frappe.whitelist()
	def sync_status(self):
		response = self.tabby_settings.get_order_status(self.tabby_payment_id)
		frappe.errprint(response)
		status = response["status"]
		self.status = status

		if response.get("refunds", []):
			self.refund_id = response["refunds"][0]["id"]
			self.refunded_at = frappe.utils.get_datetime_str(response["refunds"][0]["created_at"])
			self.status = "REFUND"

		self.save()

	@frappe.whitelist()
	def refund(self):
		frappe.only_for("System Manager")

		if self.status != "CLOSED":
			frappe.throw(frappe._("Refunds can be made only on completed payments!"))

		response = self.tabby_settings.refund_payment(
			self.tabby_payment_id, self.amount
		)

		if len(response.get("refunds", [])):
			self.refund_id = response["refunds"][0]["id"]
			self.refunded_at = frappe.utils.get_datetime_str(response["refunds"][0]["created_at"])
			self.status = "REFUND"
			self.save()


# Todo implement webhook
# @frappe.whitelist(allow_guest=True)
# def process_tabby_webhook():
# 	data = frappe.request.get_json()
# 	if data["status"] == "authorized":
# 		tabby_process_success(data["id"])

# 	return Response(status=200)


def refund_payment_for_payment_entry(doc, event=None):
	if doc.mode_of_payment != "Tabby":
		return

	frappe.get_doc("Tabby Payment Request", {"tabby_order_ref": doc.reference_no}).refund()