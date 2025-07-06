const WebSocket = require('ws');

const testWebSocket = async () => {
  console.log('Testing WebSocket connection...');
  
  const ws = new WebSocket('ws://localhost:8001/ws/test-whiteboard?userId=test-user&token=test-token');
  
  ws.on('open', () => {
    console.log('✓ WebSocket connection opened successfully');
    
    // Send a test message
    const testMessage = {
      type: 'ping',
      data: {},
      userId: 'test-user',
      timestamp: new Date().toISOString()
    };
    
    ws.send(JSON.stringify(testMessage));
    console.log('✓ Test message sent');
    
    // Close connection after 2 seconds
    setTimeout(() => {
      ws.close();
    }, 2000);
  });
  
  ws.on('message', (data) => {
    console.log('✓ Received message:', data.toString());
  });
  
  ws.on('close', (code, reason) => {
    console.log('✓ WebSocket connection closed:', code, reason.toString());
  });
  
  ws.on('error', (error) => {
    console.error('✗ WebSocket connection error:', error);
  });
};

testWebSocket().catch(console.error);