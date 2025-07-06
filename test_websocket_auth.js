const WebSocket = require('ws');

const testWebSocketWithAuth = async () => {
  console.log('Testing WebSocket connection with authentication...');
  
  const userId = '16351c9d-faaa-47bd-a7ba-13be9afdc815';
  const whiteboardId = '536c414f-1d3c-466c-80e9-e0a8366cb86b';
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTI0MDM3NTcsInN1YiI6IjE2MzUxYzlkLWZhYWEtNDdiZC1hN2JhLTEzYmU5YWZkYzgxNSJ9.p0E8ERpKyOh8eOogHJpVhDe-g2pVCkhqpshdqtqyPiQ';
  
  const wsUrl = `ws://localhost:8001/ws/${whiteboardId}?userId=${userId}&token=${token}`;
  
  console.log('Connecting to:', wsUrl);
  
  const ws = new WebSocket(wsUrl);
  
  ws.on('open', () => {
    console.log('✓ WebSocket connection opened successfully');
    
    // Send a test drawing message
    const testMessage = {
      type: 'draw',
      data: {
        element: {
          type: 'pen',
          x: 100,
          y: 100,
          points: [{x: 100, y: 100}, {x: 150, y: 150}],
          color: '#000000',
          strokeWidth: 2
        }
      },
      userId: userId,
      timestamp: new Date().toISOString()
    };
    
    ws.send(JSON.stringify(testMessage));
    console.log('✓ Test drawing message sent');
    
    // Send ping
    setTimeout(() => {
      const pingMessage = {
        type: 'ping',
        data: {},
        userId: userId,
        timestamp: new Date().toISOString()
      };
      ws.send(JSON.stringify(pingMessage));
      console.log('✓ Ping message sent');
    }, 1000);
    
    // Close connection after 5 seconds
    setTimeout(() => {
      console.log('Closing connection...');
      ws.close();
    }, 5000);
  });
  
  ws.on('message', (data) => {
    console.log('✓ Received message:', JSON.parse(data.toString()));
  });
  
  ws.on('close', (code, reason) => {
    console.log('✓ WebSocket connection closed:', code, reason.toString());
  });
  
  ws.on('error', (error) => {
    console.error('✗ WebSocket connection error:', error);
  });
};

testWebSocketWithAuth().catch(console.error);