//import './assets/main.css'
//import 'bootstrap/dist/css/bootstrap.min.css'
//import 'bootstrap-icons/font/bootstrap-icons.min.css'
import './assets/base.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

import App from './App.vue'
import router from './router'
import { formatDate, formatDateTime } from './filters/dateFilter';
import { capitalizeFirstLetter } from './filters/stringFilter';

import { FontAwesomeIcon } from './fontAwesome';

const app = createApp(App)

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);
app.use(pinia);

app.component('font-awesome-icon', FontAwesomeIcon);

app.config.globalProperties.$formatDate = formatDate;
app.config.globalProperties.$formatDateTime = formatDateTime;
app.config.globalProperties.$capitalizeFirstLetter = capitalizeFirstLetter;


app.use(router)

app.mount('#app')

