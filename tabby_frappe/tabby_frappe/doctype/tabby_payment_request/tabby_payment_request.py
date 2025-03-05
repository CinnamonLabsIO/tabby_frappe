# Copyright (c) 2025, cinnamonlabs.io and contributors
# For license information, please see license.txt


from frappe.model.document import Document
import frappe
from frappe.integrations.utils import create_request_log
import requests
from werkzeug.wrappers import Response
import werkzeug.utils
from frappe.utils import get_url

class TabbyPaymentRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from tabby_frappe.tabby_frappe.doctype.tabby_monthly_installments.tabby_monthly_installments import TabbyMonthlyInstallments

		amended_from: DF.Link | None
		amount: DF.Currency
		down_payment: DF.Currency
		monthly_installments: DF.Table[TabbyMonthlyInstallments]
		payment_url: DF.Data | None
		reference_id: DF.Data
		status: DF.Literal["Pending", "Completed", "Faliure", "Refund"]
		tabby_payment_id: DF.Data
	# end: auto-generated types
	pass
	@property
	def is_complete(self):
		return self.status == "Completed"
	
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
	@property
	def base_url(self):
		return 'https://api.tabby.ai/'

	@frappe.whitelist()
	def refund(self):
		frappe.only_for("System Manager")

		if not self.is_complete:
			frappe.throw("Refunds Can be Made Only on Complete Payments!")
		url = self.base_url + f"api/v2/payments/{self.tabby_payment_id}/refunds"
		response = requests.post(url,headers=self.headers,json={"amount":self.amount})
		status = "Completed" if response.status_code ==200 else "Failed"
		create_request_log(data={"payment_id":self.tabby_payment_id,"amount":self.amount},service_name="Tabby Refund",output=response.json(),status=status,request_headers=response.headers)
		if status=="Completed":
			self.status="Refund"
			self.save()
			return "refund successful"
		else:
			frappe.throw("Could not process refund, please try again later.")

tabby_settings = frappe.get_doc('Tabby Settings')
key_secret = tabby_settings.get_password("key_secret")
base_url = 'https://api.tabby.ai/'
headers =  {
    'Authorization': f'Bearer {key_secret}',
    'Content-Type': 'application/json'
}
@frappe.whitelist(allow_guest=True)
def initiate_checkout(amount:int,currency: str= "SAR",description:str = "",language:str="en",merchant_code:str="",buyer=""):
	tabby_settings = frappe.get_doc('Tabby Settings')
	payload = {
		"payment":{
			"amount":amount,
			"currency":currency,
			"description":description,
			  "buyer": buyer
		
					},
						"lang":language,
			"merchant_code":merchant_code,
				"merchant_urls": {
				"success": get_url("/api/v2/method/tabby_frappe.tabby_frappe.doctype.tabby_payment_request.tabby_payment_request.tabby_merchant_success"),
				"cancel": tabby_settings.cancel_url,
				"failure":get_url("/api/v2/method/tabby_frappe.tabby_frappe.doctype.tabby_payment_request.tabby_payment_request.tabby_merchant_failure")
			}
				}
	response = requests.post(base_url+"api/v2/checkout", headers=headers, json=payload)

	response_status  = "Completed" if response.status_code ==200 else "Failed"

	create_request_log(data=payload,service_name="Tabby Checkout",output=response.json(),status=response_status,request_headers=response.headers)
	# This is just a log can be removed
	frappe.get_doc({
	"doctype":"Tabby Payment Log",
	"request_data":frappe.as_json(payload,indent=2),
	"response_data": frappe.as_json(response.json(),indent=2),
	"status": "Success" if response.status_code ==200 else "Error"
}).insert(ignore_permissions = True)
	frappe.db.commit()


	# Check the response
	if response.status_code == 200:
		checkout_data = response.json()
		doc =frappe.get_doc({
			"doctype":"Tabby Payment Request",
			"reference_id":checkout_data["id"],
			"amount":checkout_data["payment"]["amount"],
			"status":"Pending",
			"tabby_payment_id":checkout_data["payment"]["id"],

		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		return(checkout_data)
	else:
		frappe.throw(f"Tabby Payment Error: Cannot create payment request, Error: {response.text}")


def tabby_process_success(payment_id):


		payment_request = frappe.get_doc("Tabby Payment Request",{'tabby_payment_id' :payment_id})
        
		if payment_request.status != "Completed":
			# Check if the payment is already captured
			payment_response = requests.get(base_url+f"api/v2/payments/{payment_id}",headers=headers)
			payment_response_json = payment_response.json()
			if payment_response_json["status"] =="CLOSED" or payment_request.status == "Completed":
				return
            # capture the payment
			url = base_url + f"api/v2/payments/{payment_id}/captures"
			payload ={"amount":payment_request.amount}
			response = requests.post(url,headers=headers,json=payload)
			response_status  = "Completed" if response.status_code ==200 else "Failed"
			create_request_log(data=payload,service_name="Tabby Integration Payment Capture",output=response.json(),status=response_status,request_headers=response.headers)
			if response_status == "Completed":
				# Process bills in erp
				payment_request.status = "Completed"

				payment_request.save(ignore_permissions=True).submit()

				frappe.db.commit()
			else :
				frappe.throw("Tabby payment error: Failed to capture payment")



@frappe.whitelist(allow_guest=True)
def tabby_merchant_success():
	payment_id = frappe.request.args.get("payment_id")

	url = base_url + f"api/v2/payments/{payment_id}"
	response = requests.get(url,headers=headers)
	response_json = response.json()
	response_status  = "Completed" if response.status_code ==200 else "Failed"
	create_request_log(data={},service_name="Tabby Integration Success",output=response.json(),status=response_status,request_headers=response.headers)
	if(response_json["status"]=="AUTHORIZED" or response_json["status"]=="CLOSED"):

		tabby_process_success(payment_id)
		return werkzeug.utils.redirect(tabby_settings.success_url)


	else:
		frappe.throw("Something went wrong.")

@frappe.whitelist(allow_guest=True)
def tabby_merchant_failure():
	payment_id = frappe.request.args.get("payment_id")
	payment_request = frappe.get_doc("Tabby Payment Request",{'tabby_payment_id' :payment_id})
	payment_request.status = "Failure"
	payment_request.insert(ignore_permissions=True).submit()
	frappe.db.commit()
	return werkzeug.utils.redirect(tabby_settings.success_url)




@frappe.whitelist(allow_guest=True)
def process_tabby_webhook():
	# Todo :Verfiy the webhook

	data = frappe.request.get_json()
	if data["status"] == "authorized":
		tabby_process_success(data["id"])  
	
	return Response(status=200)


