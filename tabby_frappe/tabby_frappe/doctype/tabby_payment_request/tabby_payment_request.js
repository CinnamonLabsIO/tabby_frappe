// Copyright (c) 2025, cinnamonlabs.io and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Tabby Payment Request", {
// 	refresh(frm) {

// 	},
// });
// Todo: Update refund date in doctype
frappe.ui.form.on("Tabby Payment Request", {
	refresh(frm) {
		if (frm.doc.status === "CLOSED") {
			frm.add_custom_button(_('Refund'), () => {
     
                frappe.confirm("Are you sure you want to refund in full?", () => {
					frm.call("refund").then(({ message }) => {
						if (message != "failed") {
							frappe.show_alert(_("Refund Processed"));
							frm.refresh();
						}
					});
				});
			})
		}
		const btn = frm.add_custom_button(__('Sync Status'), () => {
			frm
				.call({
					method: 'sync_status',
					doc: frm.doc,
					btn,
				})
				.then(() => {
					frappe.show_alert(__('Status synced!'));
					frm.refresh();
				});
		});
		if (frm.doc.status === "AUTHORIZED") {
		const capture_btn = frm.add_custom_button(__('Capture Payment'), () => {
			frm
				.call({
					method: 'capture_payment',
					doc: frm.doc,
					capture_btn,
				})
				.then(() => {
					frappe.show_alert(__('Payment captured!'));
					frm.refresh();
				});
		});
	}
	},
});