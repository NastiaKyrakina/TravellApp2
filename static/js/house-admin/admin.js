$(document).ready(function () {
    $('[id^=house-]').on('click', function () {
        console.log($(this).attr('id'));

        var house_primary_key = $(this).attr('id').split('-')[1];
        $('.main-area').load('/house/house-admin/' + house_primary_key, function () {
        });
    })
})
;
