import { createRouter, createWebHistory } from "vue-router";
import UrlFormPage from "../pages/UrlFormPage.vue";

const routes = [
  {
    path: "/",
    name: "url-form",
    component: UrlFormPage,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
// noop commit marker
