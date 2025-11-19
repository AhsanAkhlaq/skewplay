import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import './style.css';
import router from './router';
import { useAuthStore } from './stores/auth';
import vuetify from './plugins/vuetify';
import '@mdi/font/css/materialdesignicons.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(vuetify);

const authStore = useAuthStore();
authStore.init();

app.use(router);
app.mount('#app');
