(function() {
  var KISHORE = {};

  KISHORE.init = function() {
    $("body").addClass("kishore-with-js");
    this.artwork_carousel();
  }

  KISHORE.artwork_carousel = function() {
    function carousel_init() {
      var unit_width = $(".kishore_container .artwork").width();
      $(".kishore_container .artwork").attr("data-unit-width", unit_width);

      $(".kishore_container .artwork .images").each(function(i) {
        $(this).find("li").css("width", unit_width);
        $(this).css("width", ($(this).find("li").length * unit_width));
      });
    }

    carousel_init();
    $(window).resize(function() {carousel_init();});

    $(".kishore_container .artwork .thumbnails a").click(function() {
      new_position = $(this).parent().index() * parseInt($(this).parents(".artwork").attr("data-unit-width"));
      $(this).parents(".artwork").find(".images").css("margin-left", -new_position);
      $(this).parent().addClass("active").siblings().removeClass("active");
      return false;
    });
  }

  $(document).ready(function() {
    KISHORE.init();
  });
})();
