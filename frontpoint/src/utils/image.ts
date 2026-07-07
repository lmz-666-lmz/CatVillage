const DEFAULT_AVATAR_SEED = 'catvillage-default';

const buildDefaultUserAvatar = (seed: string) => {
  const normalized = String(seed || DEFAULT_AVATAR_SEED).trim() || DEFAULT_AVATAR_SEED;
  let hash = 0;
  for (let index = 0; index < normalized.length; index += 1) {
    hash = (hash * 31 + normalized.charCodeAt(index)) % 360;
  }
  const hue = hash;
  const hue2 = (hash + 40) % 360;
  const initials = normalized
    .replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '')
    .slice(0, 2)
    .toUpperCase() || 'CV';

  // Soft gradient circle with cat paw accent
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="128" y2="128" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="hsl(${hue},70%,78%)"/>
      <stop offset="50%" stop-color="hsl(${hue2},65%,68%)"/>
      <stop offset="100%" stop-color="hsl(${(hue + 20) % 360},60%,58%)"/>
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="rgba(0,0,0,0.12)"/>
    </filter>
  </defs>
  <!-- Background circle -->
  <rect width="128" height="128" rx="64" fill="url(#bg)"/>
  <!-- Decorative circles -->
  <circle cx="100" cy="20" r="30" fill="rgba(255,255,255,0.12)"/>
  <circle cx="20" cy="108" r="24" fill="rgba(255,255,255,0.10)"/>
  <!-- Cat body silhouette -->
  <g filter="url(#shadow)" fill="rgba(255,255,255,0.85)">
    <!-- Cat head -->
    <circle cx="64" cy="52" r="20"/>
    <!-- Cat ears -->
    <polygon points="46,38 44,18 56,32"/>
    <polygon points="82,38 84,18 72,32"/>
    <!-- Cat body -->
    <ellipse cx="64" cy="82" rx="22" ry="18"/>
    <!-- Cat tail -->
    <path d="M86 80 Q100 70 98 58" stroke="rgba(255,255,255,0.7)" stroke-width="6" fill="none" stroke-linecap="round"/>
  </g>
  <!-- Cat face details -->
  <g fill="rgba(80,60,50,0.35)">
    <circle cx="56" cy="48" r="3"/>
    <circle cx="72" cy="48" r="3"/>
    <ellipse cx="64" cy="56" rx="3" ry="2"/>
  </g>
  <!-- Initials -->
  <text x="64" y="98" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-size="17" font-weight="700" fill="rgba(255,255,255,0.92)">${initials}</text>
</svg>`;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
};

export const getDefaultUserAvatar = (seed = DEFAULT_AVATAR_SEED) => {
  return buildDefaultUserAvatar(seed);
};

export const DEFAULT_CAT_AVATAR = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';
export const DEFAULT_SOCIAL_IMAGE = '';

const isDataOrBlobUrl = (value: string) => /^(data:|blob:)/i.test(value);
const isHttpUrl = (value: string) => /^https?:\/\//i.test(value);

export const getSafeImageUrl = (value?: string | null, fallback = DEFAULT_CAT_AVATAR) => {
  const url = String(value || '').trim();
  if (!url) {
    return fallback;
  }
  if (isDataOrBlobUrl(url) || isHttpUrl(url) || url.startsWith('/')) {
    return url;
  }
  return `/${url.replace(/^\/+/, '')}`;
};

export const getSafeAvatarUrl = (value?: string | null, seed?: string | null) =>
  getSafeImageUrl(value, getDefaultUserAvatar(seed || undefined));

const isGeneratedUserAvatar = (value: string) =>
  /api\.dicebear\.com\/7\.x\/adventurer-neutral\/svg/i.test(value);

export const getSafeCatAvatarUrl = (value?: string | null) => {
  const url = String(value || '').trim();
  if (!url || isGeneratedUserAvatar(url)) {
    return DEFAULT_CAT_AVATAR;
  }
  return getSafeImageUrl(url, DEFAULT_CAT_AVATAR);
};

export const getOptionalImageUrl = (value?: string | null) => {
  const url = String(value || '').trim();
  return url ? getSafeImageUrl(url, '') : '';
};

export const handleImageError = (event: Event, fallback = DEFAULT_CAT_AVATAR) => {
  const target = event.target as HTMLImageElement | null;
  if (!target || target.dataset.fallbackApplied === 'true') {
    return;
  }
  target.dataset.fallbackApplied = 'true';
  target.src = fallback;
};
