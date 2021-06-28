var ready = (callback) => {
    if (document.readyState != "loading") callback();
    else document.addEventListener("DOMContentLoaded", callback);
}
ready(() => {
    document.querySelector(".header").style.height = window.innerHeight + "px";
})

function getElementY(query) {
  return window.pageYOffset + document.querySelector(query).getBoundingClientRect().top
}

function doScrolling(element, duration) {
	var startingY = window.pageYOffset
  var elementY = getElementY(element)
  // If element is close to page's bottom then window will scroll only to some position above the element.
  var targetY = document.body.scrollHeight - elementY < window.innerHeight ? document.body.scrollHeight - window.innerHeight : elementY
	var diff = targetY - startingY
  // Easing function: easeInOutCubic
  // From: https://gist.github.com/gre/1650294
  var easing = function (t) { return t<.5 ? 4*t*t*t : (t-1)*(2*t-2)*(2*t-2)+1 }
  var start

  if (!diff) return

	// Bootstrap our animation - it will get called right before next frame shall be rendered.
	window.requestAnimationFrame(function step(timestamp) {
    if (!start) start = timestamp
    // Elapsed miliseconds since start of scrolling.
    var time = timestamp - start
		// Get percent of completion in range [0, 1].
    var percent = Math.min(time / duration, 1)
    // Apply the easing.
    // It can cause bad-looking slow frames in browser performance tool, so be careful.
    percent = easing(percent)

    window.scrollTo(0, startingY + diff * percent)

		// Proceed with animation as long as we wanted it to.
    if (time < duration) {
      window.requestAnimationFrame(step)
    }
  })
}

function clear_result() {
  if (resID.length > 0) {
    $.ajax({
      async: false,
      url: '/clear_result',
      data: JSON.stringify({
          "srcID": srcID,
          "resID": resID
      }),
      type: "POST",
      contentType: "application/json;charset=utf-8",
      success: function(res){},
      error: function(xhr, ajaxOptions, thrownError){
          console.log(xhr.status);
          console.log(thrownError);
      }
    }); 
  }
  resID = '';
}


function clear() {
  $.ajax({
    url: '/clear',
    data: JSON.stringify({
        "srcID": srcID,
        "tarID": tarID,
        "resID": resID
    }),
    type: "POST",
    contentType: "application/json;charset=utf-8",
    success: function(res){},
    error: function(xhr, ajaxOptions, thrownError){
        console.log(xhr.status);
        console.log(thrownError);
    }
  });
  srcID = '';
  tarID = '';
  resID = '';
}

function restart() {
  complete = false;
  clear_result()
  $('#to_step3').addClass('disabled');
  $('#to_step3_fast').addClass('disabled');
  $('#download').addClass('disabled');
  destroy_canvas();
  destroy_konva();
  $("#result").hide();
  $('#result_src').attr("href", "static/data/result.png");
}


window.onbeforeunload = function () {
  clear();
};
