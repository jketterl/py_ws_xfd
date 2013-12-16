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
        return this.updateOperation(operation, 'add', callback, scope);
    },
    updateOperation:function(operation, method,  callback, scope){
        var me = this, 
            record = operation.getRecords()[0],
            request = Ext.create('Ext.data.Request', {
                operation:operation
            }),
            data = me.getWriter().write(request).jsonData,
            command = Ext.create('xfd.socket.Command', method, me.module, data, function(command){
                operation.setCompleted();
                if (command.wasSuccessful()) {
                    operation.setSuccessful();
                    record.set(command.getResult());
                } else {
                    me.fireEvent('exception', me, null, operation);
                }

                Ext.callback(callback, scope || me, [operation]);
            });
        me.socket.sendCommand(command);
    },
    read:function(operation, callback, scope){
        var me = this,
            command = Ext.create('xfd.socket.Command', 'read', me.module, {}, function(command) {
                operation.setCompleted();
                if (command.wasSuccessful()) {
                    var result = operation.resultSet = me.getReader().read(command.getResult());
                    if (result.success) operation.setSuccessful();
                } else {
                    me.fireEvent('exception', me, null, operation);
                }
                Ext.callback(callback, scope || me, [operation]);
            });
        me.socket.sendCommand(command);
    },
    update:function(operation, callback, scope){
        return this.updateOperation(operation, 'write', callback, scope);
    }
});
