
var oldSync = Backbone.sync;
Backbone.sync = function(method, model, options){
    options.beforeSend = function(xhr){
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
    };
    return oldSync(method, model, options);
};

var TelephoneBase = Backbone.Model.extend({

  defaults: {
    "message_receipts": "",
    "chain_receipts": "",
    "message_url": "",
    "message_pk": "",
    "recording": ""
  },

  sync: function (method, model, options) {
    if (method == "read") {
      // Send all the model data with the read request
      _.defaults(options || (options = {}), {
        data: model.attributes
      });
    } else if (method == "create") {
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
    }
    return Backbone.sync.call(this, method, model, options);
  }
});

var TelephoneView = Backbone.View.extend({

  el: "#player",

  events: {
    "click .share": "share",
    "click .play": "play",
    "click .record": "record"
  },

  initialize: function() {
    this.listenTo(this.model, "change", this.render);

    this.on("error", function (msg) { console.log(msg); });
  },

  render: function () {
    var that = this;
    this.$("#sound").attr("src", this.model.get("audio") || "");
    this.$("#sound").bind("ended", function () {
      that.hasListened = true;
      that.$(".play").removeClass("button-on");
      that.$(".record").removeClass("unavailable");
    });
    return this;
  },

  share: function () {
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
        console.log("error");
        that.trigger("error");
      }
    );
  },

  play: function () {
    if (!this.audioRecorder) {
      this.trigger("error", "Click on the telephone to start.");
    } else if (!this.model.has("audio")) {
      this.trigger("error", "There is not a message to imitate.")
    } else {
      this.$("#sound").trigger("play");
      this.$(".play").addClass("button-on");
    }
  },

  record: function () {
    if (!this.audioRecorder) {
      this.trigger("error", "Click on the telephone to start.");
    } else if (!this.hasListened) {
      this.trigger("error", "You have to listen to the message first.")
    } else if (this.$(".record").hasClass("button-on")) {
      this.audioRecorder.stop();
      this.audioRecorder.exportWAV();
      this.$(".record").removeClass("button-on");
    } else {
      this.audioRecorder.clear();
      this.audioRecorder.record();
      this.$(".record").addClass("button-on");
    }
  }
});
