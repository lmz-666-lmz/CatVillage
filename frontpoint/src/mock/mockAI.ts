import type { 
  ChatWithAIRequest, 
  ChatWithAIResponse, 
  ChatHistoryResponse,
  ClearSessionResponse,
  EmergencyHelpResponse
} from '@/types/aiAssistant';

// 模拟AI对话历史
const mockChatHistory: ChatWithAIResponse[] = [
  {
    id: 'chat-1',
    sessionId: 'session-1',
    message: '如何判断我的猫咪是否快乐？',
    role: 'user',
    timestamp: new Date(Date.now() - 86400000).toISOString() // 1天前
  },
  {
    id: 'chat-2',
    sessionId: 'session-1',
    message: '猫咪快乐的表现包括：发出呼噜声、尾巴竖立、眼睛微闭放松、主动接近主人、食欲正常、玩耍积极等。如果您的猫咪有这些表现，说明它很健康快乐。',
    role: 'assistant',
    timestamp: new Date(Date.now() - 86300000).toISOString() // 紧接着的回答
  },
  {
    id: 'chat-3',
    sessionId: 'session-1',
    message: '我家奶茶最近不太爱吃饭怎么办？',
    role: 'user',
    timestamp: new Date(Date.now() - 43200000).toISOString() // 12小时前
  },
  {
    id: 'chat-4',
    sessionId: 'session-1',
    message: '猫咪不爱吃饭可能有几个原因：1.食物变质或不合口味；2.环境压力大；3.身体不适。建议您：1.更换新鲜食物；2.检查喂食环境是否安静；3.观察是否有其他异常症状。如果持续超过2天，建议就医。',
    role: 'assistant',
    timestamp: new Date(Date.now() - 43100000).toISOString() // 紧接着的回答
  },
  {
    id: 'chat-5',
    sessionId: 'session-2',
    message: '布丁总是半夜乱叫，有什么办法解决吗？',
    role: 'user',
    timestamp: new Date(Date.now() - 3600000).toISOString() // 1小时前
  },
  {
    id: 'chat-6',
    sessionId: 'session-2',
    message: '猫咪夜间叫唤常见原因：1.寻求注意；2.生理需求（饥饿、上厕所）；3.年龄相关的认知障碍。建议：1.白天增加活动量；2.睡前喂食；3.提供舒适的睡眠环境。不要在夜间回应叫唤，以免强化行为。',
    role: 'assistant',
    timestamp: new Date(Date.now() - 3500000).toISOString() // 紧接着的回答
  }
];

// 模拟会话数据
const mockSessions = [
  {
    id: 'session-1',
    userId: 'user-1',
    catId: 'cat-1',
    title: '关于猫咪快乐的咨询',
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: new Date(Date.now() - 3600000).toISOString()
  },
  {
    id: 'session-2',
    userId: 'user-1',
    catId: 'cat-2',
    title: '解决布丁夜间叫唤问题',
    createdAt: new Date(Date.now() - 7200000).toISOString(),
    updatedAt: new Date(Date.now() - 1800000).toISOString()
  }
];

// 模拟AI对话
export const mockChatWithAI = (data: ChatWithAIRequest): Promise<{ data: ChatWithAIResponse }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 根据用户问题生成模拟答案
      const answers: Record<string, string> = {
        '快乐': '猫咪快乐的表现包括：发出呼噜声、尾巴竖立、眼睛微闭放松、主动接近主人、食欲正常、玩耍积极等。',
        '吃饭': '猫咪不爱吃饭可能有几个原因：1.食物变质或不合口味；2.环境压力大；3.身体不适。建议您：1.更换新鲜食物；2.检查喂食环境是否安静；3.观察是否有其他异常症状。',
        '叫唤': '猫咪夜间叫唤常见原因：1.寻求注意；2.生理需求（饥饿、上厕所）；3.年龄相关的认知障碍。建议：1.白天增加活动量；2.睡前喂食；3.提供舒适的睡眠环境。',
        '疫苗': '猫咪常规疫苗包括：猫三联（预防猫瘟、猫鼻支、猫杯状病毒）、狂犬病疫苗。首次免疫通常在6-8周龄开始，之后每年加强一次。',
        '绝育': '猫咪绝育的最佳时间通常在6-8个月龄，此时猫咪身体发育较好，手术风险较低。绝育前需确保猫咪身体健康，已做完基础疫苗。'
      };

      // 尝试匹配问题关键词
      let answer = '感谢您的提问，我会尽力为您解答关于猫咪养护的问题。';
      for (const [keyword, response] of Object.entries(answers)) {
        if (data.message.includes(keyword)) {
          answer = response + ' 如果问题持续存在或加重，建议咨询专业兽医获得更详细的指导。';
          break;
        }
      }

      const newChat: ChatWithAIResponse = {
        id: `chat-${mockChatHistory.length + 1}`,
        sessionId: data.sessionId || `session-${Date.now()}`,
        message: answer,
        role: 'assistant',
        timestamp: new Date().toISOString()
      };

      mockChatHistory.push(newChat);

      resolve({ data: newChat });
    }, 1500); // 模拟AI思考时间
  });
};

// 获取对话历史
export const getMockChatHistory = (params: { sessionId?: string; catId?: string; page: number; pageSize: number }): Promise<{ data: ChatHistoryResponse }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filteredHistory = [...mockChatHistory];

      // 如果指定了sessionId，则过滤出该会话的历史
      if (params.sessionId) {
        filteredHistory = filteredHistory.filter(chat => chat.sessionId === params.sessionId);
      }

      // 分页处理
      const start = (params.page - 1) * params.pageSize;
      const end = start + params.pageSize;
      const paginatedList = filteredHistory.slice(start, end);

      resolve({ 
        data: { 
          list: paginatedList, 
          total: filteredHistory.length,
          page: params.page,
          pageSize: params.pageSize
        } 
      });
    }, 500);
  });
};

// 清空会话
export const mockClearSession = (sessionId: string): Promise<{ data: ClearSessionResponse }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const sessionExists = mockSessions.some(session => session.id === sessionId);
      if (sessionExists) {
        // 删除会话中的对话记录
        for (let i = mockChatHistory.length - 1; i >= 0; i--) {
          if (mockChatHistory[i]?.sessionId === sessionId) {
            mockChatHistory.splice(i, 1);
          }
        }
        
        resolve({ data: { success: true } });
      } else {
        reject(new Error('会话不存在'));
      }
    }, 300);
  });
};

// 模拟紧急求助
export const mockEmergencyHelp = (_warningId: string): Promise<{ data: EmergencyHelpResponse }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const response: EmergencyHelpResponse = {
        success: true,
        advice: '已连接到AI助理，正在为您提供专业的紧急建议',
        nextSteps: [
          '请保持冷静，观察猫咪的生命体征',
          '如果猫咪呼吸困难或失去意识，请立即联系最近的急诊兽医院',
          '准备好猫咪的医疗记录，以便兽医参考',
          '在前往医院的路上，保持猫咪温暖和安静',
          '联系24小时动物急诊热线：400-xxx-xxxx',
          '就近寻找动物医院：https://map.example.com/vets',
          '观看急救指导视频：https://video.example.com/cat-first-aid'
        ]
      };
      
      resolve({ data: response });
    }, 1000);
  });
};