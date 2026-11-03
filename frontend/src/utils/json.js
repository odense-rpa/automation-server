// Shared helpers for JsonPreview and JsonTree.

export function jsonType(value) {
  if (value === null || value === undefined) return 'null'
  if (Array.isArray(value)) return 'array'
  return typeof value // 'object' | 'string' | 'number' | 'boolean'
}

export function isContainer(value) {
  const type = jsonType(value)
  return type === 'object' || type === 'array'
}

export function childCount(value) {
  if (Array.isArray(value)) return value.length
  if (jsonType(value) === 'object') return Object.keys(value).length
  return 0
}

// One-line summary, e.g. "{ case, citizen, deep_chain, … +5 }" or "[50 items]"
export function summarize(value, maxKeys = 3) {
  const type = jsonType(value)
  if (type === 'array') {
    return value.length === 0 ? '[]' : `[${value.length} ${value.length === 1 ? 'item' : 'items'}]`
  }
  if (type === 'object') {
    const keys = Object.keys(value)
    if (keys.length === 0) return '{}'
    const shown = keys.slice(0, maxKeys).join(', ')
    const rest = keys.length - maxKeys
    return rest > 0 ? `{ ${shown}, … +${rest} }` : `{ ${shown} }`
  }
  return formatScalar(value)
}

export function formatScalar(value) {
  const type = jsonType(value)
  if (type === 'null') return 'null'
  // Quoted but not escaped, so inner quotes and backslashes stay readable
  if (type === 'string') return `"${value}"`
  return String(value)
}

// Tailwind/DaisyUI text classes per value type, so colours follow the theme
export const typeClass = {
  string: 'text-success',
  number: 'text-info',
  boolean: 'text-warning',
  null: 'text-base-content/50 italic'
}
