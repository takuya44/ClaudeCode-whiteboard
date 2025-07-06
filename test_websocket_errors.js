const WebSocket = require('ws');

// WebSocketエラーハンドリングテスト
const testWebSocketErrors = async () => {
  console.log('🔍 Testing WebSocket error handling...\n');
  
  // 1. 無効なパラメータでの接続テスト
  console.log('1. Testing connection with missing parameters...');
  const invalidWs1 = new WebSocket('ws://localhost:8000/ws/test-whiteboard?token=test-token');
  
  invalidWs1.on('open', () => console.log('   ❌ Should not connect without userId'));
  invalidWs1.on('close', (code, reason) => {
    console.log(`   ✅ Connection properly rejected with code ${code}: ${reason.toString()}`);
  });
  invalidWs1.on('error', (error) => {
    console.log('   ✅ Connection error handled:', error.message);
  });
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // 2. 無効なJSONメッセージ送信テスト
  console.log('\n2. Testing invalid JSON message handling...');
  const validWs = new WebSocket('ws://localhost:8000/ws/test-whiteboard?userId=test-user&token=test-token');
  
  validWs.on('open', () => {
    console.log('   ✅ Valid connection established');
    
    // 無効なJSONを送信
    try {
      validWs.send('invalid json message');
      console.log('   📤 Sent invalid JSON message');
    } catch (error) {
      console.log('   ❌ Error sending message:', error.message);
    }
  });
  
  validWs.on('message', (data) => {
    const message = JSON.parse(data);
    console.log('   📥 Received:', message.type);
  });
  
  validWs.on('close', (code) => {
    console.log(`   🔌 Connection closed with code ${code}`);
  });
  
  validWs.on('error', (error) => {
    console.log('   ❌ WebSocket error:', error.message);
  });
  
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // 3. 突然の接続切断テスト
  console.log('\n3. Testing sudden disconnection...');
  const disconnectWs = new WebSocket('ws://localhost:8000/ws/test-whiteboard?userId=disconnect-user&token=test-token');
  
  disconnectWs.on('open', () => {
    console.log('   ✅ Connection established for disconnect test');
    
    // すぐに切断
    setTimeout(() => {
      console.log('   🔚 Forcefully closing connection...');
      disconnectWs.terminate();
    }, 1000);
  });
  
  disconnectWs.on('close', (code, reason) => {
    console.log(`   🔌 Disconnect test completed with code ${code}`);
  });
  
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // 4. 複数接続での1つの切断テスト
  console.log('\n4. Testing one client disconnect in multi-client scenario...');
  const client1 = new WebSocket('ws://localhost:8000/ws/multi-test?userId=multi-user-1&token=test-token');
  const client2 = new WebSocket('ws://localhost:8000/ws/multi-test?userId=multi-user-2&token=test-token');
  
  let connectionsReady = 0;
  
  client1.on('open', () => {
    console.log('   ✅ Multi-client 1 connected');
    connectionsReady++;
  });
  
  client2.on('open', () => {
    console.log('   ✅ Multi-client 2 connected');
    connectionsReady++;
  });
  
  client1.on('message', (data) => {
    const message = JSON.parse(data);
    if (message.type === 'user_leave') {
      console.log('   ✅ Client 1 received user_leave notification');
    }
  });
  
  client2.on('message', (data) => {
    const message = JSON.parse(data);
    if (message.type === 'user_join') {
      console.log('   ✅ Client 2 received user_join notification');
    }
  });
  
  // 両方の接続を待機してから一方を切断
  const waitForBoth = setInterval(() => {
    if (connectionsReady === 2) {
      clearInterval(waitForBoth);
      setTimeout(() => {
        console.log('   🔚 Disconnecting client 2...');
        client2.close();
      }, 2000);
    }
  }, 100);
  
  await new Promise(resolve => setTimeout(resolve, 5000));
  
  client1.close();
  
  console.log('\n✅ WebSocket error handling tests completed');
};

testWebSocketErrors().catch(console.error);