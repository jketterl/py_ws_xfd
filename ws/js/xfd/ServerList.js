Ext.define('xfd.ServerList', {
    extend:'Ext.grid.Panel',
    model:'xfd.Server',
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
                    var server = Ext.create('xfd.Server');
                    me.store.add(server);
                    me.getSelectionModel().select(server);
                }
            },{
                xtype:'button',
                text:'-',
                flex:1,
                handler:function(){
                    var selection = me.getSelectionModel().getSelection();
                    if (!selection[0]) return;
                    me.store.remove(selection[0]);
                }
            }]
        }];

        me.callParent(arguments);
    }
});
