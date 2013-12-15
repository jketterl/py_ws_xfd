Ext.define('xfd.data.proxy.Socket', {
    extend:'Ext.data.proxy.Proxy',
    alias:'proxy.socket',
    requires:[
        'xfd.socket.Socket',
        'xfd.socket.Command'
    ],
    constructor:function(){
        this.callParent(arguments);
        this.socket = this.socket || xfd.socket.Socket.getInstance();
    },
    create:function(operation, callback, scope){
        var me = this, 
            record = operation.getRecords()[0],
            command = Ext.create('xfd.socket.Command', 'add', me.module, record.getData(), function(command){
            operation.setSuccessful(command.wasSuccessful());
            operation.setCompleted();
            if (command.wasSuccessful()) record.set(command.getResult());

            Ext.callback(callback, scope || me, [operation]);
        });
        this.socket.sendCommand(command);
    }
});
