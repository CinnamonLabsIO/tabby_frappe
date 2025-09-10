# Tabby Frappe

A plug-and-play Frappe app for seamless integration with Tabby's Buy Now, Pay Later (BNPL) payment gateway. 


<img width="2866" height="2690" alt="tabby_frappe" src="https://github.com/user-attachments/assets/80c9dd75-57e5-4a44-9166-132e17a68a45" />



## 🚀 Quick Start

### Prerequisites
- Frappe Framework (v14+)
- ERPNext
- Valid Tabby Merchant Account

### Installation

1. **Install the app:**
```bash
bench get-app tabby_frappe https://github.com/CinnamonLabsIO/tabby_frappe.git
bench install-app tabby_frappe --site your-site-name
```


## ⚙️ Configuration

### 1. Tabby Payment Gateway Setup

<img width="2866" height="1450" alt="tabby_frappe_settings" src="https://github.com/user-attachments/assets/e15fcccd-ceb6-4748-b24c-cdb805697900" />


Navigate to: `Desk > Tabby Settings` and fill in details:

```

Tabby Keys
- Key ID: [Your Tabby Public Key]
- Key Secred: [Your Tabby Secret Key]
Merchant URLs
- Success URL: [Your website success URL]
- Failure URL: [Your website failure URL]
- Cancel URL: [Your website cancel URL]

```


### Basic Implementation

Create Tabby Payment Request

```python

payment_request = frappe.get_doc(
			{
				"doctype": "Tabby Payment Request",
				"amount": "amount",
				"currency_code": "currency_code",
				"ref_doctype": "ref_doctype",
				"ref_docname": "ref_docname",
				"customer_ref": "customer_ref",
				"customer_phone": "customer_phone",
				"customer_name": "customer_name",
				"customer_email": "customer_email",
				"customer_address": "customer_address",
			}
		).insert()

```



### Documentation
- [Tabby Developer Docs](https://docs.tabby.ai/)
- [Frappe Framework Docs](https://frappeframework.com/docs)

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/yourusername/tabby_frappe/issues)
- **Email**: developers@buildwithhussain.com
- **Community**: [Frappe Community Forum](https://discuss.frappe.io/)

### Commercial Support
Professional support and customization available through BWH Studios.

## 🏢 About

Developed by **BWH Studios**

**BWH Studios** is based in Jagdalpur, Chhattisgarh, India, and provides:



⭐ If Tabby Frappe helps your business, please star the repository!

#### License

mit
