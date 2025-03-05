// Copyright (c) 2025, cinnamonlabs.io and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Tabby Payment Request", {
// 	refresh(frm) {

// 	},
// });
// Todo: Update refund date in doctype
frappe.ui.form.on("Tabby Payment Request", {
	refresh(frm) {
		if (frm.doc.status === "Completed") {
			frm.add_custom_button("Refund", () => {
     
                frappe.confirm("Are you sure you want to refund in full?", () => {
					frm.call("refund").then(({ message }) => {
						if (message != "failed") {
							frappe.show_alert("Refund Processed");
							frm.refresh();
						}
					});
				});
			}).addClass("btn-primary");;
		}
	},
});