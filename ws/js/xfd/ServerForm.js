Ext.define('xfd.ServerForm', {
    extend:'Ext.form.Panel',
    defaults:{ width: 400 },
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
                    var form = me.getForm();
                    form.updateRecord();
                    form.getRecord().commit();
                }
            }]
        }];

        me.callParent(arguments);
    }
});
