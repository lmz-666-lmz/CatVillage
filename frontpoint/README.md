# my-cat-app

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Recommended Browser Setup

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [Turn on Custom Object Formatter in Chrome DevTools](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [Turn on Custom Object Formatter in Firefox DevTools](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Run End-to-End Tests with [Playwright](https://playwright.dev)

```sh
# Install browsers for the first run
npx playwright install

# When testing on CI, must build the project first
npm run build

# Runs the end-to-end tests
npm run test:e2e
# Runs the tests only on Chromium
npm run test:e2e -- --project=chromium
# Runs the tests of a specific file
npm run test:e2e -- tests/example.spec.ts
# Runs the tests in debug mode
npm run test:e2e -- --debug
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

## Cat Village Incremental Notes (Added Only)

This section is appended for project-specific updates and does not replace the original Vite template content above.

### 2026-04-08 Updates

- Fixed router crash caused by missing named exports in [src/api/social.ts](src/api/social.ts):
  - Added `getFollowingDynamicsList`
  - Added `toggleFavoriteDynamic`
  - Added `toggleFollowUser`
  - Added `toggleCommentLike`
  - Added `getHotTopics`
- Kept [src/composables/useSocialFeatures.ts](src/composables/useSocialFeatures.ts) aligned with social API exports to avoid runtime `does not provide an export named ...` errors.
- Updated profile navigation behavior in [src/views/UserProfileView.vue](src/views/UserProfileView.vue):
  - `我的萌宠` now opens the cat archive page (`CatArchive`) instead of `喵喵台` (`Cats`).

### Local Run Checklist

When running locally with Vite HMR:

1. Start backend service in `backend`.
2. Start frontend with `npm run dev` in `frontpoint`.
3. If route/module errors persist after hot reload, do a hard refresh once to clear stale module cache.

### Functional Verification Checklist

- Open `广场` tab: page should render without module import errors.
- Open `消息` tab: page should render without router navigation errors.
- Open `我的` -> click `我的萌宠`: should jump to `猫咪档案` page.

