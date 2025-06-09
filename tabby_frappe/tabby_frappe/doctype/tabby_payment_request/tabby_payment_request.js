frappe.ui.form.on("Tabby Payment Request", {
	refresh(frm) {
		if (frm.doc.status === "CLOSED" || frm.doc.status === "PARTIAL REFUND") {
			frm.add_custom_button(__("Refund"), () => {
				frappe.confirm(__("Are you sure you want to refund in full?"), () => {
					frm.call("refund").then(() => {
						frappe.show_alert(__("Refund Processed"));
						frm.refresh();
					});
				});
			});
		}
		const btn = frm.add_custom_button(__("Sync Status"), () => {
			frm
				.call({
					method: "sync_status",
					doc: frm.doc,
					btn,
				})
				.then(() => {
					frappe.show_alert(__("Status synced!"));
					frm.refresh();
				});
		});
		if (frm.doc.status === "AUTHORIZED") {
			const capture_btn = frm.add_custom_button(__("Capture Payment"), () => {
				frm
					.call({
						method: "capture_payment",
						doc: frm.doc,
						capture_btn,
					})
					.then(() => {
						frappe.show_alert(__("Payment captured!"));
						frm.refresh();
					});
			});
		}
	},
});
