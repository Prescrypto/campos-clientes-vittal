// @format

openerp.models_export_vittal = function(instance, local) {
  instance.web.ListView.include({
    render_buttons: function() {
      var btn;
      // GET BUTTON REFERENCE
      this._super.apply(this, arguments);
      if (this.$buttons) {
        btnExport = this.$buttons.find('.export_button');
        btnExportAll = this.$buttons.find('.export_all_button');
        //btnStampAll = this.$buttons.find('.stmp_all_button');
      }

      // PERFORM THE ACTION
      //btnExport.on('click', this.proxy('export_button'));
      btnExport.on('click', this.proxy('stmp_all_button'));
      btnExportAll.on('click', this.proxy('export_all_button'));
      //btnStampAll.on('click'), this.proxy('stmp_all_button');
    },
    export_button: function(event) {
      var type = event.target.dataset.type;
      var filename = event.target.dataset.filename + '.csv';
      //call the export function on python and send all the ids of the rows
      new instance.web.Model(this.model)
        .call('export', [extractIds(this.records.records)], {
          context: instance.session.user_context,
        })
        .done(createCsv.bind(this, filename, type));
    },
    export_all_button: function(event) {
      var myids = extractIds(this.records.records);
      var filtered_ids = get_checked_rows(myids);
      var type = event.target.dataset.type;
      var filename = event.target.dataset.filename + '_completo.csv';
      if(filtered_ids.length > 0){
        //if there were some selected rows then filter the ids
        myids = filtered_ids;
      }
      else{
        //if none is selected then export all

      }
        //call the export all function on python and send the ids of the rows we need to export
       new instance.web.Model(this.model)
        .call('export_all', [myids], {
          context: instance.session.user_context,
        })
        .done(createCsv.bind(this, filename, type));

    },
    stmp_all_button : function(event) {
      var myids = extractIds(this.records.records);
      var filtered_ids = get_checked_rows(myids);
      var type = event.target.dataset.type;
      var filename = event.target.dataset.filename + '_completo.csv';
      if(filtered_ids.length > 0){
        //if there were some selected rows then filter the ids
        myids = filtered_ids;
      }
      else{
        //if none is selected then export all

      }
        //call the export all function on python and send the ids of the rows we need to export
       new instance.web.Model(this.model)
        //.call('stamp_all_cfdi', [myids], {
        .call('action_invoice_cfdi_multi', [myids], {  
          context: instance.session.user_context,
        })
        //.done(createCsv.bind(this, filename, type));
      location.reload();  
    },
  });
};

function extractIds(records) {
    //get the ids of every row on an array
   return _.map(records, record => record.attributes.id);
}

function get_checked_rows(ids){
    //filter by tr > input to get only the ids of the rows which are checked
    var export_rows = [];
    var rows = $(".o_list_view > tbody > tr > td:first-child");
    for(var i = 0; i< rows.length; i++){
        var item = rows[i];
        var mychecked = item.children[0].children[0].checked;
        if(mychecked === true){
            export_rows.push(ids[i]);
        }
    }

    return export_rows;
}

function createCsv(filename, type, source) {
  //create the file with the information we got from the model
  var encodedUri = encodeURI('data:text/csv;charset=utf-8,' + source);
  var link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
}
