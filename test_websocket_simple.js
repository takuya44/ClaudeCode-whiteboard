const WebSocket = require('ws');

// 簡単なWebSocketテスト
const testSimpleWebSocket = async () => {
  const wsUrl = 'ws://localhost:8000/ws/test';
  
  console.log('Connecting to simple WebSocket:', wsUrl);
  
  const ws = new WebSocket(wsUrl);
  
  ws.on('open', () => {
    console.log('✅ Simple WebSocket connection opened');
  });
  
  ws.on('message', (data) => {
    console.log('📥 Received message:', data.toString());
  });
  
  ws.on('close', (code, reason) => {
    console.log(`🔌 WebSocket closed with code ${code}:`, reason.toString());
    process.exit(0);
  });
  
  ws.on('error', (error) => {
    console.error('❌ WebSocket error:', error);
  });
};

testSimpleWebSocket();