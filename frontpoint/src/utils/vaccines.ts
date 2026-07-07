export const PRESET_VACCINES = ['三联疫苗', '狂犬疫苗', '体内驱虫', '体外驱虫'] as const;

export type PresetVaccine = (typeof PRESET_VACCINES)[number];

const SPLIT_RE = /[、,，;；\n\r]+/;

export const normalizeVaccineList = (value: unknown): string[] => {
  const source = Array.isArray(value) ? value.join('、') : String(value || '');
  const seen = new Set<string>();
  return source
    .split(SPLIT_RE)
    .map((item) => item.trim())
    .filter((item) => {
      if (!item || seen.has(item)) {
        return false;
      }
      seen.add(item);
      return true;
    });
};

export const buildVaccineStatus = (items: string[]): string | undefined => {
  const normalized = normalizeVaccineList(items);
  return normalized.length ? normalized.join('、') : undefined;
};

export const isPresetVaccine = (value: string): value is PresetVaccine =>
  PRESET_VACCINES.includes(value as PresetVaccine);
