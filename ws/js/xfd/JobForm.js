Ext.define('xfd.JobForm', {
    extend:'Ext.form.Panel',
    requires:[
        'xfd.Server',
        'xfd.JenkinsJob',
        'xfd.Output'
    ],
    defaults:{ width: 400, labelWidth:120 },
    items:[{
    },],
    initComponent:function(){
        var me = this;

        var serverCombo = Ext.create('Ext.form.field.ComboBox', {
            fieldLabel:'Server',
            name:'server_id',
            valueField:'id',
            displayField:'name',
            store:{
                model:'xfd.Server'
            }
        });

        var jobCombo = Ext.create('Ext.form.field.ComboBox', {
            fieldLabel:'Name',
            name:'name',
            store:{
                model:'xfd.JenkinsJob'
            },
            displayField:'name',
            valueField:'name'
        });

        var outputCombo = Ext.create('Ext.form.field.ComboBox', {
            fieldLabel:'Output',
            name:'output_id',
            valueField:'id',
            displayField:'name',
            store:{
                model:'xfd.Output'
            }
        });

        serverCombo.on('select', function(combo, records){
            var server = records[0];
            jobCombo.bindStore(server.getJobs());
        });

        me.items = [
            serverCombo,
            jobCombo,
            outputCombo
        ];

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
