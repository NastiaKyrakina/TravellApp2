
$(document).ready(function () {

    DelUncorrectSimvol('input[name=city],input[name=country]');
    TrimInput();
    TextAreaTrim();
    CorrectRegistr('input[name=city]');
    OnlyLatOrKir('input[name=city]');
    OnlyNumber('input[name=phone_num]');
    OnlyNumber('input[name=birthday]', '.');
    DateView('input[name=birthday]');
    load_countrues('2');


    $("input#id_country").on('change', function () {

        id_country = GetIdCountry();
        if (id_country === undefined && $(this).val().length > 0) {
            $(this).addClass('UncorrectValue');
            $(".js-country-error").removeAttr('hidden');
        }
        else {
            $(this).removeClass('UncorrectValue');
            let code = $('option#' + id_country).attr('code');
            $(".js-country-error").attr('hidden', true);
            $('#phone-code').text(code);
        }

    });

    $('.info-form').submit(function (e) {

        id_country = GetIdCountry();
        if (id_country == undefined) {
            console.log('1');
            e.preventDefault();
            return false;
        } else {
            console.log('2');
            let date = $('input[name=birthday]').val().split('.');

            if (!is_valid_date(date) || !in_diapazone(date)) {
                console.log('3');
                e.preventDefault();
                return false;
            }
        }


        $("input#id_country").val(id_country);
            code = $('#phone-code').text();
            return;
    });

});
