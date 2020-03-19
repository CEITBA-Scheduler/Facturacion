(function ($) {
    $(function () {
        var typeField = $('#id_type');
        var addCeitbaEnrollmentField = $('#id_add_ceitba_enrollment');
        var autoBillField = $('.field-auto_bill');

        function toggleVerified(value) {
            value == 'Personal' ? autoBillField.show() : autoBillField.hide();
        }

        // show/hide on load based on pervious value of selectField
        toggleVerified(typeField.val());

        // show/hide on change
        typeField.change(function () {
            toggleVerified($(this).find('option:selected').text());
        });

        // show/hide on change
        addCeitbaEnrollmentField.change(function () {
            if (this.checked) {
                autoBillField.show()
            } else {
                autoBillField.hide()
            }
        });
    });
})(django.jQuery);