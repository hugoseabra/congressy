window.cgsy = window.cgsy || {};
window.cgsy.survey = window.cgsy.survey || {};

(function($, survey) {

  survey.OptionManager = function(option_input_tags_el, add_button_el, options_counter_el) {
    var self = this;

    this.option_input_tags_el = $(option_input_tags_el);
    this.add_button_el = $(add_button_el);
    this.options_counter_el = $(options_counter_el);
    this.fields = [];
    this.focused_input = null;

    var countFields = function() {
      return self.fields.length;
    };

    var createPasteEvent = function(field) {
    	input_el = field.getElement().find('input.option-input-text');
      input_el.unbind('paste');
      input_el.on('paste', function(e) {
      	var el = $(this);
      
        // common browser -> e.originalEvent.clipboardData
        // uncommon browser -> window.clipboardData
        var clipboardData = e.clipboardData || e.originalEvent.clipboardData || window.clipboardData;
        var pastedData = clipboardData.getData('text');
                
        window.setTimeout(function() {
          
          console.log('Content pasted on: ' + field.id);
        	var split_data = pastedData.split("\n");

          if (split_data.length <= 1) {
          	return;
          }
          
          $(input_el).val('');
          
          self.options_counter_el.text('aguarde...');
          
          window.setTimeout(function() {
            var started = false;
            $.each(self.fields, function(i, existing_field) {
              if (started === true) {
                existing_field.remove();
                return;
              }

              if (existing_field.id === field.id) {
                started = true;
              }              
            });

            $.each(split_data, function(i, line_data) {
              var value = $.trim(line_data);
              if (!value) {
                return;
              }

              if (i === 0) {
                el.val(value);
              } else {
                self.addAndRenderField(value);
              }
            });
          }, 10);
        }, 5);
      });
    };

    this.updateOptionCounter = function() {
      this.options_counter_el.text(countFields());
    };

    this.createField = function(value) {
      // NÃO DEIXAR REPETIR ID
      var field = new survey.OptionField(value);
      field.setRemoveCallback(function() {
        if (!self.fields.length) {
          return;
        }
        var new_fields = [];
        $.each(self.fields, function(i, existing_field) {
          if (existing_field.id !== field.id) {
            new_fields.push(existing_field);
          }
        });
        self.fields = new_fields;
        self.updateOptionCounter();
      });
      return field;
    };

    this.addField = function(value) {
      var field = self.createField(value);
      self.fields.push(field);
      self.updateOptionCounter();
      return field;
    };
    
    this.renderField = function(field) {
    	createPasteEvent(field);
      self.option_input_tags_el.append(field.getElement());
    };

    this.addAndRenderField = function(value) {
      self.renderField(self.addField(value))
    };
    
    this.render = function(data) {
      if (typeof data === 'undefined') {
        data = [];
      } else if (typeof data[Symbol.iterator] !== 'function') {
        data = [];
        console.error('Provided data is not iterable.');
      }
      this.fields = [];

      if (data.length === 0 && countFields() === 0) {
        this.addField(null);
      } else if (data.length) {
        $.each(data, function(i, item) {

        });
      }

      $.each(self.fields, function(i, field) {
      	self.renderField(field);
      });
    };

    self.add_button_el.unbind('click');
    window.setTimeout(function() {
      self.add_button_el.on('click', function() {
        self.addAndRenderField();
      });
    }, 350);
  };

  survey.OptionField = function(value) {
    this.id = null;

    this.value = value;
    this.input_el = null;
    this.main_el = null;

    var self = this;
    var remove_callback = function() {};

    var init = function() {
      self.id = makeId();
    };

    var makeId = function() {
      var text = "";
      var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

      for (var i = 0; i < 5; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));

      return text;
    };

    var createMainEl = function() {
      if (self.main_el) {
        return self.main_el;
      }

      self.main_el = $('<div>').addClass('form-group ').css('margin-bottom', '3px');
      self.input_el = $('<input>').attr({
        'type': 'text',
        'class': 'form-control option-input-text',
        'name': 'option',
        'maxlength': 150
      }).val(self.value);
      self.main_el.append(self.input_el);

      var delete_button_field = $('<div>').css({
        'position': 'absolute',
        'right': '17px',
        'margin-top': '-32px',
        'z-index': 3
      });
      self.main_el.append(delete_button_field);

      var delete_button_el = $('<button>').attr('type', 'button').addClass('btn btn-sm btn-danger btn-trans option-delete-button').append($('<i>').addClass('glyphicon glyphicon-trash'));
      delete_button_field.append(delete_button_el);

      return self.main_el;
    };

    this.setRemoveCallback = function(callback) {
      if (typeof callback !== 'function') {
        console.error('Callback is not callable: ' + callback);
        return;
      }
      remove_callback = callback;
    };

    this.remove = function() {
      this.main_el.remove();
      remove_callback();
    };

    this.getElement = function() {
      var el = createMainEl();

      window.setTimeout(function() {
        var delete_button = el.find('button.option-delete-button');
        delete_button.unbind('click');
        delete_button.on('click', function() {
          self.remove();
        });
      }, 300);

      return el;
    };

    init();
  };

})(jQuery, window.cgsy.survey);
