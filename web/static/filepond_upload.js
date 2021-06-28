var srcID = '';
var tarID = '';

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
var src_pond_obj = FilePond.create(
    src_pond,
    {
        allowMultiple:false,
        maxFileSize: '3MB',
        server: {
            url: './',
            process: {
                url: './upload_src',
                onload: function (res) {
                    srcID = res;
                    return res;
                }
            },
            revert: './del_src',
        },
    }
);

dst_pond = document.querySelector('#dst_img');
var dst_pond_obj = FilePond.create(
    dst_pond,
    {
        allowMultiple:false,
        maxFileSize: '3MB',
        server: {
            url: './',
            process: {
                url: './upload_dst',
                onload: function (res) {
                    tarID = res;
                    return res;
                }
            },
            revert: './del_dst',
        },
    }
);

$(document).ready(function () {
    console.log("in the function");
    setTimeout(checkFile, 500);

    function checkFile() {
        if (srcID.length > 0 && tarID.length > 0) {
            $('#to_step2').removeClass('disabled'); 
        } else {
            if (!$('#to_step2').hasClass('disabled')) {
                $('#to_step2').addClass('disabled');
            }
            setTimeout(checkFile, 500); // you can add a setTimeout if you don't want this  
        }
        // $.ajax({
        //     url: './checkfile',
        //     type: 'GET',
        //     dataType: "json",
        //     contentType: 'application/json',
        //     success: function (data) {
        //         console.log(data.success);
        //         if (data.success == true) { // or whatever you want the response to be
        //             $('#to_step2').removeClass('disabled');
        //         }
        //         else {
        //             if(!$('#to_step2').hasClass('disabled')){
        //                 $('#to_step2').addClass('disabled');
        //             }
        //             setTimeout(checkFile, 500); // you can add a setTimeout if you don't want this running too often
        //         }
        //     }
        // });
    };
});

function remove_frontend(){
    console.log("remove front end!");
    src_pond_obj.removeFiles();
    dst_pond_obj.removeFiles();
    srcID = '';
    dstID = '';
    if (!$('#to_step2').hasClass('disabled')) {
        $('#to_step2').addClass('disabled');
    }
}
