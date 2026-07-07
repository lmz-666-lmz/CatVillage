import request from '@/utils/request';

export interface VisualRecognitionResult {
  facialExpression: { eyes: string; ears: string; mouth: string };
  bodyPosture: { posture: string; tail: string; relaxLevel: number };
  behaviorAnalysis: string;
  emotionScore: number;
  emotionLabel: string;
}

export interface AudioVisualFusionResult {
  primaryEmotion: { label: string; description: string; confidence: number };
  otherEmotions: Array<{ label: string; description: string; confidence: number; color: string }>;
  fusionSteps: Array<{ name: string; detail: string }>;
}

export function recognizeCatImage(file: Blob) {
  const data = new FormData();
  data.append('file', file);
  return request<VisualRecognitionResult>({
    url: '/vision/recognize',
    method: 'post',
    headers: { 'Content-Type': 'multipart/form-data' },
    data,
    timeout: 30000
  });
}

export function analyzeAudioVisualFusion(petId?: string) {
  return request<AudioVisualFusionResult>({
    url: '/vision/audio-visual-fusion',
    method: 'post',
    data: {
      pet_id: petId || undefined
    },
    timeout: 30000
  });
}
