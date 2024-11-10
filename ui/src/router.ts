import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { usePageStore } from './core/page-store';

export const Route = {
  MAIN: 'MAIN',
};

const makeRoute = (
  name: string,
  path: string,
  component: () => Promise<unknown>,
): RouteRecordRaw => {
  return { path, name, component };
};

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/BlankLayout.vue'),
      children: [
        { path: '', redirect: { name: Route.MAIN } },
        makeRoute(Route.MAIN, 'classifier', () => import('@/classifier/views/MainPage.vue')),
      ],
    },
  ],
});

router.beforeEach(() => {
  const store = usePageStore();
  store.isLoading = true;
});

router.afterEach(() => {
  const store = usePageStore();
  store.isLoading = false;
});

export const linkFactory = {};

export default router;
