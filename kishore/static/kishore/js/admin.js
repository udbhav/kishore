(function($) {
  $.fn.kishoreConfirmForm = function(option) {
    return this.each(function () {
      $(this).on("submit", function() {
        if (confirm("Aure you sure")) {
          return true;
        } else {
          return false;
        }
      });
    });
  }

  $.fn.kishoreFormTriggers = function(option) {
    return this.each(function() {
      var $this = $(this), $form = $("." + $this.attr("data-form-class"));
      $form.kishoreConfirmForm();
      $this.on("click", function() {
        $form.submit();
      });
    });
  }

  $.fn.kishoreEditor = function(option) {
    return this.each(function(i) {
      var $elem = $(this), converter = Markdown.getSanitizingConverter()
      suffix = "-kishore-editor-" + i, initial = $elem.val();

      $elem.hide();
      var $editor = $($.parseHTML(
        Mustache.render($("#kishore-editor-template").html(), {
          suffix: suffix,
          initial: initial
        })));

      $elem.after($editor);
      $(".kishore-editor-input", $editor).on("change", function() {
        $elem.val($(this).val());
      });

      var editor = new Markdown.Editor(converter, suffix);
      editor.run();
    });
  }

  $.fn.kishoreDatepicker = function(option) {
    return this.each(function() {
      var $this = $(this);
      $this.datepicker({
        prevText: "",
        nextText: "",
        dateFormat: "yy-mm-dd"
      });
    });
  }

  var productForm = function(element, options) {
    this.$elem = $(element);
    this.options = options;
    this.init();
  };

  productForm.prototype = {
    init: function() {
      var self = this, $input = $("input[name=model_class]");

      if ($input.attr("type") == "radio") {
        $input.on("change", function() {
          var model_class = $("input[name=model_class]:checked").val();
          self.showModelSpecificFields(model_class);
        });

        var model_class = $("input[name=model_class]:checked").val();
        if (model_class) {
          self.showModelSpecificFields(model_class);
        }

      } else {
        self.showModelSpecificFields($input.val())
      }
    }

    , model_classes: {
      'Merch': '.merch',
      'PhysicalRelease': '.release, .physical-release',
      'DigitalSong': '.song',
      'DigitalRelease': '.release, .digital-release'
    }

    , showModelSpecificFields: function(model_class) {
      var self = this;
      var selector = self.model_classes[model_class];
      $(".hideable", self.$elem).addClass("hide");
      $(selector,self.$elem).removeClass("hide");
    }

  }


  $.fn.kishoreProductForm = function(option) {
    return this.each(function() {
      var $this = $(this)
      , data = $this.data('kishoreProductForm')
      , options = $.extend({}, $.fn.kishoreProductForm.defaults, typeof option == 'object' && option);
      if (!data) $this.data('kishoreProductForm', (data = new productForm(this, options)))
      if (typeof(option) == 'string') {
        data[action]();
      }
    });
  }


})(jQuery)

$(document).ready(function() {
  $(".delete-link").kishoreFormTriggers();
  // $(".image-picker-form").kishoreImagePicker();


  $(".release-form").kishorePicker({
    fieldSelector: 'input[name=release_images]'
  });

  $(".release-form").kishorePicker({
    fieldSelector: 'input[name=release_songs]',
    templateSelector: '#song-picker-template',
    itemTemplateSelector: '#song-picker-item-template',
    modalSelector: '#add-songs',
    JSONArrayName: 'song_list',
  })

  $(".song-form").kishorePicker({
    fieldSelector: 'input[name=song_images]'
  });

  $(".product-form").kishorePicker({
    fieldSelector: 'input[name=product_images]'
  });

  $(".kishore-editor-input").kishoreEditor();
  $(".song-form input[name=release_date]").kishoreDatepicker();
  $(".product-form").kishoreProductForm();
  $.fn.kishoreCSRFProtection();
});
