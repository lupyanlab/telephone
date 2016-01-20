
var oldSync = Backbone.sync;
Backbone.sync = function(method, model, options){
    options.beforeSend = function(xhr){
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
    };
    return oldSync(method, model, options);
};

var showRecorderError = function (model, response, options) {
  telephoneView.trigger("alert", "Your recording wasn't loud enough. Really let it out this time.", "danger", 2000);
  model.set(model.previousAttributes());
}

var seeIfDone = function (model, response, options) {
  // Called after a successful POST
  // If the model hasn't changed, then we are done.
  if (model.has("completion_code")) {
    telephoneView.trigger("alert", "Your completion code is <code>" + model.get("completion_code") + "</code>", "success");
    telephoneView.trigger("disable");
    model.clear();
  } else {
    telephoneView.trigger("alert", "Your message was received! A new message was loaded.", "success", 1000);
  }
}

var MessageBase = Backbone.Model.extend({
  initialize: function () {
    this.on("createSound", this.createSound, this);
  },

  sync: function (method, model, options) {
    if (method == "create") {
      // If sending a recording, have to attach it to a form
      var formData = new FormData();
      _.each(model.attributes, function (value, key) {
        formData.append(key, value);
      });

      _.defaults(options || (options = {}), {
        data: formData,
        processData: false,
        contentType: false
      });

      telephoneView.trigger("alert", "Sending your message. Please wait.", "info");
    }
    return Backbone.sync.call(this, method, model, options);
  },

  createSound: function () {
    var that = this;
    this.soundId = "s" + this.get("id");

    soundManager.createSound({
      id: this.soundId,
      url: this.get("audio"),
      onload: function () {
        if (!that.get("end_at")) {
          that.set("end_at", soundManager.sounds[that.soundId].duration);
        }
      }
    });
  }

});

var TelephoneView = Backbone.View.extend({

  el: "#player",

  events: {
    "click .share": "share",
    "click .play": "play",
    "click .record": "record"
  },

  initialize: function () {
    this.listenTo(this.model, "change", this.render);
    this.on("alert", this.alert, this);
    this.on("disable", this.disable, this);
    this.on("finishedPlaying", this.finishedPlaying, this);

    this.hasListened = false;
  },

  render: function () {
    this.model.trigger("createSound");
  },

  finishedPlaying: function () {
    this.hasListened = true;
    this.$(".play").removeClass("button-on");
    this.$(".record").removeClass("unavailable");
  },

  share: function () {
    if (!this.audioRecorder) {
      var that = this;

      if (!navigator.getUserMedia) {
        navigator.getUserMedia = navigator.webkitGetUserMedia ||
                                 navigator.mozGetUserMedia;
      }

      navigator.getUserMedia(
        {audio: true},
        function (stream) {
          var audioInput = audioContext.createMediaStreamSource(stream);
          that.audioRecorder = new Recorder(audioInput, config);
          that.$(".share").removeClass("unavailable");

          if (that.model.get("audio")) {
            that.$(".play").removeClass("unavailable");
          } else {
            that.hasListened = true;
            that.$(".record").removeClass("unavailable");
          }
        },
        function (error) {
          that.trigger("alert", "There was a problem sharing your mic", "danger", 2000);
        }
      );
    }
  },

  play: function () {
    if (!this.audioRecorder) {
      this.trigger("alert", "Click on the telephone to start.", "info", 2000);
    } else if (!this.model.has("audio")) {
      this.trigger("alert", "There is not a message to imitate.", "info", 2000)
    } else {
      var that = this;
      soundManager.play(this.model.soundId, {
        from: this.model.get("start_at"),
        to: this.model.get("end_at"),
        onfinish: function () {
          that.trigger("finishedPlaying");
        }
      })
      this.$(".play").addClass("button-on");
    }
  },

  record: function () {
    if (!this.audioRecorder) {
      this.trigger("alert", "Click on the telephone to start.", "info", 2000);
    } else if (!this.hasListened) {
      this.trigger("alert", "You have to listen to the message first.", "info", 2000)
    } else if (this.$(".record").hasClass("button-on")) {
      this.audioRecorder.stop();
      this.audioRecorder.exportWAV();
      this.$(".record").removeClass("button-on");
      this.trigger("error", "Sending message. Please wait.", "success");
    } else {
      this.audioRecorder.clear();
      this.audioRecorder.record();
      this.$(".record").addClass("button-on");
    }
  },

  alert: function (msg, type, timeout) {
    if (!this.disabled) {
      $("#alert").html(msg);
      $("#alert").attr("class", "alert alert-" + type)
      if (timeout) {
        setTimeout(function () {
          $("#alert").text("");
          $("#alert").attr("class", "alert");
        }, timeout);
      }
    }
  },

  disable: function () {
    this.$(".record").removeClass("button-on");
    this.$(".record").addClass("unavailable");
    this.$(".play").removeClass("button-on");
    this.$(".play").addClass("unavailable");
    this.disabled = true;
  }
});
