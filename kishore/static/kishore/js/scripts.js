(function($) {
  var Carousel = function(element, options) {
    this.$elem = $(element);
    this.options = options;
    this.init();
  }

  Carousel.prototype = {
    init: function() {
      var self = this;
      self.setup_carousel();
      $(window).resize(function() {self.setup_carousel();});
    }

    , setup_carousel: function() {
      var self = this;
      var unit_width = self.$elem.width();
      self.$elem.attr("data-unit-width", unit_width);

      $(".images", self.$elem).each(function(i) {
        $(this).find("li").css("width", unit_width);
        $(this).css("width", ($(this).find("li").length * unit_width));
      });

      $(".thumbnails a", self.$elem).on("click", function() {
        new_position = $(this).parent().index() * parseInt(self.$elem.attr("data-unit-width"));
        self.$elem.find(".images").css("margin-left", -new_position);
        $(this).parent().addClass("active").siblings().removeClass("active");
        return false;
      });
    }
  }

  $.fn.kishoreCarousel = function(option) {
    return this.each(function () {
      var $this = $(this)
      , data = $this.data('kishoreCarousel')
      , options = $.extend({}, $.fn.kishoreCarousel.defaults, typeof option == 'object' && option);
      if (!data) $this.data('kishoreCarousel', (data = new Carousel(this, options)))
      if (typeof(option) == 'string') {
        data[action]();
      }
    });
  }

  var kishoreStripe = function(element, options) {
    this.$elem = $(element);
    this.options = options;
    this.init();
  }

  kishoreStripe.prototype = {
    init: function() {
      var self = this;
      this.bindForms();
    }

    , bindForms: function() {
      var self = this;

      self.$elem.on("submit", function() {
        var $form = $(this);

        $form.find("button").prop("disabled", true);

        Stripe.createToken($form, function(status, response) {
          if (response.error) {
            $form.find("button").prop("disabled", false);
            var $error = $form.find(".alert-danger");

            if ($error.length == 0) {
              $error = $('<div class="alert alert-danger">').html(response.error.message);
              $form.find("legend").after($error);
            } else {
              $error.html(response.error.message);
            }
          } else {
            $form.find("input[name=token]").val(response.id);
            $form[0].submit();
          }
        });

        return false;
      });
    }

  }

  $.fn.kishoreStripe = function(option) {
    return this.each(function () {
      var $this = $(this)
      , data = $this.data('kishoreStripe')
      , options = $.extend({}, $.fn.kishoreStripe.defaults, typeof option == 'object' && option);
      if (!data) $this.data('kishoreStripe', (data = new kishoreStripe(this, options)))
      if (typeof(option) == 'string') {
        data[action]();
      }
    });
  }

  $.fn.kishoreAddCartForm = function(option) {
    return this.each(function() {
      var $this = $(this);
      $("input[type=radio], input[type=submit]", $this).hide();
      $("label", $this).addClass("btn btn-primary").on("click", function() {
        $(this).find("input[type=radio]").prop('checked',true);
        $this.submit();
      });
    });
  }
})(jQuery);

$(document).ready(function() {
  $.fn.kishoreCSRFProtection();
  $(".add-cart").kishoreAddCartForm();
  $(".kishore-audio-player").kishoreAudioPlayer();
});
