# Copyright (c) 2025, cinnamonlabs.io and Contributors
# See license.txt

# import frappe
from frappe.tests.utils import FrappeTestCase
from tabby_frappe.tabby_frappe.doctype.tabby_payment_request.tabby_payment_request import initiate_checkout,tabby_merchant_success
import frappe
from unittest.mock import patch, MagicMock
from frappe.utils import set_request


class TestTabbyPaymentRequest(FrappeTestCase):
	@property
	def buyer(self):
		return {
            "phone": "500000001", 
            "email": "card.success@tabby.ai", 
            "name": "string", 
            "dob": "2019-08-24" 
        }
	
	def test_initiate_checkout(self):
		test_amount = 200
		
		response = initiate_checkout(amount=test_amount,buyer=self.buyer)

		self.assertIn("payment", response)
		self.assertIn("status", response)

		# request doc created behind the scenes
		request_doc_exists = frappe.db.exists(
			"Tabby Payment Request", {"tabby_payment_id": response["payment"]["id"]}
		)
		self.assertTrue(request_doc_exists)

		# status should be pending
		order_doc = frappe.get_doc(
			"Tabby Payment Request", {"tabby_payment_id": response["payment"]["id"]}
		)
		self.assertEqual(order_doc.status, "Pending")
		self.assertEqual(order_doc.amount, test_amount)
	def test_tabby_merchant_success(self):

		response = initiate_checkout(amount=200,buyer=self.buyer)

		payment_id = response["payment"]["id"]
		print("this is id",payment_id)
		query_string= f"?payment_id={payment_id}"
		set_request(method="GET", query_string=query_string)
		tabby_merchant_success()


		doc = frappe.get_doc("Tabby Payment Request", {"tabby_payment_id": payment_id})
		self.assertEqual(doc.status, "Complete")