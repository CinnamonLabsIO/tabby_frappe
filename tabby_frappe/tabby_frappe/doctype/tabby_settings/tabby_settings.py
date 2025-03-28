# Copyright (c) 2025, cinnamonlabs.io and contributors
# For license information, please see license.txt

# import frappe
import frappe
import requests
from frappe.integrations.utils import (
	create_request_log,
	make_get_request,
	make_post_request,
)
from frappe.model.document import Document


class TabbySettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cancel_url: DF.Data | None
		failure_url: DF.Data | None
		key_id: DF.Data | None
		key_secret: DF.Password | None
		success_url: DF.Data | None
		webhook_secret: DF.Password | None
	# end: auto-generated types
	pass

	@property
	def base_url(self):
		return "https://api.tabby.ai/"

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

	@frappe.whitelist()
	def create_session(
		self,
		amount: float,
		reference_id: str,
		currency_code: str | None = None,
		buyer: dict | None = None,
		address: dict | None = None,
	):
		tabby_settings = self.tabby_settings
		payload = {
			"payment": {
				"amount": amount,
				"currency": currency_code,
				"buyer": buyer or {},
				"shipping_address": address or {},
				"order": {
					"reference_id": reference_id,
				},
			},
			"lang": frappe.local.lang,
			"merchant_code": "",
			"merchant_urls": {
				"success": tabby_settings.success_url,
				"cancel": tabby_settings.cancel_url,
				"failure": tabby_settings.failure_url,
			},
		}
		endpoint = f"{self.base_url}api/v2/checkout"
		response = None
		try:
			response = make_post_request(endpoint, json=payload, headers=self.headers)

			create_tabby_request_log(
				endpoint, data=payload, headers=self.headers, output=response
			)
		except Exception as e:
			create_tabby_request_log(endpoint, error=e, headers=self.headers)
			raise
		return response

	@frappe.whitelist()
	def get_order_status(self, payment_id: str):
		endpoint = f"{self.base_url}api/v2/payments/{payment_id}"
		key_secret = self.tabby_settings.get_password("key_secret")
		headers = {"Authorization": f"Bearer {key_secret}"}
		response = make_get_request(endpoint, headers=headers)
		return response

	@frappe.whitelist()
	def capture_payment(self, payment_id: str, amount: float):
		endpoint = f"{self.base_url}api/v2/payments/{payment_id}/captures"
		payload = {"amount": amount}
		response = make_post_request(endpoint, json=payload, headers=self.headers)
		return response

	@frappe.whitelist()
	def register_webhook(self, site_url: str, is_production: bool):
		frappe.only_for("System Manager")
		url = self.base_url + "api/v1/webhooks"

		payload = {
			"url": f"{site_url}/api/v2/method/tabby_frappe.tabby_frappe.doctype.tabby_payment_request.tabby_payment_request.handle_tabby_webhook",
			"is_test": not is_production,
			"header": {"title": "string", "value": "string"},
		}
		response = requests.post(url, headers=self.headers, json=payload)
		response_status = "Completed" if response.status_code == 200 else "Failed"
		create_request_log(
			data=payload,
			service_name="Tabby Webhook",
			output=response.json(),
			status=response_status,
			request_headers=response.headers,
		)
		if response_status == "Completed":
			return "Webhook Registered"
		else:
			frappe.throw(response.json()["error"])


def create_tabby_request_log(
	url: str, data=None, error=None, headers=None, output=None
):
	create_request_log(
		data,
		url=url,
		request_headers=headers,
		is_remote_request=True,
		service_name="Tabby",
		reference_doctype="Tabby Settings",
		reference_docname="Tabby Settings",
		output=output,
		error=error,
		status="Failed" if error else "Completed",
	)
