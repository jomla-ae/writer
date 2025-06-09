odoo.define("writer.WriterMany2manyTags",function (require) {
    "use strict";

    var PublicWidget = require("web.public.widget");

    var WriterMany2manyTags = PublicWidget.Widget.extend({
        selector: ".writer_field_many2many_tags",
        start: function () {
            $(".writer_field_many2many_tags").select2();
        }
});

PublicWidget.registry.WriterMany2manyTags = WriterMany2manyTags;

return WriterMany2manyTags;

});