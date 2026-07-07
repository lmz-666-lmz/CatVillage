export type AudioRecordingSupport = {
  isSecureContext: boolean;
  hasMediaDevices: boolean;
  hasGetUserMedia: boolean;
  hasMediaRecorder: boolean;
  supportedMimeType: string;
  supportedMimeTypes: string[];
  canRecord: boolean;
  reason: 'ok' | 'insecure' | 'no-media-devices' | 'no-get-user-media' | 'no-media-recorder';
  message: string;
};

const AUDIO_MIME_TYPES = ['audio/webm', 'audio/mp4', 'audio/mpeg', 'audio/wav'];

export const detectAudioRecordingSupport = (): AudioRecordingSupport => {
  const mediaDevices = navigator.mediaDevices;
  const hasMediaRecorder = typeof window.MediaRecorder !== 'undefined';
  const supportedMimeTypes = hasMediaRecorder
    ? AUDIO_MIME_TYPES.filter((type) => {
        try {
          return window.MediaRecorder.isTypeSupported(type);
        } catch {
          return false;
        }
      })
    : [];

  const result: AudioRecordingSupport = {
    isSecureContext: window.isSecureContext,
    hasMediaDevices: !!mediaDevices,
    hasGetUserMedia: typeof mediaDevices?.getUserMedia === 'function',
    hasMediaRecorder,
    supportedMimeType: supportedMimeTypes[0] || '',
    supportedMimeTypes,
    canRecord: false,
    reason: 'ok',
    message: ''
  };

  if (!result.isSecureContext) {
    result.reason = 'insecure';
    result.message = '手机浏览器录音需要 HTTPS 安全访问，当前可先上传音频文件识别。';
  } else if (!result.hasMediaDevices) {
    result.reason = 'no-media-devices';
    result.message = '当前浏览器不支持直接录音，可上传音频文件识别。';
  } else if (!result.hasGetUserMedia) {
    result.reason = 'no-get-user-media';
    result.message = '当前浏览器不支持直接录音，可上传音频文件识别。';
  } else if (!result.hasMediaRecorder) {
    result.reason = 'no-media-recorder';
    result.message = '当前浏览器不支持直接录音，可上传音频文件识别。';
  } else {
    result.canRecord = true;
    result.message = result.supportedMimeType
      ? `当前浏览器支持录音，格式 ${result.supportedMimeType}。`
      : '当前浏览器支持录音。';
  }

  return result;
};
