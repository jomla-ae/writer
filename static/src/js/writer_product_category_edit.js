odoo.define("writer.writer_product_category_edit", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var wysiwygLoader = require("web_editor.loader");

    publicWidget.registry.WriterProductCategoryEditor = publicWidget.Widget.extend({
        selector: ".o_writer_product_category_editor_form",
        events: Object.assign({}, publicWidget.Widget.prototype.events, {
            'click [name="o_writer_edit_product_category_image"]': '_editImage',
            'click [name="o_writer_remove_product_category_image"]': '_removeImage',
            'click [id="add_faq"]': '_addFaq',
            'click [id="remove_faq"]': '_removeFaq',
            'click [name="o_writer_submit_save_button"]': '_submitEditForm'
        }),
        start: async function () {
            var def = this._super.apply(this, arguments);
            if (this.editableMode) {
                return def;
            }

            this.last_number_add_faq= 0;
            this.delete_faqs = [];
            var textarea_inputs = this.$("textarea.o_wysiwyg_loader");
            if(textarea_inputs.length > 0){
                for(let textarea_input of textarea_inputs){
                    this._wysiwyg = await wysiwygLoader.loadFromTextarea(this, textarea_input, {
                        recordInfo: {
                            context: this._getContext(),
                            res_model: "product.category",
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
                      document.getElementById("product_category_image").children[0].src = reader.result;
                      document.getElementById("edit_delete_image").value = "1";
                })

                reader.readAsDataURL(input_image.files[0]);
            };

            return false;
        },
        _removeImage: function(ev) {
            var product_category_image = document.getElementById("product_category_image");
            product_category_image.children[0].src = "";
            document.getElementById("edit_delete_image").value = "2";

            return false;
        },
        _submitEditForm: function (ev) {
            this.el.querySelector('input[name="submit_option"]').value = 1;
        },
        _addFaq: function(ev) {
            this.last_number_add_faq += 1;
            const tr_faq = document.getElementById("add_tr_faq");
            const new_tr_faq = tr_faq.cloneNode(true);
            new_tr_faq.style = "";
            new_tr_faq.id = "tr_faq";
            const new_tds_faq = new_tr_faq.children;

            new_tds_faq[0].children[0].id = "add_faq_quotation_" + this.last_number_add_faq;
            new_tds_faq[0].children[0].name = "add_faq_quotation_" + this.last_number_add_faq;
            new_tds_faq[1].children[0].id = "add_faq_quotation_arabic_" + this.last_number_add_faq;
            new_tds_faq[1].children[0].name = "add_faq_quotation_arabic_" + this.last_number_add_faq;

            new_tds_faq[2].children[0].id = "add_faq_answer_" + this.last_number_add_faq;
            new_tds_faq[2].children[0].name = "add_faq_answer_" + this.last_number_add_faq;
            new_tds_faq[3].children[0].id = "add_faq_answer_arabic_" + this.last_number_add_faq;
            new_tds_faq[3].children[0].name = "add_faq_answer_arabic_" + this.last_number_add_faq;

            new_tds_faq[4].children[0].setAttribute("faq_id","new");
            tr_faq.before(new_tr_faq);


        },
        _removeFaq: function(ev) {
            const faq_id = ev.target.getAttribute("faq_id");
            if(faq_id !== "new"){
                this.delete_faqs.push(faq_id);
                this.el.querySelector('input[name="delete_faqs"]').value =  JSON.stringify(this.delete_faqs);
            }

            ev.target.parentElement.parentElement.remove();
        }
    });

    return publicWidget.registry.WriterProductCategoryEditor;
});