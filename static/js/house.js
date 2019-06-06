$(document).ready(function () {


    $(".house").on('click', 'button[id^=edit-element-]',
        function () {
            var house_primary_key = $(this).attr('id').split('-')[2];
            location.href = '/house/edit/' + house_primary_key + '/';

        });

    $(".house").on('click', 'button[id^=delete-element-]',
        function () {
            var house_primary_key = $(this).attr('id').split('-')[2];
            let action = $(this).attr('formaction');
            delete_house(house_primary_key, action);

        });

    $(".house").on('click', 'button[id^=change-element-]',
        function () {
            var house_primary_key = $(this).attr('id').split('-')[2];
            let action = $(this).attr('formaction');
            change_status(house_primary_key, action);

        });

    function delete_house(house_primary_key, action) {
        if (confirm('are you sure you want to remove this post?') == true) {

            $.ajax({
                url: action, // the endpoint
                type: "POST", // http method
                data: {
                    csrfmiddlewaretoken: Cookies.get('csrftoken'),
                    housepk: house_primary_key
                }, // data sent with the delete request
                success: function (json) {

                    location.href = '/user/1/'

                },

                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        } else {
            return false;
        }
    }


    function change_status(house_primary_key, action) {

        $.ajax({
            url: action, // the endpoint
            type: "POST", // http method
            data: {
                csrfmiddlewaretoken: Cookies.get('csrftoken'),
                housepk: house_primary_key
            }, // data sent with the delete request
            success: function (status) {

                if (status.status == 'fail') {
                    alert('Status was not be change');
                } else {
                    let status_span;
                    let button = $('.button-status');

                    if (status.status) {
                        status_span = '<span class="text-success">Active</span>';
                        button.text('frozen');
                    } else {
                        status_span = '<span class="text-info">Frozen</span>';
                        button.text('active');
                    }

                    $('.status').html(status_span);

                }

            },

            error: function (xhr, errmsg, err) {
                // Show an error
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });

    }

});

