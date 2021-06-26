var stageW = 640; // window.innerWidth;
var stageH = 300; // window.innerHeight;
var stage = new Konva.Stage({
    container: 'konva',
    width: stageW,
    height: stageH,
});
var layer = new Konva.Layer();
var src_patch;
var tar_patch;

var tar_obj = new Image();
tar_obj.onload = function () {
    draw_tar(this);
};
var src_obj = new Image();
src_obj.onload = function () {
    draw_src(this);
};


function draw_src(src_obj) {
    src_patch = new Konva.Image({
        image: src_obj,
        x: stage.width() / 2 - src_obj.width / 2,
        y: stage.height() / 2 - src_obj.height / 2,
        draggable: true,
        name: 'src'
    });

    // add cursor styling
    src_patch.on('mouseover', function () {
        document.body.style.cursor = 'pointer';
    });
    src_patch.on('mouseout', function () {
        document.body.style.cursor = 'default';
    });

    layer.add(src_patch);
    src_patch.moveToTop();

    const tr = new Konva.Transformer({
        nodes: [src_patch],
        keepRatio: true,
        boundBoxFunc: (oldBox, newBox) => {
            if (newBox.width < 10 || newBox.height < 10) {
                return oldBox;
            }
            return newBox;
        },
    });
    layer.add(tr);
    src_patch.on('transform', () => {
        // reset scale on transform
        src_patch.setAttrs({
            scaleX: 1,
            scaleY: 1,
            width: src_patch.width() * src_patch.scaleX(),
            height: src_patch.height() * src_patch.scaleY(),
        });
    });
}


function draw_tar(tar_obj) {
    var w = tar_obj.width;
    var h = tar_obj.height;
    var changed = false;
    if (w > stageW) {
        h = Math.round(h / w * stageW);
        w = stageW;
        changed = true;
    }
    if (h > stageH) {
        w = Math.round(w / h * stageH);
        h = stageH;
        changed = true;
    }
    stage.width(w);
    stage.height(h);

    tar_patch = new Konva.Image({
        image: tar_obj,
        x: 0,
        y: 0,
        name: 'tar',
        width: w,
        height: h,
    });
    layer.add(tar_patch);
    tar_patch.moveToBottom();
}


function start_konva(width, height) {
    stageW = width;
    stageH = height;
    tar_obj.src = 'static/data/tar.png';
    src_obj.src = 'static/data/patch.png';
    stage.add(layer);
}


function finish_transform() {
    var data = {
        "perimeter": perimeter,
        "pos": src_patch.getAbsolutePosition(),
        "rot": src_patch.getAbsoluteRotation(),
        "src_size": src_patch.size(),
        "tar_size": tar_patch.size(),
        "cavs_width": canvas.width,
        "cavs_height": canvas.height
    };
    $.ajax({
        // async: false,
        url: '/clone',
        data: JSON.stringify(data),
        type: "POST",
        contentType: "application/json;charset=utf-8",
        error: function(xhr, ajaxOptions, thrownError){
            console.log(xhr.status);
            console.log(thrownError);
        }
    });
}