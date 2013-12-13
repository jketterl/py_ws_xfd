var start = function(){
    Ext.Loader.setConfig({
        enabled:true,
        paths:{
            "xfd":"js/xfd"
        }
    });

    var serverList = Ext.create('xfd.ServerList', {
        region:'west',
        split:true,
        width:200
    });

    var serverForm = Ext.create('xfd.ServerForm', {
        title:'Server config',
        region:'center',
        frame:true,
        bodyStyle:{ padding:'15px' },
        disabled:true
    });

    serverList.on('select', function(grid, record){
        serverForm.loadRecord(record);
        serverForm.enable();
    });

    var viewport = Ext.create('Ext.container.Viewport', {
        layout:'fit',
        items:[Ext.create('Ext.tab.Panel', {
            items:[{
                    title:'Projects'
                },{
                    title:'Servers',
                    layout:'border',
                    items:[serverList, serverForm]
                }]
        })]
    });
};

Ext.onReady(start)
