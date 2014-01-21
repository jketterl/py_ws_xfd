Ext.define('xfd.Server', {
    requires:[
        'xfd.data.proxy.Socket',
        'xfd.JenkinsJob'
    ],
    extend:'Ext.data.Model',
    fields:[
        {name:'id', type:'Integer'},
        {name:'name', type:'String'},
        {name:'host', type:'String'},
        {name:'port', type:'Integer', defaultValue:8080},
        {name:'urlPrefix', type:'string'},
        {name:'wsPort', type:'Integer', defaultValue:8081},
        {name:'https', type:'Boolean', defaultValue:false},
        {name:'user', type:'String'},
        {name:'token', type:'String'},
        {name:'uuid', type:'String'}
    ],
    proxy:{
        type:'socket',
        module:'serverList'
    },
    getJobs:function(){
        var store = Ext.create('Ext.data.Store', {
            model:'xfd.JenkinsJob',
            proxy:{
                type:'socket',
                module:this.get('uuid'),
                reader:{
                    type:'json',
                    root:'jobs'
                }
            }
        });
        store.load();
        return store;
    }
});
