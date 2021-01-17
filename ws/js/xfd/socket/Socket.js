Ext.define('xfd.socket.Socket', {
	extend:'Ext.util.Observable',
	statics:{
		instance:null,
		getInstance:function(){
			if (this.instance == null) this.instance = new this();
			return this.instance;
		}
	},
	constructor:function(){
		this.queue = [];
		this.requestCount = 0;
		this.requests = [];
		this.addEvents('open', 'close', 'update');
		this.callParent(arguments);
	},
	connect:function(){
		var me = this;
		if (!me.socket) {
			console.info('connecting to server');
            var protocol = window.location.protocol.match(/https/) ? 'wss' : 'ws';

            var href = window.location.href;
            var index = href.lastIndexOf('/');
            if (index > 0) {
                href = href.substr(0, index + 1);
            }
            href = href.split('://')[1];
            href = protocol + '://' + href;
            if (!href.endsWith('/')) {
                href += '/';
            }
            var ws_url = href + "socket";
			me.socket = new WebSocket(ws_url);
			me.socket.onopen = function(){
				console.info('socket is now open!');
				me.onConnect();
				me.socket.onmessage = function(event){
					if (event.type != 'message') return;
					var data = JSON.parse(event.data);
					if (typeof(data.sequence) != 'undefined' && me.requests[data.sequence]) {
						var command = me.requests[data.sequence];
						command.updateResult(data);
					} else if (data.event && data.event == 'update') {
						me.fireEvent('update', data.data);
					}
				};
				me.socket.onerror = function(){
					console.info(arguments);
				}

				me.fireEvent('open', me);
			};
			me.socket.onclose = function(){
				me.reconnect();
			};
		};
	},
	disconnect:function(){
		var me = this;
		if (!me.socket) return;
		me.fireEvent('close', me);
		me.socket.close();
		delete me.socket;
	},
	reconnect:function(){
		var me = this;
		me.disconnect();
		setTimeout(function(){
			me.connect();
		}, 10000);
	},
	sendCommand:function(command){
		if (this.queue) {
			this.connect();
			this.queue.push(command);
			return;
		}
		this.requests[this.requestCount] = command;
		command.setRequestId(this.requestCount++);
		this.socket.send(command.getJSON());
	},
	onConnect:function(){
		var me = this;
		if (me.queue) {
			var queue = me.queue;
			delete(me.queue);
			queue.forEach(function(command){
				me.sendCommand(command);
			});
		}
	}
});
