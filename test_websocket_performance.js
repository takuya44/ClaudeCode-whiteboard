const WebSocket = require('ws');

// WebSocketパフォーマンステスト
const testWebSocketPerformance = async () => {
  console.log('⚡ Testing WebSocket performance...\n');
  
  const whiteboardId = 'performance-test';
  const client1 = new WebSocket(`ws://localhost:8000/ws/${whiteboardId}?userId=perf-user-1&token=test-token`);
  const client2 = new WebSocket(`ws://localhost:8000/ws/${whiteboardId}?userId=perf-user-2&token=test-token`);
  
  let connectionsReady = 0;
  let messagesReceived = 0;
  let messagesSent = 0;
  const latencies = [];
  
  const waitForConnections = () => {
    return new Promise((resolve) => {
      const checkReady = () => {
        if (connectionsReady === 2) {
          resolve();
        }
      };
      
      client1.on('open', () => {
        console.log('✅ Performance client 1 connected');
        connectionsReady++;
        checkReady();
      });
      
      client2.on('open', () => {
        console.log('✅ Performance client 2 connected');
        connectionsReady++;
        checkReady();
      });
    });
  };
  
  // Client 2のメッセージハンドラー（レシーバー）
  client2.on('message', (data) => {
    const message = JSON.parse(data);
    if (message.type === 'draw' && message.data && message.data.element) {
      const receivedAt = Date.now();
      const sentAt = message.data.element.sentAt;
      if (sentAt) {
        const latency = receivedAt - sentAt;
        latencies.push(latency);
        messagesReceived++;
      }
    }
  });
  
  await waitForConnections();
  
  console.log('🎯 Starting latency test...');
  
  // 100メッセージを送信してレイテンシーを測定
  const messageCount = 100;
  const sendInterval = 50; // 50ms間隔
  
  const startTime = Date.now();
  
  for (let i = 0; i < messageCount; i++) {
    const sentAt = Date.now();
    const drawingMessage = {
      type: 'draw',
      data: {
        element: {
          id: `perf-element-${i}`,
          type: 'pen',
          points: [
            { x: 100 + i, y: 100 + i },
            { x: 150 + i, y: 150 + i }
          ],
          color: '#FF0000',
          strokeWidth: 2,
          whiteboardId: whiteboardId,
          userId: 'perf-user-1',
          sentAt: sentAt
        }
      },
      userId: 'perf-user-1',
      timestamp: new Date().toISOString()
    };
    
    client1.send(JSON.stringify(drawingMessage));
    messagesSent++;
    
    // 次のメッセージを送信する前に待機
    await new Promise(resolve => setTimeout(resolve, sendInterval));
  }
  
  // 全てのメッセージが受信されるまで待機
  await new Promise(resolve => {
    const checkComplete = setInterval(() => {
      if (messagesReceived >= messageCount) {
        clearInterval(checkComplete);
        resolve();
      }
    }, 100);
    
    // タイムアウト（10秒）
    setTimeout(() => {
      clearInterval(checkComplete);
      resolve();
    }, 10000);
  });
  
  const endTime = Date.now();
  const totalTime = endTime - startTime;
  
  // パフォーマンス統計を計算
  const avgLatency = latencies.length > 0 ? latencies.reduce((a, b) => a + b, 0) / latencies.length : 0;
  const minLatency = latencies.length > 0 ? Math.min(...latencies) : 0;
  const maxLatency = latencies.length > 0 ? Math.max(...latencies) : 0;
  const throughput = (messagesReceived / (totalTime / 1000)).toFixed(2);
  const lossRate = ((messagesSent - messagesReceived) / messagesSent * 100).toFixed(2);
  
  console.log('\n📊 Performance Results:');
  console.log(`   Messages sent: ${messagesSent}`);
  console.log(`   Messages received: ${messagesReceived}`);
  console.log(`   Message loss rate: ${lossRate}%`);
  console.log(`   Total time: ${totalTime}ms`);
  console.log(`   Average latency: ${avgLatency.toFixed(2)}ms`);
  console.log(`   Min latency: ${minLatency}ms`);
  console.log(`   Max latency: ${maxLatency}ms`);
  console.log(`   Throughput: ${throughput} messages/sec`);
  
  // メモリ使用量の確認
  const memUsage = process.memoryUsage();
  console.log('\n💾 Memory Usage:');
  console.log(`   RSS: ${(memUsage.rss / 1024 / 1024).toFixed(2)} MB`);
  console.log(`   Heap Used: ${(memUsage.heapUsed / 1024 / 1024).toFixed(2)} MB`);
  console.log(`   Heap Total: ${(memUsage.heapTotal / 1024 / 1024).toFixed(2)} MB`);
  
  // パフォーマンス評価
  console.log('\n🏆 Performance Assessment:');
  
  if (lossRate < 1) {
    console.log('   ✅ Message delivery: EXCELLENT (< 1% loss)');
  } else if (lossRate < 5) {
    console.log('   ⚠️  Message delivery: GOOD (< 5% loss)');
  } else {
    console.log('   ❌ Message delivery: POOR (>= 5% loss)');
  }
  
  if (avgLatency < 100) {
    console.log('   ✅ Latency: EXCELLENT (< 100ms)');
  } else if (avgLatency < 500) {
    console.log('   ⚠️  Latency: GOOD (< 500ms)');
  } else {
    console.log('   ❌ Latency: POOR (>= 500ms)');
  }
  
  if (throughput > 10) {
    console.log('   ✅ Throughput: EXCELLENT (> 10 msg/sec)');
  } else if (throughput > 5) {
    console.log('   ⚠️  Throughput: GOOD (> 5 msg/sec)');
  } else {
    console.log('   ❌ Throughput: POOR (<= 5 msg/sec)');
  }
  
  // 接続を閉じる
  client1.close();
  client2.close();
  
  console.log('\n✅ Performance test completed');
};

testWebSocketPerformance().catch(console.error);