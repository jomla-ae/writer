odoo.define("writer.writer_product_edit", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var ckeditorLoader = require("@widget_ckeditor/js/loader");

  publicWidget.registry.WriterProductEditor = publicWidget.Widget.extend({
    selector: ".o_writer_product_editor_form",
    events: Object.assign({}, publicWidget.Widget.prototype.events, {
      'click [name="o_writer_submit_save_button"]': "_submitEditForm",
    }),
    start: async function () {
      const def = this._super.apply(this, arguments);
      if (this.editableMode) return def;

      ckeditorLoader.load({
        resModel: "product.template",
        resId: window.location.pathname.split("/").pop(),
      });

      return Promise.all([def]);
    },
    _submitEditForm: function (ev) {
      this.el.querySelector('input[name="submit_option"]').value = 1;
    },
  });

  return publicWidget.registry.WriterProductEditor;
});
