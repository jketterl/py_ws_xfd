Ext.define('xfd.Output', {
    extend:'Ext.data.Model',
    requires:['xfd.data.proxy.Socket'],
    fields:['id', 'name', 'offset', 'leds'],
    proxy:{
        type:'socket',
        module:'outputList'
    }
});
