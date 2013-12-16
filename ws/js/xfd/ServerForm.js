Ext.define('xfd.ServerForm', {
    extend:'Ext.form.Panel',
    defaults:{ width: 400, labelWidth:120 },
    items:[{
        xtype:'textfield',
        fieldLabel:'Name',
        name:'name'
    }, {
        xtype:'textfield',
        fieldLabel:'Hostname / IP',
        name:'host'
    }, {
        xtype:'numberfield',
        fieldLabel:'Port',
        name:'port',
        hideTrigger:true
    }, {
        xtype:'numberfield',
        fieldLabel:'WebSocket Port <img src="img/icons/information.png" data-qtip="Installation of the Jenkins WebSocket plugin is strongly recommended, since it allows direct push of project status changes.">',
        name:'wsPort',
        hideTrigger:true
    }, {
        xtype:'checkbox',
        fieldLabel:'Use HTTPS',
        name:'https'
    }, {
        xtype:'textfield',
        fieldLabel:'Username',
        name:'user'
    }, {
        xtype:'textfield',
        fieldLabel:'Access Token',
        name:'token'
    }],
    initComponent:function(){
        var me = this;
        me.dockedItems = [{
            dock:'bottom',
            xtype:'toolbar',
            items:[{
                xtype:'button',
                text:'Save',
                handler:function(){
                    var form = me.getForm(),
                        record = form.getRecord();
                    form.updateRecord();
                    record.save({
                        callback:function(records, operation){
                            if (operation.wasSuccessful()) {
                                record.commit();
                            }
                        }
                    });
                }
            }]
        }];

        me.callParent(arguments);
    }
});
