export type AudioValidationResult = {
  ok: boolean;
  message?: string;
  warning?: string;
};

const AUDIO_MAX_BYTES = 10 * 1024 * 1024;
const AUDIO_MIN_SECONDS = 3;
const AUDIO_MAX_SECONDS = 20;

export const isSupportedAudioFile = (file: File) => {
  return file.type.startsWith('audio/') || /\.(mp3|wav|m4a|aac|ogg|oga|webm|flac|amr)$/i.test(file.name);
};

export const getAudioDuration = (file: File): Promise<number> => {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const audio = new Audio();
    const cleanup = () => {
      audio.removeAttribute('src');
      URL.revokeObjectURL(url);
    };
    audio.preload = 'metadata';
    audio.onloadedmetadata = () => {
      const duration = audio.duration;
      cleanup();
      Number.isFinite(duration) ? resolve(duration) : reject(new Error('duration unavailable'));
    };
    audio.onerror = () => {
      cleanup();
      reject(new Error('duration unavailable'));
    };
    audio.src = url;
  });
};

export const validateAudioFile = async (file: File): Promise<AudioValidationResult> => {
  if (file.size > AUDIO_MAX_BYTES) {
    return { ok: false, message: '音频文件过大' };
  }
  if (!isSupportedAudioFile(file)) {
    return { ok: false, message: '格式不支持，请上传常见音频格式' };
  }
  try {
    const duration = await getAudioDuration(file);
    if (duration < AUDIO_MIN_SECONDS) {
      return { ok: false, message: '音频太短，请上传 5-20 秒清晰猫叫' };
    }
    if (duration > AUDIO_MAX_SECONDS) {
      return { ok: false, message: '音频过长，请截取 5-20 秒猫叫片段后再上传' };
    }
    return { ok: true };
  } catch {
    return { ok: true, warning: '无法读取音频时长，建议上传 5-20 秒猫叫' };
  }
};
