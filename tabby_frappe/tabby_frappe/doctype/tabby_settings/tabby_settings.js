// Copyright (c) 2025, cinnamonlabs.io and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tabby Settings", {
    refresh(frm) {
        frm.add_custom_button(_("Register Webhook"), () => {
            let d = new frappe.ui.Dialog({
                title: _("Register Webhook"),
                fields: [
                    {
                        label: "Base URL",
                        fieldname: "base_url",
                        fieldtype: "Data",
                        reqd: 1,
                        default : `https://${frappe.boot.sitename}`
                    },
                    {
                        label: _("Is Production Webhook?"),
                        fieldname: _("is_production"),
                        fieldtype: "Check"
                    }
                ],
                primary_action_label: _("Register"),
                primary_action(values) {
                    frappe.confirm(_("Are you sure you want to add this webhook?"), () => {
                        frm.call("register_webhook", { 
                            site_url: values.base_url, 
                            is_production: values.is_production 
                        }).then(({ message }) => {
                            if (message !== "failed") {
                                frappe.show_alert(_("Webhook Added"));
                                frm.refresh();
                            }
                        });
                        d.hide();  // Close the dialog
                    });
                }
            });

            d.show();
        });
    },
});
