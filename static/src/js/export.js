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
    'Estatus',
    'Nombre',
    'R.F.C.',
    'Calle',
    'Número interior',
    'Número exterior',
    'Entre Calle',
    'Y Calle',
    'Colonia',
    'Código Postal',
    'Población',
    'Municipio',
    'Estado',
    'País',
    'Nacionalidad',
    'Referencia',
    'Teléfono',
    'Clasificación',
    'Fax',
    'Página web',
    'C.U.R.P.',
    'Clave de zona',
    'Imprimir',
    'Enviar por correo electrónico',
    'Envío silencioso',
    'Mail Predeterminado',
    'Día de revisión',
    'Día de pago',
    'Con crédito',
    'Días de crédito',
    'Limite de crédito',
    'Saldo',
    'Lista de precios',
    'Documento del último pago',
    'Monto del último pago',
    'Descuento',
    'Documento de última venta',
    'Monto de última venta',
    'Fecha de última venta',
    'Ventas anuales',
    'Clave de vendedor',
    'Tipo de empresa',
    'Matriz',
    'Calle de envío',
    'Núm. Int de envío',
    'Núm. Ext de envío',
    'Entre calle envío',
    'Y calle envío',
    'Colonia de envío',
    'Población de envío',
    'Municipio de envío',
    'Estado de envío',
    'País de envío',
    'Código postal de envío',
    'Clave de zona de envío',
    'Referencia de envío',
    'Cuenta contable',
    'Addenda de facturas',
    'Addenda de devolución',
    'Namespace del cliente',
    'Método de pago',
    'Número de cuenta',
    'Desglose de impuesto 1',
    'Desglose de impuesto 2',
    'Desglose de impuesto 3',
    'Desglose de impuesto 4',
    'Desglose personalizado',
    'Uso del CFDI',
    'Residencia fiscal',
    'Número de registro de identidad fiscal',
    'Forma de pago SAT',
    'Campo Libre 1',
    'Campo Libre 2',
    'Campo Libre 3',
    'Campo Libre 4',
    'Campo Libre 5',
  ].join(',');

  return clientHeader;
}
