import { describe, it, expect } from 'vitest';
import { createPinia } from 'pinia';
import { mount } from '@vue/test-utils';
import router from '../router';
import App from '../App.vue';

describe('App', () => {
  it('mounts renders properly', async () => {
    router.push('/login');
    await router.isReady();

    const wrapper = mount(App, {
      global: {
        plugins: [createPinia(), router],
        stubs: {
          RouterLink: true,
          RouterView: true,
          'van-tabbar': true,
          'van-tabbar-item': true,
        },
      },
    });

    expect(wrapper.exists()).toBe(true);
  });
});
