# コーディング規約

## 📋 全般的なルール

### 1. 基本方針
- **可読性を重視**: 他の開発者が理解しやすいコード
- **一貫性を保つ**: プロジェクト全体で統一されたスタイル
- **保守性を考慮**: 変更・拡張しやすい構造

### 2. 言語・フレームワーク
- **フロントエンド**: TypeScript, Vue 3 Composition API
- **バックエンド**: Python 3.10, FastAPI
- **コードフォーマッター**: Prettier (Frontend), Black (Backend)
- **リンター**: ESLint (Frontend), Flake8 (Backend)

## 🎨 フロントエンド規約

### TypeScript/Vue 3

#### 1. ファイル構成
```
src/
├── components/          # 再利用可能コンポーネント
│   ├── common/         # 汎用コンポーネント
│   ├── whiteboard/     # ホワイトボード固有
│   └── ui/            # UIコンポーネント
├── composables/        # Composition API
├── stores/            # 状態管理
├── types/             # 型定義
├── utils/             # ユーティリティ
└── views/             # ページコンポーネント
```

#### 2. 命名規則
```typescript
// ファイル名: PascalCase
// ButtonComponent.vue
// WhiteboardCanvas.vue

// 変数・関数: camelCase
const userName = 'John'
const fetchUserData = () => {}

// 定数: SCREAMING_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com'

// 型: PascalCase
interface UserData {
  id: number
  name: string
}

// Enum: PascalCase
enum DrawingTool {
  Pen = 'pen',
  Eraser = 'eraser'
}
```

#### 3. Vue コンポーネント
```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Props定義
interface Props {
  title: string
  isActive?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isActive: false
})

// Emits定義
interface Emits {
  update: [value: string]
  close: []
}

const emit = defineEmits<Emits>()

// リアクティブデータ
const count = ref(0)
const doubleCount = computed(() => count.value * 2)

// ライフサイクル
onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <div class="component-container">
    <h2>{{ props.title }}</h2>
    <p>Count: {{ count }}</p>
  </div>
</template>

<style scoped>
.component-container {
  padding: 1rem;
}
</style>
```

#### 4. Composables
```typescript
// useWhiteboard.ts
import { ref, reactive } from 'vue'

export function useWhiteboard() {
  const isDrawing = ref(false)
  const currentTool = ref('pen')
  
  const state = reactive({
    strokes: [],
    selectedColor: '#000000'
  })
  
  const startDrawing = (x: number, y: number) => {
    isDrawing.value = true
    // 描画開始処理
  }
  
  return {
    isDrawing,
    currentTool,
    state,
    startDrawing
  }
}
```

## 🐍 バックエンド規約

### Python/FastAPI

#### 1. ファイル構成
```
backend/
├── app/
│   ├── core/           # 設定・共通処理
│   ├── models/         # データベースモデル
│   ├── schemas/        # Pydanticスキーマ
│   ├── api/           # APIルーター
│   ├── services/       # ビジネスロジック
│   ├── utils/          # ユーティリティ
│   └── websocket/      # WebSocket処理
├── tests/             # テストコード
└── main.py           # アプリケーションエントリーポイント
```

#### 2. 命名規則
```python
# ファイル名: snake_case
# user_service.py
# whiteboard_model.py

# 変数・関数: snake_case
user_name = "John"
def fetch_user_data():
    pass

# 定数: SCREAMING_SNAKE_CASE
API_BASE_URL = "https://api.example.com"
MAX_CONNECTIONS = 100

# クラス: PascalCase
class UserService:
    pass

class WhiteboardModel:
    pass
```

#### 3. FastAPI エンドポイント
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.whiteboard import WhiteboardCreate, WhiteboardResponse
from app.services.whiteboard_service import WhiteboardService
from app.core.database import get_db

router = APIRouter(prefix="/whiteboards", tags=["whiteboards"])

@router.post("/", response_model=WhiteboardResponse)
async def create_whiteboard(
    whiteboard_data: WhiteboardCreate,
    db: Session = Depends(get_db)
) -> WhiteboardResponse:
    """
    新しいホワイトボードを作成する
    
    Args:
        whiteboard_data: ホワイトボード作成データ
        db: データベースセッション
        
    Returns:
        作成されたホワイトボード情報
        
    Raises:
        HTTPException: 作成に失敗した場合
    """
    try:
        service = WhiteboardService(db)
        return await service.create_whiteboard(whiteboard_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### 4. Pydanticスキーマ
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WhiteboardBase(BaseModel):
    """ホワイトボード基底スキーマ"""
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class WhiteboardCreate(WhiteboardBase):
    """ホワイトボード作成スキーマ"""
    pass

class WhiteboardResponse(WhiteboardBase):
    """ホワイトボードレスポンススキーマ"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

## 🧪 テスト規約

### フロントエンドテスト
```typescript
// Button.test.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ButtonComponent from '../ButtonComponent.vue'

describe('ButtonComponent', () => {
  it('should render with correct text', () => {
    const wrapper = mount(ButtonComponent, {
      props: {
        text: 'Click me'
      }
    })
    
    expect(wrapper.text()).toBe('Click me')
  })
  
  it('should emit click event', async () => {
    const wrapper = mount(ButtonComponent)
    
    await wrapper.trigger('click')
    
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```

### バックエンドテスト
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestWhiteboardAPI:
    """ホワイトボードAPI テストクラス"""
    
    def test_create_whiteboard(self):
        """ホワイトボード作成テスト"""
        whiteboard_data = {
            "title": "Test Whiteboard",
            "description": "Test description"
        }
        
        response = client.post("/whiteboards/", json=whiteboard_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == whiteboard_data["title"]
        assert "id" in data
    
    def test_create_whiteboard_invalid_data(self):
        """無効データでのホワイトボード作成テスト"""
        whiteboard_data = {"title": ""}  # 空のタイトル
        
        response = client.post("/whiteboards/", json=whiteboard_data)
        
        assert response.status_code == 422
```

## 🔧 コードフォーマット・リント

### フロントエンド設定

#### .eslintrc.js
```javascript
module.exports = {
  extends: [
    '@vue/typescript/recommended',
    'prettier'
  ],
  rules: {
    'vue/component-name-in-template-casing': ['error', 'PascalCase'],
    '@typescript-eslint/no-unused-vars': 'error',
    'prefer-const': 'error'
  }
}
```

#### prettier.config.js
```javascript
module.exports = {
  semi: false,
  singleQuote: true,
  tabWidth: 2,
  trailingComma: 'es5'
}
```

### バックエンド設定

#### pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py310']

[tool.flake8]
max-line-length = 88
extend-ignore = E203, W503

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

## 📝 コメント・ドキュメント

### TSDoc (フロントエンド)
```typescript
/**
 * ホワイトボードキャンバスコンポーネント
 * 
 * @param props - コンポーネントプロパティ
 * @param props.width - キャンバス幅
 * @param props.height - キャンバス高さ
 * @returns 描画可能なキャンバス要素
 */
export const WhiteboardCanvas = (props: CanvasProps) => {
  // 実装
}
```

### Docstring (バックエンド)
```python
def create_whiteboard(self, data: WhiteboardCreate) -> Whiteboard:
    """
    新しいホワイトボードを作成する
    
    Args:
        data (WhiteboardCreate): ホワイトボード作成データ
        
    Returns:
        Whiteboard: 作成されたホワイトボードオブジェクト
        
    Raises:
        ValueError: 無効なデータが提供された場合
        DatabaseError: データベース操作でエラーが発生した場合
    """
```

## 🚀 コマンド

### コード品質チェック
```bash
# フロントエンド
make lint-frontend
make format-frontend

# バックエンド  
make lint-backend
make format-backend

# 全体
make lint
make format
```

## 📊 品質基準

### コードレビュー必須項目
- [ ] 命名規則に従っている
- [ ] 適切なコメント・ドキュメント
- [ ] テストが含まれている
- [ ] リント・フォーマットチェック通過
- [ ] 型定義が適切
- [ ] エラーハンドリングが適切

### パフォーマンス考慮
- 不要な再レンダリング回避
- 適切なメモ化
- データベースクエリ最適化
- WebSocket接続効率化