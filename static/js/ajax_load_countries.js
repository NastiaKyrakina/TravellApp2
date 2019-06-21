function GetIdCountry() {
    const inp = $("input#id_country").val();
    let opt = $("#countries option[value='" + inp + "']");
    return opt.attr('id');
}


function set_country(status = '1') {
    let country;
    let country_id = $("input#id_country").val();
    if (country_id) {
        country_option = $("#countries option[id=" + country_id + "]");
        country = country_option.val();
        $("input#id_country").val(country);
        if (status == '2' && country_option.attr('code')) {
            $('#phone-code').text(country_option.attr('code'));
        }
    }
}



function load_countrues(status = '1') {

    dataList = $("#countries");

    $.ajax({
        type: 'GET',
        async: true,
        url: '/load_countries/',
        data: "qc=" + status,
        success: function (data) {

            for (let i in data['dict']) {

                let option = document.createElement('option');
                option.value = data['dict'][i]['name'];
                option.id = data['dict'][i]['value'];
                if (status == '2') {
                    option.setAttribute('code', data['dict'][i]['phone_code']);

                }
                dataList.append(option);
            }
            set_country('2');
        },
        dataType: 'json',
    });
}