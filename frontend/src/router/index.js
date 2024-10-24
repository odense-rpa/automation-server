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
        path: ':id/edit',
        name: 'workqueue.edit',
        component: () => import('../views/EditWorkqueueView.vue')
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
    name: 'Credentials',
    component: () => import('../views/CredentialsView.vue')
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
        path: ':id',
        name: 'session.edit',
        component: () => import('../views/EditSessionView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes
})

export default router
