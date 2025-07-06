const WebSocket = require('ws');

// WebSocket接続テスト
const testWebSocketConnection = async () => {
  const wsUrl = 'ws://localhost:8000/ws/test-whiteboard-1?userId=test-user-1&token=test-token';
  
  console.log('Connecting to WebSocket:', wsUrl);
  
  const ws = new WebSocket(wsUrl);
  
  ws.on('open', () => {
    console.log('✅ WebSocket connection opened');
    
    // テストメッセージを送信
    const testMessage = {
      type: 'test',
      data: { message: 'Hello from test client' },
      userId: 'test-user-1',
      timestamp: new Date().toISOString()
    };
    
    ws.send(JSON.stringify(testMessage));
    console.log('📤 Sent test message:', testMessage);
  });
  
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data);
      console.log('📥 Received message:', message);
    } catch (error) {
      console.error('❌ Failed to parse message:', error);
    }
  });
  
  ws.on('close', (code, reason) => {
    console.log(`🔌 WebSocket closed with code ${code}:`, reason.toString());
  });
  
  ws.on('error', (error) => {
    console.error('❌ WebSocket error:', error);
  });
  
  // 5秒後に接続を閉じる
  setTimeout(() => {
    console.log('🔚 Closing WebSocket connection...');
    ws.close();
  }, 5000);
};

testWebSocketConnection();