# Copyright (c) 2025, cinnamonlabs.io and contributors
# For license information, please see license.txt


from frappe.model.document import Document
import frappe
from frappe.integrations.utils import create_request_log, make_get_request
import requests
import werkzeug.utils
from frappe.utils import get_url


TABBY_API_BASE_URL = "https://api.tabby.ai/"


class TabbyPaymentRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		amount: DF.Currency
		order_id: DF.Data | None
		payment_url: DF.Data | None
		quotation_id: DF.Data | None
		reference_id: DF.Data
		status: DF.Literal["Pending", "Completed", "Failure", "Refund"]
		tabby_payment_id: DF.Data
	# end: auto-generated types

	@property
	def is_complete(self):
		return self.status == "Completed"

	@property
	def tabby_settings(self):
		return get_tabby_settings()

	@property
	def headers(self):
		return get_headers()

	@property
	def tabby_base_url(self):
		return TABBY_API_BASE_URL

	@frappe.whitelist()
	def refund(self):
		frappe.only_for("System Manager")

		if not self.is_complete:
			frappe.throw("Refunds Can be Made Only on Complete Payments!")
		url = self.tabby_base_url + f"api/v2/payments/{self.tabby_payment_id}/refunds"
		response = requests.post(
			url, headers=self.headers, json={"amount": self.amount}
		)
		status = "Completed" if response.status_code == 200 else "Failed"
		create_request_log(
			data={"payment_id": self.tabby_payment_id, "amount": self.amount},
			service_name="Tabby Refund",
			output=response.json(),
			status=status,
			request_headers=response.headers,
		)
		if status == "Completed":
			self.status = "Refund"
			self.save()
			return "refund successful"
		else:
			frappe.throw("Could not process refund, please try again later.")


def get_tabby_settings():
	return frappe.get_cached_doc("Tabby Settings")


def get_headers():
	return {
		"Authorization": f'Bearer {get_tabby_settings().get_password("key_secret")}',
		"Content-Type": "application/json",
	}


@frappe.whitelist()
def initiate_checkout(
	amount: int,
	quotation_id: str,
	currency: str = "SAR",
	description: str = "",
	language: str = "en",
	merchant_code: str = "",
	buyer="",
):
	payload = {
		"payment": {
			"amount": amount,
			"currency": currency,
			"description": description,
			"buyer": buyer,
		},
		"lang": language,
		"merchant_code": merchant_code,
		"merchant_urls": {
			"success": get_url(
				"/api/v2/method/tabby_frappe.tabby_frappe.doctype.tabby_payment_request.tabby_payment_request.tabby_merchant_success"
			),
			"cancel": get_tabby_settings().cancel_url,
			"failure": get_url(
				"/api/v2/method/tabby_frappe.tabby_frappe.doctype.tabby_payment_request.tabby_payment_request.tabby_merchant_failure"
			),
		},
	}
	response = requests.post(
		TABBY_API_BASE_URL + "api/v2/checkout", headers=get_headers(), json=payload
	)
	response_status = "Completed" if response.status_code == 200 else "Failed"

	create_request_log(
		data=payload,
		service_name="Tabby Checkout",
		output=response.json(),
		status=response_status,
		request_headers=response.headers,
	)
	# This is just a log can be removed
	frappe.get_doc(
		{
			"doctype": "Tabby Payment Log",
			"request_data": frappe.as_json(payload, indent=2),
			"response_data": frappe.as_json(response.json(), indent=2),
			"status": "Success" if response.status_code == 200 else "Error",
		}
	).insert(ignore_permissions=True)

	# Check the response
	if response.status_code == 200:
		checkout_data = response.json()
		doc = frappe.get_doc(
			{
				"doctype": "Tabby Payment Request",
				"reference_id": checkout_data["id"],
				"amount": checkout_data["payment"]["amount"],
				"status": "Pending",
				"tabby_payment_id": checkout_data["payment"]["id"],
				"quotation_id": quotation_id,
			}
		)
		doc.insert(ignore_permissions=True)
		return {
			"web_url": checkout_data["configuration"]["available_products"][
				"installments"
			][0]["web_url"]
		}
	else:
		frappe.throw(
			f"Tabby Payment Error: Cannot create payment request, Error: {response.text}"
		)


def tabby_process_success(payment_id: str):
	payment_request = frappe.get_doc(
		"Tabby Payment Request", {"tabby_payment_id": payment_id}
	)

	if payment_request.status != "Completed":
		# Check if the payment is already captured
		payment_response = requests.get(
			TABBY_API_BASE_URL + f"api/v2/payments/{payment_id}", headers=get_headers()
		)
		payment_response_json = payment_response.json()
		if (
			payment_response_json["status"] == "CLOSED"
			or payment_request.status == "Completed"
		):
			return
		
		# capture the payment
		url = TABBY_API_BASE_URL + f"api/v2/payments/{payment_id}/captures"
		payload = {"amount": payment_request.amount}
		response = requests.post(url, headers=get_headers(), json=payload)
		response_status = "Completed" if response.status_code == 200 else "Failed"
		create_request_log(
			data=payload,
			service_name="Tabby Integration Payment Capture",
			output=response.json(),
			status=response_status,
			request_headers=response.headers,
		)
		if response_status == "Completed":
			payment_request.status = "Completed"
			payment_request.save(ignore_permissions=True).submit()
		else:
			frappe.throw("Tabby payment error: Failed to capture payment")


@frappe.whitelist()
def tabby_merchant_success():
	payment_id = frappe.form_dict.get("payment_id")

	url = TABBY_API_BASE_URL + f"api/v2/payments/{payment_id}"
	response = requests.get(url, headers=get_headers())
	response_data = response.json()
	response_status = "Completed" if response.status_code == 200 else "Failed"
	create_request_log(
		data={},
		service_name="Tabby Integration Success",
		output=response.json(),
		status=response_status,
		request_headers=response.headers,
	)
	if response_data["status"] == "AUTHORIZED" or response_data["status"] == "CLOSED":
		tabby_process_success(payment_id)
		payment_request = frappe.get_doc(
			"Tabby Payment Request", {"tabby_payment_id": payment_id}
		)
		return werkzeug.utils.redirect(
			get_tabby_settings().success_url + payment_request.order_id
		)
	else:
		frappe.throw("Something went wrong.")


@frappe.whitelist()
def tabby_merchant_failure():
	payment_id = frappe.request.args.get("payment_id")
	payment_request = frappe.get_doc(
		"Tabby Payment Request", {"tabby_payment_id": payment_id}
	)
	payment_request.status = "Failure"
	payment_request.insert(ignore_permissions=True).submit()
	frappe.db.commit()
	return werkzeug.utils.redirect(get_tabby_settings().failure_url)


TABBY_WHITELISTED_IP_ADDRESSES = {
	"34.166.36.90",
	"34.166.35.211",
	"34.166.34.222",
	"34.166.37.207",
	"34.93.76.191",
}


@frappe.whitelist(allow_guest=True)
def process_tabby_webhook():
	request_ip = frappe.request.headers.get("X-Real-Ip")
	if request_ip not in TABBY_WHITELISTED_IP_ADDRESSES:
		frappe.throw("Unauthorized request.", 417)

	data = frappe.request.get_json()
	if data["status"] == "authorized":
		tabby_process_success(data["id"])

	return "ok"
