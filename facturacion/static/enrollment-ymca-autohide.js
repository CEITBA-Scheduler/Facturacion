(function ($) {
    $(function () {
        var serviceField = $('#id_service'),
            chargeMedicalExam = $('.field-add_ymca_medical_exam');

        function toggleVerified(value) {
            value == 'YMCA' ? chargeMedicalExam.show() : chargeMedicalExam.hide();
        }

        // show/hide on load based on pervious value of selectField
        toggleVerified(serviceField.val());

        // show/hide on change
        serviceField.change(function () {
            toggleVerified($(this).find('option:selected').text());
        });
    });
})(django.jQuery);