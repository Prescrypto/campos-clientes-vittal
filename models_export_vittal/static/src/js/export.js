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
      }

      // PERFORM THE ACTION
      btnExport.on('click', this.proxy('export_button'));
      btnExportAll.on('click', this.proxy('export_all_button'));
    },
    export_button: function(event) {
      var type = event.target.dataset.type;
      var filename = event.target.dataset.filename + '.csv';
      new instance.web.Model(this.model)
        .call('export', [extractIds(this.records.records)], {
          context: instance.session.user_context,
        })
        .done(createCsv.bind(this, filename, type));
    },
    export_all_button: function(event) {
      var type = event.target.dataset.type;
      var filename = event.target.dataset.filename + '.completo.csv';
      new instance.web.Model(this.model)
        .call('export_all', [extractIds(this.records.records)], {
          context: instance.session.user_context,
        })
        .done(createCsv.bind(this, filename, type));
    }
  });
};

function extractIds(records) {
   return _.map(records, record => record.attributes.id);
}

function get_checked_rows(){
    console.log("get checked");
     var self = this;
	 view = this.getParent();
	 children = view.getChildren();

     var export_columns_keys = [];
     var export_columns_names = [];
     var columns_tab = [];
     var rows_tab = [];
     console.log("get ths");
    // find the first tr of table for the columns labels
         view.$el.find('th.o_list_record_selector ').closest('tr').each(function (i, el) {
                 var ihtml = el.innerHTML + ''; // get html content of the tr
                 var extractedTdArray = ihtml.split("</th>") // split tr in array of th

            // get the text content of each th
                 extractedTdArray.forEach(function(elt){
                     var val = elt.substring(elt.indexOf(">") + 1)
                     if(val){
                         columns_tab.push(val)
                     }
                 });

         });

        console.log("get tds");
         var export_rows = [];
            // find the all ckecked rows
         view.$el.find('td.o_list_record_selector input:checked').closest('tr').each(function (i, el) {
                 rows_tab = []
                 var ihtml = el.innerHTML + '';
                 var extractedData = ihtml.split("</td>")
                 extractedData.forEach(function(elt){
                     var val = elt.substring(elt.indexOf(">") + 1) // get the td content
                     if(val != undefined){
                         if(val.indexOf(">") < 0 ){ // if the content of the td is not html content
                             rows_tab.push(val)
                         }
                     }
                 });
                 export_rows.push(rows_tab)
         });

    console.log(export_rows);
}

function createCsv(filename, type, source) {
  console.log(source);
  var encodedUri = encodeURI('data:text/csv;charset=utf-8,' + source);
  var link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
}
