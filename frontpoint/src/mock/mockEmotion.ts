import type { EmotionRecordResponse, EmotionStatisticsResponse, WarningResponse, EmotionRecordsListResponse, MoodTrendData, EmotionDistributionData, WeeklyReportResponse, Recommendation } from '@/types/emotion';

// 模拟情绪记录数据
export const mockEmotionRecords: EmotionRecordResponse[] = [
  {
    id: 'emotion-1',
    catId: 'cat-1',
    userId: 'user-1',
    audioUrl: 'https://example.com/audio1.mp3',
    emotionTag: '开心',
    confidence: 0.92,
    emotionDescription: '系统检测到猫咪处于开心状态',
    createdAt: new Date(Date.now() - 86400000).toISOString() // 1天前
  },
  {
    id: 'emotion-2',
    catId: 'cat-1',
    userId: 'user-1',
    audioUrl: 'https://example.com/audio2.mp3',
    emotionTag: '舒适',
    confidence: 0.87,
    emotionDescription: '猫咪在休息时发出的满足呼噜声',
    createdAt: new Date(Date.now() - 43200000).toISOString() // 12小时前
  },
  {
    id: 'emotion-3',
    catId: 'cat-1',
    userId: 'user-1',
    audioUrl: 'https://example.com/audio3.mp3',
    emotionTag: '焦虑',
    confidence: 0.78,
    emotionDescription: '系统检测到猫咪处于焦虑状态，请关注',
    createdAt: new Date(Date.now() - 3600000).toISOString() // 1小时前
  },
  {
    id: 'emotion-4',
    catId: 'cat-2',
    userId: 'user-1',
    audioUrl: 'https://example.com/audio4.mp3',
    emotionTag: '疼痛警告',
    confidence: 0.95,
    emotionDescription: '系统检测到猫咪可能有疼痛表现，请及时就医',
    createdAt: new Date(Date.now() - 7200000).toISOString() // 2小时前
  }
];

// 模拟情绪统计数据
export const mockEmotionStatistics: EmotionStatisticsResponse = {
  moodTrend: [
    { date: new Date(Date.now() - 6 * 86400000).toISOString().split('T')[0]!, emotionTag: '开心', confidence: 0.85 },
    { date: new Date(Date.now() - 5 * 86400000).toISOString().split('T')[0]!, emotionTag: '舒适', confidence: 0.78 },
    { date: new Date(Date.now() - 4 * 86400000).toISOString().split('T')[0]!, emotionTag: '焦虑', confidence: 0.65 },
    { date: new Date(Date.now() - 3 * 86400000).toISOString().split('T')[0]!, emotionTag: '舒适', confidence: 0.82 },
    { date: new Date(Date.now() - 2 * 86400000).toISOString().split('T')[0]!, emotionTag: '开心', confidence: 0.91 },
    { date: new Date(Date.now() - 1 * 86400000).toISOString().split('T')[0]!, emotionTag: '舒适', confidence: 0.88 },
    { date: new Date().toISOString().split('T')[0]!, emotionTag: '开心', confidence: 0.93 }
  ] as MoodTrendData[],
  emotionDistribution: [
    { emotionTag: '开心', count: 42, percentage: 42 },
    { emotionTag: '舒适', count: 28, percentage: 28 },
    { emotionTag: '焦虑', count: 12, percentage: 12 },
    { emotionTag: '疼痛警告', count: 8, percentage: 8 },
    { emotionTag: '应激', count: 6, percentage: 6 },
    { emotionTag: '饥饿', count: 4, percentage: 4 }
  ] as EmotionDistributionData[],
  avgConfidence: 0.82,
  warningCount: 2
};

// 模拟健康预警数据
export const mockWarnings: WarningResponse[] = [
  {
    id: 'warning-1',
    catId: 'cat-1',
    userId: 'user-1',
    title: '奶茶近期焦虑指数偏高',
    description: '连续3天检测到焦虑情绪，可能与环境变化有关',
    level: 'medium', // 中等
    status: 'pending',
    createdAt: new Date(Date.now() - 86400000).toISOString(), // 1天前
    updatedAt: new Date(Date.now() - 86400000).toISOString(), // 1天前
    relatedRecordId: 'emotion-3'
  },
  {
    id: 'warning-2',
    catId: 'cat-2',
    userId: 'user-1',
    title: '布丁疑似身体不适',
    description: '检测到异常声音模式，建议尽快就医',
    level: 'high', // 严重
    status: 'pending',
    createdAt: new Date(Date.now() - 7200000).toISOString(), // 2小时前
    updatedAt: new Date(Date.now() - 7200000).toISOString(), // 2小时前
    relatedRecordId: 'emotion-4'
  }
];

// 模拟情绪识别
export const mockRecognizeEmotion = (audioFile: File): Promise<{ data: EmotionRecordResponse }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const randomIndex = Math.floor(Math.random() * 6);
      const emotions = ['开心', '舒适', '焦虑', '疼痛警告', '应激', '饥饿'];
      const emotionTag = emotions[randomIndex]!;
      const newRecord: EmotionRecordResponse = {
        id: `emotion-${mockEmotionRecords.length + 1}`,
        catId: 'cat-1', // 假设当前选择的猫咪
        userId: 'user-1',
        audioUrl: URL.createObjectURL(audioFile),
        emotionTag: emotionTag,
        confidence: parseFloat((Math.random() * 0.3 + 0.7).toFixed(2)),
        emotionDescription: `系统检测到猫咪处于${emotionTag}状态`,
        createdAt: new Date().toISOString()
      };
      
      resolve({ data: newRecord });
    }, 2000); // 模拟识别过程耗时
  });
};

// 获取情绪记录列表
export const getMockEmotionRecords = (params: { page: number; pageSize: number; catId?: string }): Promise<{ data: EmotionRecordsListResponse }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filteredRecords = [...mockEmotionRecords];
      
      // 如果指定了catId，则过滤出该猫咪的记录
      if (params.catId) {
        filteredRecords = filteredRecords.filter(r => r.catId === params.catId);
      }
      
      const start = (params.page - 1) * params.pageSize;
      const end = start + params.pageSize;
      const paginatedList = filteredRecords.slice(start, end);
      
      resolve({ 
        data: { 
          list: paginatedList, 
          total: filteredRecords.length,
          page: params.page,
          pageSize: params.pageSize
        } 
      });
    }, 500);
  });
};

// 获取情绪记录详情
export const getMockEmotionRecordDetail = (recordId: string): Promise<{ data: EmotionRecordResponse }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const record = mockEmotionRecords.find(r => r.id === recordId);
      if (record) {
        resolve({ data: record });
      } else {
        reject(new Error('情绪记录不存在'));
      }
    }, 300);
  });
};

// 获取情绪统计数据
export const getMockEmotionStatistics = (_params: { catId?: string; startDate?: string; endDate?: string }): Promise<{ data: EmotionStatisticsResponse }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockEmotionStatistics });
    }, 500);
  });
};

// 获取健康预警列表
export const getMockWarningList = (params: { page: number; pageSize: number; catId?: string; status?: string }): Promise<{ data: { list: WarningResponse[], total: number } }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filteredWarnings = [...mockWarnings];
      
      // 如果指定了catId，则过滤出该猫咪的预警
      if (params.catId) {
        filteredWarnings = filteredWarnings.filter(w => w.catId === params.catId);
      }
      
      // 如果指定了status，则过滤出相应状态的预警
      if (params.status) {
        filteredWarnings = filteredWarnings.filter(w => w.status === params.status);
      }
      
      const start = (params.page - 1) * params.pageSize;
      const end = start + params.pageSize;
      const paginatedList = filteredWarnings.slice(start, end);
      
      resolve({ 
        data: { 
          list: paginatedList, 
          total: filteredWarnings.length 
        } 
      });
    }, 500);
  });
};

// 标记预警状态
export const mockMarkWarningStatus = (warningId: string, status: string): Promise<{ data: { success: boolean } }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const warning = mockWarnings.find(w => w.id === warningId);
      if (warning) {
        warning.status = status as 'pending' | 'processing' | 'resolved';
        warning.updatedAt = new Date().toISOString(); 
        resolve({ data: { success: true } });
      } else {
        reject(new Error('预警不存在'));
      }
    }, 300);
  });
};

// 生成情绪周报
export const getMockWeeklyReport = (params: { catId?: string; week?: string }): Promise<{ data: WeeklyReportResponse }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const weekStart = params.week || new Date().toISOString().split('T')[0]!;
      const weekEnd = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]!;
      const reportData: WeeklyReportResponse = {
        weekStartDate: weekStart,
        weekEndDate: weekEnd,
        summary: '本周猫咪情绪总体稳定，开心和舒适状态占主导',
        moodTrends: mockEmotionStatistics.moodTrend,
        avgEmotion: '舒适',
        avgConfidence: 0.82,
        warningCount: 2,
        highlightMoments: [
          {
            date: new Date().toISOString().split('T')[0]!,
            emotionTag: '开心',
            description: '今天特别活跃，玩玩具很开心'
          }
        ],
        recommendations: [
          {
            title: '日常护理建议',
            description: '继续保持良好的日常护理习惯',
            priority: 'medium'
          },
          {
            title: '互动时间',
            description: '增加与猫咪的互动时间',
            priority: 'high'
          },
          {
            title: '观察提醒',
            description: '注意观察异常情绪变化',
            priority: 'low'
          }
        ] as Recommendation[]
      };
      
      resolve({ data: reportData });
    }, 1000);
  });
};