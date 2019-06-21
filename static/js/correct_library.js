function GetIdCountry() {

    const inp = $("input#id_country").val();
    let opt = $(`#countries option[value='${inp}']`);
    console.log(opt.attr('id'));
    return opt.attr('id');
}

function TrimInput() {

    $('input[type=text]').on('input', function () {
        var text = $(this).val();
        text = text.replace(/^\s*/g, "");
        text = text.replace(/^-*/g, "");
        text = text.replace(/^ʼ*/g, "");
        $(this).val(text.replace(/\s+/g, " "));

    });

    $('input[type=text]').on('change', function () {
        $(this).val($(this).val().trim());
    });


}

function TextAreaTrim() {
    $('textarea').on('input', function () {
        var text = $(this).val();
        text = text.replace(/^ */g, "");
        $(this).val(text.replace(/ +/g, " "));

    });
}

function TextAreaCountChar() {
    $('textarea').on('input', function () {
        var count = $(this).val().length;
        if (count <= 100) {
            $(".sucs-show").hide();
            $(".character-counter").show();
            $('#counter').text(100 - count);
        } else {
            $('.js-about-error').attr('hidden', true);
            $(".character-counter").hide();
            $(".sucs-show").show();
        }

    });
}


function FirstSimvolToUpper(input_selector) {
    $(input_selector).on('input', function (e) {
        var text = $(this).val();
        $(this).val(text.charAt(0).toUpperCase() + text.slice(1));
    });
}

function CorrectRegistr(input_selector) {

    $(input_selector).on('input', function (e) {

        var text = $(this).val();
        var text_list = text.toLowerCase().split(/[\s`ʼ-]+/);
        for (let i = 0; i < text_list.length; i++) {
            text_list[i] = text_list[i].charAt(0).toUpperCase() + text_list[i].slice(1);
        }

        let k = 1;
        var new_text = text_list[0];
        for (let i = 0; i < text.length && k < text_list.length; i++) {
            let char = text.charAt(i);
            if (char.search(/[\s`ʼ-]+/) > -1) {
                new_text += char + text_list[k];
                k = k + 1;
            }
        }
        $(this).val(new_text);
    });
}

function DelUncorrectSimvol(input_selector, other_simvol = '') {

    $(input_selector).on('keydown', function (e) {

        key = e.key;
        // спец. сочетание - не обрабатываем
        if (e.ctrlKey || e.altKey || e.metaKey || key === 'Backspace' || key === 'Enter') return;

        key = e.key;
        if (!key) return;
        reg = new RegExp('[\\sA-Za-zА-Яа-яіІєЄйЙїЇЁё`ʼ' + other_simvol + '-]+');
        if (key.search(reg) === -1) return false;

    });
}

function OnlyLatOrKir(input_selector) {

    let correct = true;
    $(input_selector).on('change', function (e) {

        var lat;
        var kir;
        text = $(this).val();
        lat = text.search(/[A-Za-z]+/);
        kir = text.search(/[А-Яа-яіІєЄйЙїЇ]+/);

        if (lat !== -1 && kir !== -1) {
            correct = false;
            $('.js-city-error').attr('hidden', false);
        } else {
            $('.js-city-error').attr('hidden', true);
        }


    });

    return correct;
}

function OnlyLat(input_selector) {

    let correct = true;
    $(input_selector).on('change', function (e) {

        var lat;

        text = $(this).val();
        lat = text.search(/[A-Za-z]+/);

        if (lat !== -1) {
            correct = false;
            $('.js-email-error').attr('hidden', false);
        } else {
            $('.js-email-error').attr('hidden', true);
        }
    });
    return correct;
}


function get_selected_type() {
    let type = $('#id_type option:selected').attr('value');
    return type;
}


function AddressValidation() {
    let error;
    $("input[name=address]").on('change', function (e) {
        error = false;

        text = $(this).val();
        text_arr = text.split(',');

        if (text_arr.length > 3 || text_arr.length < 2) {
            error = true;
        } else {

            if (text_arr[0].length == 0) {
                error = true;
            } else {
                text_arr[0].trim();
                reg = new RegExp('^[0-9A-Za-zА-Яа-яЇїІієЄЁё]+[\0-9A-Za-zА-Яа-яЇїІієЄЁё`ʼ-]*$');

                if (reg.test(text_arr[0]) && text_arr[0].search(/[A-Za-zА-Яа-яіІєЄйЙїЇ]/) == -1) {
                    error = true;
                }

            }
            if (text_arr[1].length == 0) {
                error = true;
            } else {
                text_arr[1].trim();
                reg = new RegExp('[0-9]{1,4}-*[0-9A-Za-zА-Яа-яЇїІієЄЁё]');

                if (!reg.test(text_arr[1])) {
                    error = true;
                }
            }
            if (get_selected_type() === 'AP' && !text_arr[2]) {
                error = true;
            } else {
                if (text_arr[2]) {
                    text_arr[2].trim();
                    reg = new RegExp('[0-9]{1,4}-*[0-9A-Za-zА-Яа-яЇїІієЄЁё]');

                    if (!reg.test(text_arr[2])) {
                        error = true;
                    }
                }

            }
        }

        if (error) {
            $('.js-address-error').attr('hidden', false);
            $('#address-pattern').text($(this).attr('title'));
        } else {
            $('.js-address-error').attr('hidden', true);
        }

    });
}


function AddresTitle() {
    var address_input = $('#id_address');

    $('#id_type').on('click', function () {

        let type = get_selected_type();

        if (type == 'AP') {
            address_input.attr('title', address_input.attr('full_title'));
        } else {
            address_input.attr('title', address_input.attr('short_title'));
        }

    });

}

function OnlyNumber(input_selector, other_simvol = '') {
    $(input_selector).on('keydown', function (e) {

        key = e.key;

        // спец. сочетание - не обрабатываем
        if (e.ctrlKey || e.altKey || e.metaKey || key === 'Backspace' || key === 'Enter') return;

        key = e.key;
        if (!key) return;
        reg = new RegExp('[0-9' + other_simvol + ']');
        if (key.search(reg) === -1) return false;

    });
}


function is_valid_date(arr) {
    let arrD = arr;
    var d = new Date(arrD[2], (arrD[1] - 1), arrD[0]);

    if ((d.getFullYear() == arrD[2]) && (d.getMonth() == (arrD[1] - 1)) && (d.getDate() == arrD[0])) {
        return true;
    } else {
        return false;
    }
}

function in_diapazone(arrD) {
    let date = new Date(arrD[2], (arrD[1] - 1), arrD[0]);
    let max = new Date();
    let min = new Date(1900, 0, 1);
    if (date < max && date > min) {

        return true;
    }
    return false;
}

function DateView(input_selector) {
    $(input_selector).on('change', function (e) {

        var arr = $(this).val().split('.');
        if (is_valid_date(arr)) {
            $('.js-birth-error').attr('hidden', true);
            let full_date = "";
            for (let i = 0; i < arr.length; i++) {
                if (arr[i].length < 2 && +arr[i] < 10) {
                    full_date += '0' + arr[i];
                } else {
                    full_date += arr[i];
                }
                if (i + 1 < arr.length) full_date += '.'
            }
            $(this).val(full_date);

            if (in_diapazone(arr)) {
                $('.js-birth-error-diap').attr('hidden', true);
            } else {
                $('.js-birth-error-diap').attr('hidden', false);
            }

        } else {
            $('.js-birth-error').attr('hidden', false);

        }
    });

}