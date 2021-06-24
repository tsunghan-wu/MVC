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
