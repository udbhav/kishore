(function($) {

  var kishorePicker = function(element, options) {
    this.$elem = $(element);
    this.options = options;
    this.init();
  }

  kishorePicker.prototype = {
    init: function() {
      this.$input = $(this.options.fieldSelector, this.$elem);
      this.item_template = $(this.options.itemTemplateSelector).html();
      this.addInitialHTML();
      this.sortingItems();
      this.choosingItems();
      this.bindForm();
    }

    , addInitialHTML: function() {
      var self = this, items_html = "", items = [];

      if (self.$input.val().length) {
        items = JSON.parse(self.$input.val());
      }

      var $picker = $($.parseHTML(
        $(self.options.templateSelector).html()
      ));

      self.$item_sorter = $(".item-sorter", $picker);

      $.each(items, function(i, item) {
        var $item = $($.parseHTML(Mustache.render(self.item_template, item)));
        $item.data("kishore-item",item);
        self.$item_sorter.append($item);
      });

      self.$input.after($picker);
      self.$select_modal = $(self.options.modalSelector, $picker);
    }

    , sortingItems: function() {
      var self = this;

      self.$item_sorter.on("click", ".item-delete", function() {
        $(this).parents(".kishore-picker-item").remove();
        return false;
      });

      // sorting
      self.$item_sorter.sortable();
    }

    , choosingItems: function() {
      var self = this;

      // item selection
      self.$select_modal.on("click", ".kishore-picker-item", function() {
        $(this).toggleClass("selected");
      });

      // unselecting
      self.$select_modal.on("hide.bs.modal", function() {
        $(".selected", self.$select_modal).removeClass("selected");
      });

      // adding items
      $(".save-items", self.$select_modal).on("click", function() {
        $(".selected", self.$select_modal).each(function() {
          item = $(this).data("kishore-item");
          var $duplicate = $(".kishore-picker-item[data-pk=" + item.pk + "]", self.$item_sorter);
          if (!$duplicate.length) {
            var $item = $($.parseHTML(Mustache.render(self.item_template, item)));
            $item.data("kishore-item", item);
            self.$item_sorter.append($item);
          }
        });
        self.$select_modal.modal('hide');
        return false;
      });

      // pagination on item selection
      self.$select_modal.on("click", ".pager a", function() {
        self.loadItemsForSelection($(this).attr("data-page"));
        return false;
      });

      self.loadItemsForSelection(1);
    }

    , loadItemsForSelection: function(page) {
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

        $.getJSON(self.$select_modal.attr("data-item-url") + "?page=" + page, function(data) {
          $(".page", self.$select_modal).hide();
          var $page = $('<div class="row page">').attr("data-page",page).html(html)
          , html = "";

          $page.data("page",data);

          var items = data[self.options.JSONArrayName];
          $.each(items, function(i,item) {
            var $item = $($.parseHTML(Mustache.render(self.item_template, item)));
            $item.data("kishore-item",item);
            $page.append($item);
          });

          self.$select_modal.find(".modal-body").prepend($page);
          update_pagination($page);
        });

      }
    }

    , bindForm: function() {
      var self = this;

      self.$elem.on("submit", function() {
        items = []
        $(".kishore-picker-item", self.$item_sorter).each(function() {
          items.push($(this).data("kishore-item"));
        });
        self.$input.val(JSON.stringify(items));
      });
    }

  }

  $.fn.kishorePicker = function(option) {
    return this.each(function() {
      var $this = $(this)
      , options = $.extend({}, $.fn.kishorePicker.defaults, typeof option == 'object' && option);
      new kishorePicker(this, options);
    });
  }

  $.fn.kishorePicker.defaults = {
    'fieldSelector': 'input.kishore-images-input',
    'templateSelector': '#image-picker-template',
    'itemTemplateSelector': '#image-picker-item-template',
    'modalSelector': '#add-images',
    'JSONArrayName': 'images'
  }

})(jQuery)
