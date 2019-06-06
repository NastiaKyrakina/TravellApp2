$(document).ready(function () {
    $('#id_photo').change(function (e) {
        var image = e.target.files[0];
        $('#image-prev img').remove();

        var reader = new FileReader();
        reader.onload = (function (theFile) {
            return function (e) {
                $('<img src="' + e.target.result + '" class="img-fluid m-1">').appendTo('#image-prev');
            };
        })(image);
        reader.readAsDataURL(image);
    });
});