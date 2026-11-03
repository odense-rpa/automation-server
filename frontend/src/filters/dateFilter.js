// src/filters/dateFilter.js
export function formatDateTime(value) {
    if (!value) return '';
    const date = new Date(value);
    return date.toLocaleString();
}