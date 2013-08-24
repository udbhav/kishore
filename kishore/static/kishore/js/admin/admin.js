(function($) {
  var confirmForm = function(element, options) {
    this.$elem = $(element);
    this.options = options;
    this.init();
  }

  confirmForm.prototype = {
    init: function() {
      this.$elem.on("submit", function() {
        if (confirm("Are you sure?")) {
          return true;
        } else {
          return false;
        }
      });
    }
  }

  $.fn.kishoreConfirmForm = function(option) {
    return this.each(function () {
      var $this = $(this)
      , data = $this.data('kishoreConfirmForm')
      , options = $.extend({}, $.fn.kishoreConfirmForm.defaults, typeof option == 'object' && option);
      if (!data) $this.data('kishoreConfirmForm', (data = new confirmForm(this, options)))
      if (typeof(option) == 'string') {
        data[action]();
      }
    });
  }

  var kishoreAdmin = function() {
    this.init();
  }

  kishoreAdmin.prototype ={
    init: function() {
      this.deleteLinks();
    }

    , deleteLinks: function() {
      $(".delete-form").kishoreConfirmForm();
      $(".delete-link").on("click", function() {
        $(".delete-form").submit();
      });
    }
  }

  $.fn.kishoreAdmin = function() {
    new kishoreAdmin();
  }

})(jQuery)

$(document).ready(function() {
  var kishore_admin = $.fn.kishoreAdmin();
});
