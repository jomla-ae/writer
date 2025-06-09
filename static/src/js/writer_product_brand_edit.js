odoo.define("writer.writer_product_brand_edit", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var wysiwygLoader = require("web_editor.loader");

    publicWidget.registry.WriterProductBrandEditor = publicWidget.Widget.extend({
        selector: ".o_writer_product_brand_editor_form",
        events: Object.assign({}, publicWidget.Widget.prototype.events, {
            'click [name="o_writer_edit_product_brand_image"]': '_editImage',
            'click [name="o_writer_remove_product_brand_image"]': '_removeImage'
        }),
        start: async function () {
            var def = this._super.apply(this, arguments);
            if (this.editableMode) {
                return def;
            }

            var textarea_inputs = this.$("textarea.o_wysiwyg_loader");
            if(textarea_inputs.length > 0){
                for(let textarea_input of textarea_inputs){
                    this._wysiwyg = await wysiwygLoader.loadFromTextarea(this, textarea_input, {
                        recordInfo: {
                            context: this._getContext(),
                            res_model: "product.brand",
                            res_id: parseInt(this.$("input[name=" + textarea_input.name + "]").val()),
                        },
                        resizable: true,
                        userGeneratedContent: true,
                    });
                }

            }

            this.$("textarea").each(function () {
                $(this).val($(this).val().trim());
            });
            return Promise.all([def]);
        },
        _editImage: function(ev) {
            var input_image = document.getElementById("image");

            input_image.click();

            input_image.onchange = () => {
                var reader = new FileReader();

                reader.addEventListener("load", () => {
                      document.getElementById("product_brand_image").children[0].src = reader.result;
                      document.getElementById("edit_delete_image").value = "1";
                })

                reader.readAsDataURL(input_image.files[0]);
            };

            return false;
        },
        _removeImage: function(ev) {
            var product_brand_image = document.getElementById("product_brand_image");
            product_brand_image.children[0].src = "";
            document.getElementById("edit_delete_image").value = "2";

            return false;
        }
    });

    return publicWidget.registry.WriterProductBrandEditor;
});