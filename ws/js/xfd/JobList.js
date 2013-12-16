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

        me.on('render', function(){
            me.getStore().load();
        });

        me.callParent(arguments);
    }
});
