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

  var imagePicker = function(element, options) {
    this.$elem = $(element);
    this.options = options;
    this.init();
  };

  imagePicker.prototype = {
    init: function() {
      this.$input = $(this.options.imageFieldSelector, this.$elem);
      this.item_template = $("#image-picker-item-template").html();

      this.addInitialHTML();
      this.sortingImages();
      this.choosingImages();
      this.bindForm();
    }

    , addInitialHTML: function() {
      var self = this, images_html = "", images = [];

      if (self.$input.val().length) {
        images = JSON.parse(self.$input.val());
      }

      var $picker = $($.parseHTML(
        $("#image-picker-template").html()
      ));

      self.$image_sorter = $(".image-sorter", $picker);

      $.each(images, function(i, image) {
        var $image = $($.parseHTML(Mustache.render(self.item_template, image)));
        $image.data("image",image);
        self.$image_sorter.append($image);
      });

      self.$input.after($picker);
      this.$select_modal = $("#add-images", $picker);
    }

    , sortingImages: function() {
      var self = this;

      // image deletion
      self.$image_sorter.on("click", ".image-delete", function() {
        $(this).parents(".image-picker-image").remove();
        return false;
      });

      // sorting
      self.$image_sorter.sortable();
    }

    , choosingImages: function() {
      var self = this;

      // image selection
      self.$select_modal.on("click", ".image-picker-image", function() {
        $(this).toggleClass("selected");
      });

      // unselecting
      self.$select_modal.on("hide.bs.modal", function() {
        $(".selected", self.$select_modal).removeClass("selected");
      });

      // adding images
      $(".save-images", self.$select_modal).on("click", function() {
        $(".selected", self.$select_modal).each(function() {
          image = $(this).data("image");
          var $duplicate = $(".image-picker-image[data-pk=" + image.pk + "]", self.$image_sorter);
          if (!$duplicate.length) {
            var $image = $($.parseHTML(
              Mustache.render($("#image-picker-item-template").html(),image)
            ));
            $image.data("image", image);
            self.$image_sorter.append($image);
          }
        });
        self.$select_modal.modal('hide');
        return false;
      });

      // pagination on image selection
      self.$select_modal.on("click", ".pager a", function() {
        self.loadImagesForSelection($(this).attr("data-page"));
        return false;
      });

      self.loadImagesForSelection(1);
    }

    , loadImagesForSelection: function(page) {
      var self = this;
      var $loaded_page = $(".page[data-page=" + page + "]", self.$select_modal);

      function update_pagination($page) {
        $(".pager li.active", self.$select_modal).removeClass("active");
        var page = $page.data("page").page;

        if (page.has_next) {
          $(".pager li.next").addClass("active").find("a").attr("data-page",page.page+1);
        }

        if (page.has_previous) {
          $(".pager li.previous").addClass("active").find("a").attr("data-page",page.page-1);
        }
      }

      if ($loaded_page.length) {
        $(".page", self.$select_modal).hide();
        $loaded_page.show();
        update_pagination($loaded_page);
      } else {

        $.getJSON(self.$select_modal.attr("data-image-url") + "?page=" + page, function(data) {
          $(".page", self.$select_modal).hide();
          var $page = $('<div class="row page">').attr("data-page",page).html(html)
          , html = "";

          $page.data("page",data);

          $.each(data.images, function(i,image) {
            var $image =  $($.parseHTML(Mustache.render(
              $("#image-picker-item-template").html(), image)));
            $image.data("image",image);
            $page.append($image);
          });

          self.$select_modal.find(".modal-body").prepend($page);
          update_pagination($page);
        });

      }
    }

    , bindForm: function() {
      var self = this;

      self.$elem.on("submit", function() {
        images = []
        $(".image-picker-image", self.$image_sorter).each(function() {
          images.push($(this).data("image"));
        });
        self.$input.val(JSON.stringify(images));
      });
    }

  }

  $.fn.kishoreImagePicker = function(option) {
    return this.each(function() {
      var $this = $(this)
      , data = $this.data('kishoreImagePicker')
      , options = $.extend({}, $.fn.kishoreImagePicker.defaults, typeof option == 'object' && option);
      if (!data) $this.data('kishoreImagePicker', (data = new imagePicker(this, options)))
      if (typeof(option) == 'string') {
        data[action]();
      }
    });
  }

  $.fn.kishoreImagePicker.defaults = {
    'imageFieldSelector': 'input.kishore-images-input',
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
          console.log(model_class);
          self.showModelSpecificFields(model_class);
        });
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

  $.fn.kishoreCSRFProtection = function() {
    // CSRF Protection
    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');
    function csrfSafeMethod(method) {
      // these HTTP methods do not require CSRF protection
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
      crossDomain: false, // obviates need for sameOrigin test
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      }
    });
  }

})(jQuery)

$(document).ready(function() {
  $(".delete-link").kishoreFormTriggers();
  $(".image-picker-form").kishoreImagePicker();


  $(".song-form").kishoreImagePicker({
    imageFieldSelector: 'input[name=song_images]'
  });

  $(".release-form").kishoreImagePicker({
    imageFieldSelector: 'input[name=release_images]'
  });

  $(".release-form").kishoreImagePicker({
    imageFieldSelector: 'input[name=release_images]'
  });

  $(".kishore-editor-input").kishoreEditor();
  $(".song-form input[name=release_date]").kishoreDatepicker();
  $(".product-form").kishoreProductForm();
  $.fn.kishoreCSRFProtection();
});
