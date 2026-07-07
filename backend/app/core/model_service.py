import os
import warnings
from pathlib import Path

import joblib
import librosa
import numpy as np

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = os.getenv('CAT_MODEL_PATH', str(BASE_DIR / 'cat_emotion_model.pkl'))
TOP_K = 3

_TRANSLATION_DICT = {
    '开心/兴奋': {
        'human': '铲屎官，本喵现在心情很好，想互动和玩耍。',
        'science': '声纹偏高频且较平稳，通常对应积极唤叫。',
        'risk': 'low'
    },
    '疼痛警告': {
        'human': '我现在不舒服，可能需要立刻关注。',
        'science': '出现尖锐高频和强烈波动，疑似疼痛相关发声。',
        'risk': 'high'
    },
    '生气/暴躁': {
        'human': '请先保持距离，我正在警戒。',
        'science': '低频成分增强，能量集中，常见于防御或驱赶。',
        'risk': 'medium'
    },
    '求偶发情': {
        'human': '我在寻找同伴，叫声会更持续。',
        'science': '持续型长音较多，符合发情期特征。',
        'risk': 'low'
    },
    '母猫呼唤': {
        'human': '宝宝们快靠近我。',
        'science': '短促节律性叫声，常用于亲子定位。',
        'risk': 'low'
    },
    '放松休息': {
        'human': '我很放松，状态稳定。',
        'science': '整体能量平稳，情绪唤醒程度较低。',
        'risk': 'low'
    },
    '打斗/攻击': {
        'human': '我处在冲突状态，建议立即干预。',
        'science': '爆发性强能量噪声明显，冲突概率高。',
        'risk': 'high'
    },
    '警告/威胁': {
        'human': '这里是我的边界，请后退。',
        'science': '中低频威吓成分明显，属于防御阶段。',
        'risk': 'medium'
    }
}

_MODEL = None


def load_model():
    global _MODEL
    if _MODEL is None:
        model_path = Path(MODEL_PATH)
        if not model_path.is_absolute():
            model_path = BASE_DIR / model_path
        _MODEL = joblib.load(model_path)
    return _MODEL


def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    return np.mean(mfcc.T, axis=0), y, sr


def _validate_audio_signal(y, sr):
    duration = float(librosa.get_duration(y=y, sr=sr))
    if duration < 0.35:
        raise ValueError('Audio too short')

    if float(np.mean(np.abs(y))) < 0.002 or float(np.max(np.abs(y))) < 0.01:
        raise ValueError('Audio quality too low or no cat sound detected.')


def _build_top_predictions(model, features_2d):
    if not hasattr(model, 'predict_proba'):
        return [], None

    probabilities = model.predict_proba(features_2d)[0]
    labels = model.classes_
    paired = [
        {'label': label, 'probability': float(prob)}
        for label, prob in zip(labels, probabilities)
    ]
    paired.sort(key=lambda item: item['probability'], reverse=True)

    top_predictions = paired[:TOP_K]
    confidence = top_predictions[0]['probability'] if top_predictions else None
    return top_predictions, confidence


def _build_audio_profile(y, sr):
    duration = float(librosa.get_duration(y=y, sr=sr))
    rms = float(np.mean(librosa.feature.rms(y=y)))
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    return {
        'duration_seconds': round(duration, 3),
        'rms_energy': round(rms, 6),
        'zero_crossing_rate': round(zcr, 6),
        'spectral_centroid': round(centroid, 3)
    }


def analyze_audio(file_path):
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError('audio file does not exist')

    features, y, sr = extract_features(file_path)
    _validate_audio_signal(y, sr)
    model = load_model()
    features_2d = features.reshape(1, -1)

    label = model.predict(features_2d)[0]
    top_predictions, confidence = _build_top_predictions(model, features_2d)

    translated = _TRANSLATION_DICT.get(label, {
        'human': str(label),
        'science': '暂无该标签的解释。',
        'risk': 'unknown'
    })

    return {
        'label': str(label),
        'confidence': confidence,
        'top_predictions': top_predictions,
        'translation': {
            'human': translated['human'],
            'science': translated['science']
        },
        'risk_level': translated['risk'],
        'audio_profile': _build_audio_profile(y, sr),
        'model_info': {
            'name': 'cat-emotion-random-forest',
            'feature': 'mfcc-40'
        }
    }
