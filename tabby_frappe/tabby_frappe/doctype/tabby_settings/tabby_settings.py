# Copyright (c) 2025, cinnamonlabs.io and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe.integrations.utils import create_request_log
import requests

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
		return 'https://api.tabby.ai/'
	@property
	def tabby_settings(self):
		return frappe.get_doc('Tabby Settings')
	@property
	def headers(self):

		key_secret = self.tabby_settings.get_password("key_secret")
		return {
            "Authorization": f"Bearer {key_secret}",
            "Content-Type": "application/json"
        }
	@frappe.whitelist()
	def register_webhook(self,site_url:str,is_production:bool):
		frappe.only_for("System Manager")
		url = self.base_url +"api/v1/webhooks"

		payload = {
			"url": f"{site_url}/api/v2/method/tabby_frappe.tabby_frappe.doctype.tabby_payment_request.tabby_payment_request.handle_tabby_webhook",
			"is_test": not is_production,
			"header": {
				"title": "string",
				"value": "string"
			}
		}
		response = requests.post(url,headers=self.headers,json=payload)
		response_status  = "Completed" if response.status_code ==200 else "Failed"
		create_request_log(data=payload, service_name="Tabby Webhook",output=response.json(),status=response_status,request_headers=
					 response.headers)
		if response_status == "Completed":
			return "Webhook Registered"
		else:
			frappe.throw(response.json()["error"])
