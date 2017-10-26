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
      new instance.web.Model(this.model)
        .call('export_client', [extractIds(this.records.records)], {
          context: instance.session.user_context,
        })
        .done(createCsv.bind(this, 'export.csv'));
    },
  });
};

function extractIds(records) {
  return _.map(records, record => record.attributes.id);
}

function createCsv(filename, source) {
  var csv = csvBody(source);
  var encodedUri = encodeURI('data:text/csv;charset=utf-8,' + csv);
  var link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
}

function csvBody(source) {
  var csvBody = source.join('\n');
  return [csvHeading(), csvBody].join('\n');
}

function csvHeading() {
  // actualizar con /models/user_sales_order.py::export_client
  var clientHeader = [
    'Clave del Cliente',
    'Nombre',
    'R.F.C.',
    'Calle',
    'Número interior',
    'Número exterior',
    'Entre Calle',
    'Y Calle',
    // 'Colonia',
    'Código Postal',
    // 'Población',
    // 'Municipio',
    // 'Estado',
    // 'País',
    // 'Nacionalidad',
    'Referencia',
    'Teléfono',
    // 'Clasificación',
    'Fax',
    'Página web',
    'C.U.R.P.',
    // 'Uso del CFDI',
    // 'Forma de pago SAT',
  ].join(',');

  return clientHeader;
}
