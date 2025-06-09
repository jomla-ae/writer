// odoo.define("writer.writer_product_edit", function (require) {
//   "use strict";

//   var publicWidget = require("web.public.widget");
//   var ckeditorLoader = require("@widget_ckeditor/js/loader");

//   publicWidget.registry.WriterProductEditor = publicWidget.Widget.extend({
//     selector: ".o_writer_product_editor_form",
//     events: Object.assign({}, publicWidget.Widget.prototype.events, {
//       'click [name="o_writer_submit_save_button"]': "_submitEditForm",
//       'click [name="image_type"]': "_UpdateProductImageType",
//       'click [name="o_writer_add_product_image"]': "_addProductImage",
//       'click [name="o_writer_edit_product_image"]': "_editProductImage",
//       'click [name="o_writer_remove_product_image"]': "_removeProductImage",
//     }),
//     start: async function () {
//       var def = this._super.apply(this, arguments);
//       if (this.editableMode) {
//         return def;
//       }

//       this.last_number_add_image = 0;
//       this.delete_image_product_ids = [];
//       this.update_product_image_types = {};

//       ckeditorLoader.load({
//         resModel: "product.template",
//         resId: window.location.pathname.split("/").pop(),
//       });

//       return Promise.all([def]);
//     },
//     _UpdateProductImageType: function (ev) {
//       const product_image = document.getElementsByClassName("carousel-item active")[0];

//       if (product_image.getAttribute("model") != "product.template") {
//         const image_type = document.getElementById("image_type").value;
//         this.update_product_image_types[product_image.id] = image_type;
//         this.el.querySelector('input[name="update_product_image_types"]').value = JSON.stringify(
//           this.update_product_image_types
//         );

//         const div_image_type = product_image.children[0];
//         if (image_type == "gallery") {
//           div_image_type.children[0].style.display = "";
//           div_image_type.children[1].style.display = "none";
//         } else if (image_type == "banner") {
//           div_image_type.children[1].style.display = "";
//           div_image_type.children[0].style.display = "none";
//         }
//       }
//     },
//     _addProductImage: function (ev) {
//       this.last_number_add_image += 1;
//       var product_image_id = "add_product_image_" + this.last_number_add_image;
//       var input_file = document.createElement("input");
//       input_file.name = product_image_id;
//       input_file.id = product_image_id;
//       input_file.type = "file";
//       input_file.accept = "image/*";
//       input_file.style = "display:none;";
//       document.querySelector('input[name="delete_image_ids"]').before(input_file);

//       input_file.click();

//       input_file.onchange = () => {
//         var reader = new FileReader();

//         reader.addEventListener("load", () => {
//           const product_image_element = document.getElementById("add_product_image_0");
//           const new_product_image = product_image_element.cloneNode(true);
//           new_product_image.id = product_image_id;
//           new_product_image.setAttribute("class", "carousel-item h-100");
//           new_product_image.style = "min-height: 400px;";

//           // default current image type for new image
//           const image_type = document.getElementById("image_type").value;
//           new_product_image.setAttribute("image_type", image_type);
//           this.update_product_image_types[product_image_id] = image_type;
//           this.el.querySelector('input[name="update_product_image_types"]').value = JSON.stringify(
//             this.update_product_image_types
//           );

//           const div_image_type = new_product_image.children[0];
//           if (image_type == "gallery") {
//             div_image_type.children[0].style.display = "";
//           } else if (image_type == "banner") {
//             div_image_type.children[1].style.display = "";
//           }

//           new_product_image.children[1].children[0].src = reader.result;
//           product_image_element.before(new_product_image);

//           const images_count = document.getElementsByClassName("carousel-item").length;
//           if (images_count > 1) {
//             const carousel_next_element = document.getElementById("carousel_next");
//             document.getElementById("carousel_prev").style = "color: black;";
//             carousel_next_element.style = "color: black;";
//             document.getElementById("edit_delete_image_product").style = "";
//           }
//         });

//         reader.readAsDataURL(input_file.files[0]);
//       };

//       return false;
//     },
//     _editProductImage: function (ev) {
//       const product_image = document.getElementsByClassName("carousel-item active")[0];
//       const product_image_id = product_image.getAttribute("id");
//       const model = product_image.getAttribute("model");
//       var input_file = false;

//       if (model != "no_model") {
//         var input_id = ((model == "product.template" && "edit_product_") || "edit_image_") + product_image_id;
//         const input_files = document.querySelectorAll(`input[id="${input_id}"]`);

//         if (input_files.length > 0) {
//           input_file = input_files[0];
//         } else {
//           var input_file = document.createElement("input");
//           input_file.name = input_id;
//           input_file.id = input_id;
//           input_file.setAttribute("model", model);
//           input_file.type = "file";
//           input_file.accept = "image/*";
//           input_file.style = "display:none;";
//           document.querySelector('input[name="delete_image_ids"]').before(input_file);
//         }
//       } else {
//         const input_files = document.querySelectorAll(`input[id="${product_image_id}"]`);
//         if (input_files.length > 0) {
//           input_file = input_files[0];
//         } else {
//           var input_file = document.createElement("input");
//           input_file.name = input_id;
//           input_file.id = input_id;
//           input_file.type = "file";
//           input_file.accept = "image/*";
//           input_file.style = "display:none;";
//           document.querySelector('input[name="delete_image_ids"]').before(input_file);
//         }
//       }

//       input_file.click();

//       input_file.onchange = () => {
//         var reader = new FileReader();

//         reader.addEventListener("load", () => {
//           if (model == "product.template") {
//             product_image.children[0].children[0].src = reader.result;
//           } else {
//             product_image.children[1].children[0].src = reader.result;
//           }
//         });

//         reader.readAsDataURL(input_file.files[0]);
//       };

//       return false;
//     },
//     _removeProductImage: function (ev) {
//       const product_image = document.getElementsByClassName("carousel-item active")[0];
//       const product_image_id = product_image.getAttribute("id");
//       const model = product_image.getAttribute("model");

//       if (model != "no_model") {
//         var input_id = ((model == "product.template" && "edit_product_") || "edit_image_") + product_image_id;
//         const input_files = document.querySelectorAll(`input[id="${input_id}"]`);
//         if (input_files.length > 0) {
//           input_files[0].remove();
//         }

//         this.delete_image_product_ids.push({
//           id: product_image_id,
//           model: model,
//         });

//         this.el.querySelector('input[name="delete_image_ids"]').value = JSON.stringify(this.delete_image_product_ids);
//       } else {
//         const input_files = document.querySelectorAll(`input[id="${product_image_id}"]`);
//         if (input_files.length > 0) {
//           input_files[0].remove();
//         }
//       }

//       delete this.update_product_image_types[product_image.id];
//       this.el.querySelector('input[name="update_product_image_types"]').value = JSON.stringify(
//         this.update_product_image_types
//       );

//       document.getElementById("carousel_next").click();
//       product_image.remove();

//       const images_count = document.getElementsByClassName("carousel-item").length;
//       if (images_count <= 1) {
//         document.getElementById("carousel_prev").style = "color: black;display:none;";
//         document.getElementById("carousel_next").style = "color: black;display:none;";

//         if (images_count == 0) {
//           document.getElementById("edit_delete_image_product").style = "display:none;";
//         }
//       }

//       return false;
//     },
//     _submitEditForm: function (ev) {
//       this.el.querySelector('input[name="submit_option"]').value = 1;
//     },
//   });

//   return publicWidget.registry.WriterProductEditor;
// });
