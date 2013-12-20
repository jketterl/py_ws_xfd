Ext.define('xfd.JobList', {
    extend:'Ext.grid.Panel',
    requires:['xfd.Job'],
    store:{
        model:'xfd.Job'
    },
    columns:[
        {header:'Name', dataIndex:'name', flex:1}
    ],
    initComponent:function(){
        var me = this;
        me.dockedItems = [{
            dock:'bottom',
            xtype:'toolbar',
            items:[{
                xtype:'button',
                text:'+',
                flex:1,
                handler:function(){
                    var job = Ext.create('xfd.Job');
                    me.store.add(job);
                    me.getSelectionModel().select(job);
                }
            },{
                xtype:'button',
                text:'-',
                flex:1,
                handler:function(){
                    var selection = me.getSelectionModel().getSelection();
                    if (!selection[0]) return;
                    selection[0].destroy({
                        callback:function(records, operation){
                            if (operation.wasSuccessful()) me.getStore().remove(selection[0]);
                        }
                    });
                }
            }]
        }];


        me.on('render', function(){
            me.getStore().load();
        });

        me.callParent(arguments);
    }
});
