// Get a reference to the file input element
FilePond.registerPlugin(
    FilePondPluginFileValidateType,
    FilePondPluginImageValidateSize,
    FilePondPluginImageExifOrientation,
    FilePondPluginImagePreview,
    // FilePondPluginImageCrop,
    // FilePondPluginImageResize,
    // FilePondPluginImageTransform,
    // FilePondPluginImageEdit
);

// Select the file input and use 
src_pond = document.querySelector('#src_img');
FilePond.create(
    src_pond,
    {
        allowMultiple:false,
        maxFileSize: '3MB',
        server: {
            url: './',
            process: './upload_src'
        },
    }
);

dst_pond = document.querySelector('#dst_img');
FilePond.create(
    dst_pond,
    {
        allowMultiple:false,
        maxFileSize: '3MB',
        server: {
            url: './',
            process: './upload_dst',  // flask data processing app
        },
    }
);

$(document).ready(function () {
    console.log("in the function");
    setTimeout(checkFile, 500);

    function checkFile() {
        $.ajax({
            url: './checkfile',
            type: 'GET',
            dataType: "json",
            contentType: 'application/json',
            success: function (data) {
                console.log(data.success);
                if (data.success == true) { // or whatever you want the response to be
                    $('#to_step2').removeClass('disabled');
                }
                else {
                    if(!$('#to_step2').hasClass('disabled')){
                        $('#to_step2').addClass('disabled');
                    }
                    setTimeout(checkFile, 500); // you can add a setTimeout if you don't want this running too often
                }
            }
        });
    };
});
