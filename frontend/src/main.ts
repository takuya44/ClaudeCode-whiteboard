// Vue 3 Application Entry Point
// このファイルは実装計画書に従って各担当者が実装してください

import { createApp } from 'vue'
import App from './App.vue'

// TODO: フロントエンド担当者Aが以下を実装
// - router/index.ts (ルーティング)
// - stores/index.ts (状態管理)
// - plugins/index.ts (プラグイン設定)

// TODO: フロントエンド担当者Bが以下を実装
// - composables/useCanvas.ts (Canvas機能)
// - composables/useWebSocket.ts (WebSocket機能)
// - utils/drawing.ts (描画ユーティリティ)

const app = createApp(App)

// プラグイン・ストア・ルーターを設定
// app.use(router)
// app.use(store)

app.mount('#app')