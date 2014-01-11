Ext.define('xfd.Job', {
    extend:'Ext.data.Model',
    requires:['xfd.data.proxy.Socket'],
    fields:[
        {name:'id', type:'integer'},
        {name:'name', type:'string'},
        {name:'server_id', type:'integer'},
        {name:'output_id', type:'ingeger'}
    ],
    proxy:{
        type:'socket',
        module:'jobList'
    }
});
