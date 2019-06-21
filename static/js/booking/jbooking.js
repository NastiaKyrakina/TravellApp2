;

function BookingSend(house_id) {
    $('#booking-add').on('submit', '#booking-form', function (e) {
        //відміняємо стандартну відправку форми
        e.preventDefault();
        //отримання даних форми
        var forms_1 = new FormData($(this).get(0));
        forms_1.append('house', house_id);
        console.log(forms_1.get('people'));


        //відправляємо дані
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            contentType: false,
            processData: false,
            data: forms_1,
            success: function (data) {

                if (typeof (data) === "object") {
                    alert(data);

                } else {
                    //додавання нового поста
                    $('.rate-block').prepend(data);
                    //очщення форми
                    $('.booking-form')[0].reset();

                }
            }


        });

        return false;
    });
}

function LoadBookingForm() {
    $('.open-book-form').on('click', () => {

        var house_primary_key = $('[id^=house-element-]').attr('id').split('-')[2];
        $('#booking-add').load('/house/booking/create/' + house_primary_key, function () {
            BookingSend(house_primary_key);
        });
        return false;
    });
}


$(document).ready(function () {
    LoadBookingForm();
});
