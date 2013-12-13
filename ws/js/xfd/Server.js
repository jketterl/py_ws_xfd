Ext.define('xfd.Server', {
    extend:'Ext.data.Model',
    fields:[
        {name:'name', type:'String'},
        {name:'host', type:'String'},
        {name:'port', type:'Integer', defaultValue:80},
        {name:'https', type:'Boolean', defaultValue:false},
        {name:'user', type:'String'},
        {name:'token', type:'String'}
    ]
});
