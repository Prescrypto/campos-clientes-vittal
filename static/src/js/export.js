// @format

openerp.campos_clientes_vittal = function(instance, local) {
  instance.web.ListView.include({
    render_buttons: function() {
      var btn;
      // GET BUTTON REFERENCE
      this._super.apply(this, arguments);
      if (this.$buttons) {
        btn = this.$buttons.find('.export_button');
      }

      // PERFORM THE ACTION
      btn.on('click', this.proxy('export_button'));
    },
    export_button: function() {
    },
  });
};
