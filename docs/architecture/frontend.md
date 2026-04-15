---
title: Frontend
sidebar_position: 3
description: Frontend web interface architecture and structure.
---

The frontend is a [Vue.js 3](https://vuejs.org) application styled with [Tailwind CSS](https://tailwindcss.com) and [DaisyUI](https://daisyui.com). It communicates with the backend REST API.

## Structure

```
frontend/src/
├── views/           # Page-level components (one per route)
├── components/      # Reusable UI components
├── services/        # API client (wraps fetch calls to the backend)
├── stores/          # Pinia state stores
├── router/          # Vue Router configuration
└── fontAwesome.js   # Icon library registration
```

## Conventions

- Components use the **Options API**, not the Composition API.
- Icons use `@fortawesome/vue-fontawesome`. New icons must be imported and added to `library.add()` in `fontAwesome.js`. Don't use `<i class="fa ...">` CSS icon tags.
- API calls go through the service layer in `frontend/src/services/automationserver.js`, not directly in components.

## Development

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies API requests to the backend. See `vite.config.js` for the proxy configuration.
