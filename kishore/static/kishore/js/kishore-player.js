(function($) {
  soundManager.setup({
    url: kishore_static_root + "/swf/",
    preferFlash: false,
    onready: function() {
      $("body").trigger("soundManager.ready");
    }
  });

  var kishorePlayer = function(element, options) {
    this.$elem = $(element);
    this.options = options;
    this.init();
  }

  kishorePlayer.prototype = {
    init: function() {
      var self = this;

      $("body").on("soundManager.ready", function() {
        self.getSounds();
        self.bindEvents();
      });
    }

    , getSounds: function() {
      var self = this, song_ids = new Array();
      $("li", self.$elem).each(function() {
        song_ids.push($(this).attr("data-song-id"));
      });

      $.post(self.$elem.attr("data-song-url"), {song_ids: JSON.stringify(song_ids)}, function(data) {
        $.each(data, function(k,v) {
          self.createSound(k, v);
        });
      });
    }

    , createSound: function(id, url) {
      var self = this;
      var sound = soundManager.createSound({url: url});
      $("li[data-song-id=" + id + "]", self.$elem).data("kishore_sound",sound);
    }

    , bindEvents: function() {
      var self = this;

      $("li", self.$elem).on("click", function() {
        self.toggleSound(this);
      });

      $(".song-link", self.$elem).on("click", function(e) {
        e.stopPropagation();
      });
    }

    , toggleSound: function(li) {
      var self = this, $li = $(li), sound = $li.data("kishore_sound");

      if ($li.hasClass("paused")) {

        sound.play();
        $li.removeClass("paused");

      } else if ($li.hasClass("playing")) {

        sound.pause();
        $li.addClass("paused");

      } else {

        self.initialPlay($li, sound);

      }
    }

    , initialPlay: function($li, sound) {
      var self = this
      , $controls = $('<div id="song-controls"><div id="song-loading"></div></div>')
      , $loading = $("#song-loading", $controls)
      , $position = $('<div id="song-position" class="progress"><div class="progress-bar"></div></div>')
      , $progress = $(".progress-bar", $position)

      , $time = $('<div id="song-time" class="pull-right"></div>')
      , $link = $('<a class="pull-right" id="song-link">').attr("href", $li.attr("data-link")).html("permalink");

      // stop other stuff
      soundManager.stopAll();
      $("li", self.$elem).removeClass("playing", "paused");
      $("#song-controls, #song-time, #song-link").remove();

      $controls.append($position);
      $li.addClass("playing").append($controls).prepend($time).prepend($link);

      $position.on("click", function(e) {
        var position = (e.pageX - $(this).offset().left) / $(this).width() * sound.durationEstimate;
        sound.setPosition(position);
        e.stopPropagation();
      });

      $link.on("click", function(e) { e.stopPropagation() });

      sound.play({
        whileplaying: function() {
          $progress.width(String(sound.position/sound.durationEstimate*100) + "%");
          $time.html(self.getPosition(sound));
        },
        whileloading: function() {
          //
          //console.log(width);
        },
        onfinish: function() {
          $("li", self.$elem).removeClass("playing paused");
          $controls.remove();
          $time.remove()
        }
      });
    }

    , getPosition: function(sound) {
      var self = this;

      var position = Math.round(sound.position/1000);
      var duration = Math.round(sound.durationEstimate/1000);

      return Math.floor(position/60) + ':' + self.padSeconds(position % 60) + ' / ' + Math.floor(duration/60) + ':' + self.padSeconds(duration % 60);
    }

    , padSeconds: function(number) {
      var str = '' + number;
      while (str.length < 2) {
        str = '0' + str;
      }

      return str;
    }

  }

  $.fn.kishoreAudioPlayer = function(option) {
    return this.each(function () {
      var $this = $(this)
      , data = $this.data('kishoreAudioPlayer')
      , options = $.extend({}, $.fn.kishoreAudioPlayer.defaults, typeof option == 'object' && option);
      if (!data) $this.data('kishoreAudioPlayer', (data = new kishorePlayer(this, options)))
      if (typeof(option) == 'string') {
        data[action]();
      }
    });
  }

})(jQuery);
