const WebSocket = require('ws');

// 描画同期のテスト
const testDrawingSync = async () => {
  const whiteboardId = 'test-whiteboard-1';
  
  // クライアント1（描画者）
  const client1 = new WebSocket(`ws://localhost:8000/ws/${whiteboardId}?userId=user-1&token=test-token-1`);
  
  // クライアント2（観察者）
  const client2 = new WebSocket(`ws://localhost:8000/ws/${whiteboardId}?userId=user-2&token=test-token-2`);
  
  let connectionsReady = 0;
  
  const waitForConnections = () => {
    return new Promise((resolve) => {
      const checkReady = () => {
        if (connectionsReady === 2) {
          resolve();
        }
      };
      
      client1.on('open', () => {
        console.log('✅ Client 1 connected');
        connectionsReady++;
        checkReady();
      });
      
      client2.on('open', () => {
        console.log('✅ Client 2 connected');
        connectionsReady++;
        checkReady();
      });
    });
  };
  
  // Client 1のメッセージハンドラー
  client1.on('message', (data) => {
    const message = JSON.parse(data);
    console.log('📥 Client 1 received:', message.type, message.data);
  });
  
  // Client 2のメッセージハンドラー
  client2.on('message', (data) => {
    const message = JSON.parse(data);
    console.log('📥 Client 2 received:', message.type, message.data);
  });
  
  // 接続を待機
  await waitForConnections();
  
  console.log('\n🎨 Testing drawing synchronization...');
  
  // 描画要素の追加テスト
  const drawingElement = {
    type: 'draw',
    data: {
      element: {
        id: 'element-1',
        type: 'pen',
        points: [
          { x: 100, y: 100 },
          { x: 150, y: 150 },
          { x: 200, y: 100 }
        ],
        color: '#FF0000',
        strokeWidth: 3,
        whiteboardId: whiteboardId,
        userId: 'user-1'
      }
    },
    userId: 'user-1',
    timestamp: new Date().toISOString()
  };
  
  setTimeout(() => {
    console.log('📤 Client 1 sending drawing element...');
    client1.send(JSON.stringify(drawingElement));
  }, 1000);
  
  // 描画要素の更新テスト
  const updateElement = {
    type: 'draw',
    data: {
      element: {
        id: 'element-1',
        type: 'pen',
        points: [
          { x: 100, y: 100 },
          { x: 150, y: 150 },
          { x: 200, y: 100 },
          { x: 250, y: 150 }
        ],
        color: '#FF0000',
        strokeWidth: 3,
        whiteboardId: whiteboardId,
        userId: 'user-1'
      }
    },
    userId: 'user-1',
    timestamp: new Date().toISOString()
  };
  
  setTimeout(() => {
    console.log('📤 Client 1 updating drawing element...');
    client1.send(JSON.stringify(updateElement));
  }, 2000);
  
  // 描画要素の削除テスト
  const removeElement = {
    type: 'erase',
    data: {
      elementId: 'element-1',
      element: {
        id: 'element-1',
        whiteboardId: whiteboardId,
        userId: 'user-1'
      }
    },
    userId: 'user-1',
    timestamp: new Date().toISOString()
  };
  
  setTimeout(() => {
    console.log('📤 Client 1 removing drawing element...');
    client1.send(JSON.stringify(removeElement));
  }, 3000);
  
  // カーソル位置の更新テスト
  const cursorUpdate = {
    type: 'cursor',
    data: {
      x: 300,
      y: 200,
      userId: 'user-1'
    },
    userId: 'user-1',
    timestamp: new Date().toISOString()
  };
  
  setTimeout(() => {
    console.log('📤 Client 1 updating cursor position...');
    client1.send(JSON.stringify(cursorUpdate));
  }, 4000);
  
  // テスト終了
  setTimeout(() => {
    console.log('\n✅ Drawing synchronization test completed');
    client1.close();
    client2.close();
  }, 6000);
};

testDrawingSync().catch(console.error);