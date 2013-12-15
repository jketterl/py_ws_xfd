Ext.define('xfd.socket.Command', {
	constructor:function(command, module, params, callback){
		this.command = command;
        this.module = module;
		this.params = params || {};
		this.callback = callback || Ext.emptyFn;
	},
	setRequestId:function(id){
		this.requestId = id;
	},
	getJSON:function(){
		var data = {
			command:this.command,
            module:this.module,
			params:this.params
		};
		if (typeof(this.requestId) != 'undefined') data.sequence = this.requestId;
		return JSON.stringify(data);
	},
	updateResult:function(data){
		this.success = data.success || false;
		this.result = data.data || {};
		this.callback(this);
	},
	wasSuccessful:function(){
		return this.success;
	},
	getResult:function(){
		return this.result;
	}
});
