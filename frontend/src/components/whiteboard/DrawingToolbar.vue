<template>
  <div class="drawing-toolbar bg-white rounded-lg shadow-lg p-4 border border-gray-200">
    <!-- Tool Selection -->
    <div class="flex flex-wrap gap-2 mb-4">
      <button
        v-for="drawingTool in tools"
        :key="drawingTool.type"
        :class="[
          'flex items-center justify-center w-10 h-10 rounded-lg border-2 transition-all duration-200',
          selectedTool === drawingTool.type
            ? 'border-blue-500 bg-blue-50 text-blue-600'
            : 'border-gray-300 bg-white text-gray-600 hover:border-gray-400 hover:bg-gray-50'
        ]"
        :title="drawingTool.label"
        @click="selectTool(drawingTool.type)"
      >
        <component
          :is="drawingTool.icon"
          class="w-5 h-5"
        />
      </button>
    </div>

    <!-- Color Picker -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Color
      </label>
      <div class="flex items-center gap-2">
        <input
          v-model="currentColor"
          type="color"
          class="w-8 h-8 rounded border border-gray-300 cursor-pointer"
          @change="updateColor"
        >
        <div class="flex gap-1">
          <button
            v-for="color in presetColors"
            :key="color"
            :class="[
              'w-6 h-6 rounded border-2 cursor-pointer transition-all duration-200',
              currentColor === color
                ? 'border-gray-800 scale-110'
                : 'border-gray-300 hover:border-gray-500'
            ]"
            :style="{ backgroundColor: color }"
            :title="color"
            @click="setColor(color)"
          />
        </div>
      </div>
    </div>

    <!-- Stroke Width -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Stroke Width: {{ strokeWidth }}px
      </label>
      <input
        v-model.number="strokeWidth"
        type="range"
        min="1"
        max="20"
        step="1"
        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
        @input="updateStrokeWidth"
      >
      <div class="flex justify-between text-xs text-gray-500 mt-1">
        <span>1px</span>
        <span>20px</span>
      </div>
    </div>

    <!-- Fill Color (for shapes) -->
    <div
      v-if="showFillOptions"
      class="mb-4"
    >
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Fill
      </label>
      <div class="flex items-center gap-2">
        <input
          v-model="fillColor"
          type="color"
          class="w-8 h-8 rounded border border-gray-300 cursor-pointer"
          @change="updateFillColor"
        >
        <span class="text-sm text-gray-600">Fill Color</span>
      </div>
    </div>

    <!-- Font Size (for text) -->
    <div
      v-if="selectedTool === 'text'"
      class="mb-4"
    >
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Font Size: {{ fontSize }}px
      </label>
      <input
        v-model.number="fontSize"
        type="range"
        min="12"
        max="72"
        step="2"
        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
        @input="updateFontSize"
      >
      <div class="flex justify-between text-xs text-gray-500 mt-1">
        <span>12px</span>
        <span>72px</span>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-2 pt-4 border-t border-gray-200">
      <button
        :disabled="!canUndo"
        :class="[
          'flex items-center justify-center w-10 h-10 rounded-lg border transition-all duration-200',
          canUndo
            ? 'border-gray-300 bg-white text-gray-600 hover:border-gray-400 hover:bg-gray-50'
            : 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
        ]"
        title="Undo"
        @click="undo"
      >
        <UndoIcon class="w-5 h-5" />
      </button>
      
      <button
        :disabled="!canRedo"
        :class="[
          'flex items-center justify-center w-10 h-10 rounded-lg border transition-all duration-200',
          canRedo
            ? 'border-gray-300 bg-white text-gray-600 hover:border-gray-400 hover:bg-gray-50'
            : 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
        ]"
        title="Redo"
        @click="redo"
      >
        <RedoIcon class="w-5 h-5" />
      </button>
      
      <button
        class="flex items-center justify-center w-10 h-10 rounded-lg border border-red-300 bg-white text-red-600 hover:border-red-400 hover:bg-red-50 transition-all duration-200"
        title="Clear Canvas"
        @click="clear"
      >
        <TrashIcon class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { DrawingTool } from '@/types'

// Icons (you can replace these with your preferred icon library)
const PenIcon = () => 'pen'
const LineIcon = () => 'line'
const RectangleIcon = () => 'rectangle'
const CircleIcon = () => 'circle'
const TextIcon = () => 'text'
const EraserIcon = () => 'eraser'
const SelectIcon = () => 'select'
const UndoIcon = () => 'undo'
const RedoIcon = () => 'redo'
const TrashIcon = () => 'trash'

interface Props {
  tool: DrawingTool
  canUndo?: boolean
  canRedo?: boolean
}

interface Emits {
  (e: 'update:tool', tool: DrawingTool): void
  (e: 'undo'): void
  (e: 'redo'): void
  (e: 'clear'): void
}

const props = withDefaults(defineProps<Props>(), {
  canUndo: false,
  canRedo: false
})

const emit = defineEmits<Emits>()

// Tools configuration
const tools = [
  { type: 'pen', label: 'Pen', icon: PenIcon },
  { type: 'line', label: 'Line', icon: LineIcon },
  { type: 'rectangle', label: 'Rectangle', icon: RectangleIcon },
  { type: 'circle', label: 'Circle', icon: CircleIcon },
  { type: 'text', label: 'Text', icon: TextIcon },
  { type: 'eraser', label: 'Eraser', icon: EraserIcon },
  { type: 'select', label: 'Select', icon: SelectIcon }
] as const

// Preset colors
const presetColors = [
  '#000000', '#FF0000', '#00FF00', '#0000FF',
  '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500',
  '#800080', '#008000', '#000080', '#808080'
]

// Local state
const selectedTool = ref(props.tool.type)
const currentColor = ref(props.tool.color)
const strokeWidth = ref(props.tool.strokeWidth)
const fillColor = ref(props.tool.fill || '#ffffff')  // デフォルトを白色に設定
const fontSize = ref(props.tool.fontSize || 16)

// Computed properties
const showFillOptions = computed(() => {
  return ['rectangle', 'circle'].includes(selectedTool.value)
})

// Methods
const selectTool = (toolType: DrawingTool['type']) => {
  selectedTool.value = toolType
  updateTool()
}

const setColor = (color: string) => {
  currentColor.value = color
  updateTool()
}

const updateColor = () => {
  updateTool()
}

const updateStrokeWidth = () => {
  updateTool()
}

const updateFillColor = () => {
  updateTool()
}

const updateFontSize = () => {
  updateTool()
}

const updateTool = () => {
  const updatedTool: DrawingTool = {
    type: selectedTool.value,
    color: currentColor.value,
    strokeWidth: strokeWidth.value,
    fill: fillColor.value,
    fontSize: fontSize.value
  }
  
  emit('update:tool', updatedTool)
}

const undo = () => {
  emit('undo')
}

const redo = () => {
  emit('redo')
}

const clear = () => {
  if (confirm('Are you sure you want to clear the canvas? This action cannot be undone.')) {
    emit('clear')
  }
}

// Watch for external tool changes
watch(() => props.tool, (newTool) => {
  selectedTool.value = newTool.type
  currentColor.value = newTool.color
  strokeWidth.value = newTool.strokeWidth
  fillColor.value = newTool.fill || '#ffffff'  // デフォルトを白色に設定
  fontSize.value = newTool.fontSize || 16
}, { deep: true })

</script>

<style scoped>
.slider::-webkit-slider-thumb {
  appearance: none;
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.slider::-moz-range-thumb {
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
