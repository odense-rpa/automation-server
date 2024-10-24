// src/filters/dateFilter.js
export function formatDate(value) {
    if (!value) return '';
    const date = new Date(value);
    return date.toLocaleDateString();
}

export function formatDateTime(value) {
    if (!value) return '';
    const date = new Date(value);
    return date.toLocaleString();
}