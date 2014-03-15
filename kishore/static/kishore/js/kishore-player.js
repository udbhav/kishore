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
      var self = this, song_ids = new Array(), stream_urls = new Array();

      $("li", self.$elem).each(function() {
        var song_id = $(this).attr("data-song-id");
        var stream_url = $(this).attr("data-stream-url");
        if (song_id) {
          song_ids.push(song_id);
        } else if (stream_url) {
          stream_urls.push([this, stream_url])
        }
      });

      if (song_ids.length) {
        $.post(self.$elem.attr("data-song-url"), {song_ids: JSON.stringify(song_ids)}, function(data) {
          $.each(data, function(k,v) {
            var element = $("li[data-song-id=" + k + "]", self.$elem)[0];
            $("li[data-song-id=" + k + "]", self.$elem).data("kishre_stream_url",v);
            //self.createSound(element, v);
          });
        });
      }

      if (stream_urls.length) {
        $.each(stream_urls, function(i, v) {
          $(v[0]).data("kishore_stream_url", v[1]);
        });
      }
    }

    , createSound: function(element, url) {
      var sound = soundManager.createSound({
        url: url,
        multiShot: false
      });
      $(element).data("kishore_sound",sound);
    }

    , bindEvents: function() {
      var self = this;

      $("li", self.$elem).on("click", function(e) {
        self.toggleSound(this);
      });

      $(".song-link", self.$elem).on("click", function(e) {
        e.stopPropagation();
      });
    }

    , toggleSound: function(li) {
      var self = this, $li = $(li),
      state = $li.data("kishore_sound_state");
      console.log(state);

      if (!state) { // stopped
        self.initialPlay($li);
      } else if (state == 1) { // playing
        $li.data("kishore_sound_state",2);
        self.lastSound.pause();
        $li.addClass("paused");
      } else if (state == 2) { // paused
        $li.data("kishore_sound_state",1);
        self.lastSound.resume();
        $li.removeClass("paused");
      }

    }

    , initialPlay: function($li) {
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

      // create sound
      self.lastSound = soundManager.createSound({
        url: $li.data('kishore_stream_url'),
        multiShot: false
      });

      $controls.append($position);
      $li.append($controls).prepend($time);

      $position.on("click", function(e) {
        e.stopPropagation();
        // var duration = self.lastSound.loaded ? self.lastSound.duration : self.lastSound.durationEstimate;
        // var position = (e.pageX - $(this).offset().left) / $(this).width() * duration;
        // position = Math.min(Math.floor(position), duration);
        // if (!isNaN(position)) {
        //   self.lastSound.setPosition(position);
        // }
      });

      $link.on("click", function(e) { e.stopPropagation() });

      self.lastSound.play({
        whileplaying: function() {
          var duration = self.lastSound.loaded ? self.lastSound.duration : self.lastSound.durationEstimate;
          $progress.width(String(self.lastSound.position/duration*100) + "%");
          $time.html(self.getPosition(self.lastSound));
        },
        onload: function() {},
        onfinish: function() {
          $("li", self.$elem).removeClass("playing paused");
          $controls.remove();
          $time.remove()
        }
      });
      $li.addClass("playing");
      $li.data("kishore_sound_state",1);
    }

    , getPosition: function(sound) {
      var self = this;

      var position = Math.round(self.lastSound.position/1000);
      var duration = self.lastSound.loaded ? self.lastSound.duration : self.lastSound.durationEstimate;

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
