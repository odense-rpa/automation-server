import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  {
    path: '/process',
    name: 'process.container',
    children: [
      {
        path: '',
        name: 'process',
        component: () => import('../views/ProcessesView.vue')
      },
      {
        path: ':id/edit',
        name: 'process.edit',
        component: () => import('../views/EditProcessView.vue')
      },
      {
        path: 'create',
        name: 'process.create',
        component: () => import('../views/CreateProcessView.vue')
      }
    ]
  },
  {
    path: '/workqueues',
    name: 'workqueues.container',
    children: [
      {
        path: '',
        name: 'workqueues',
        component: () => import('../views/WorkqueuesView.vue')
      },
      {
        path: ':id',
        name: 'workqueue.detail',
        component: () => import('../views/WorkqueueView.vue')
      },
      {
        path: ':id/edit',
        name: 'workqueue.edit',
        component: () => import('../views/EditWorkqueueView.vue')
      },
      {
        path: ':id/item/:itemId',
        name: 'workqueue.item',
        component: () => import('../views/WorkItemView.vue')
      },
      {
        path: 'create',
        name: 'workqueue.create',
        component: () => import('../views/CreateWorkqueueView.vue')
      }
    ]
  },
  {
    path: '/credentials',
    name: 'credentials.container',
    children: [
      {
        path: '',
        name: 'credentials',
        component: () => import('../views/CredentialsView.vue')
      },
      {
        path: ':id/edit',
        name: 'credential.edit',
        component: () => import('../views/EditCredentialView.vue')
      },
      {
        path: 'create',
        name: 'credential.create',
        component: () => import('../views/CreateCredentialView.vue')
      }
    ]
  },
  {
    path: '/administration',
    name: 'Administration.container',
    children: [
      {
        path: '',
        name: 'administration',
        component: () => import('../views/AdministrationView.vue')
      },
      {
        path: 'tokens/create',
        name: 'token.create',
        component: () => import('../views/CreateTokenView.vue')
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('../views/SettingsView.vue')
      },
    ]
  },
  {
    path: '/sessions',
    name: 'sessions.container',
    children: [
      {
        path: '',
        name: 'sessions',
        component: () => import('../views/SessionsView.vue')
      },
      {
        path: ':id',
        name: 'session.edit',
        component: () => import('../views/EditSessionView.vue')
      }
    ]
  },
  // Must stay last: anything no other route matched
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes
})

export default router
