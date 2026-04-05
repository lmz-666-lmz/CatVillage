import type { CatProfileResponse, UpdateCatProfileRequest } from '@/types/cat';

// 模拟猫咪数据
export const mockCats: CatProfileResponse[] = [
  {
    id: 'cat-1',
    userId: 'user-1',
    name: '奶茶',
    breed: '英短',
    age: 24, // 月龄
    gender: 1, // 1为雌性，0为雄性
    avatarUrl: 'https://placekitten.com/200/200',
    weight: 4.2,
    isNeutered: true,
    medicalHistory: '无特殊病史',
    vaccineStatus: '已完成',
    createdAt: '2022-03-10',
    updatedAt: '2023-05-20'
  },
  {
    id: 'cat-2',
    userId: 'user-1',
    name: '布丁',
    breed: '美短',
    age: 12, // 月龄
    gender: 0,
    avatarUrl: 'https://placekitten.com/200/201',
    weight: 3.8,
    isNeutered: true,
    medicalHistory: '去年曾患感冒，现已康复',
    vaccineStatus: '已完成',
    createdAt: '2022-08-22',
    updatedAt: '2023-05-22'
  },
  {
    id: 'cat-3',
    userId: 'user-1',
    name: '橘子',
    breed: '橘猫',
    age: 36, // 月龄
    gender: 0,
    avatarUrl: 'https://placekitten.com/200/202',
    weight: 5.1,
    isNeutered: true,
    medicalHistory: '轻微肥胖',
    vaccineStatus: '进行中',
    createdAt: '2021-12-05',
    updatedAt: '2023-04-15'
  }
];

// 获取猫咪列表
export const getMockCatList = (): Promise<{ data: { list: CatProfileResponse[]; total: number } }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ 
        data: { 
          list: mockCats, 
          total: mockCats.length 
        } 
      });
    }, 500);
  });
};

// 获取猫咪详情
export const getMockCatDetail = (id: string): Promise<{ data: CatProfileResponse }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const cat = mockCats.find(c => c.id === id);
      if (cat) {
        resolve({ data: cat });
      } else {
        reject(new Error('猫咪不存在'));
      }
    }, 300);
  });
};

// 更新猫咪资料
export const mockUpdateCatProfile = (id: string, data: UpdateCatProfileRequest): Promise<{ data: CatProfileResponse }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockCats.findIndex(c => c.id === id);
      if (index === -1) {
        reject(new Error('猫咪不存在'));
        return;
      }

      const existingCat = mockCats[index]!;

      const updatedCat: CatProfileResponse = {
        ...existingCat,
        ...data,
        id: existingCat.id, // 保持原ID不变
        userId: existingCat.userId, // 保持原用户ID不变
        createdAt: existingCat.createdAt, // 保持原创建时间
        updatedAt: new Date().toISOString()
      };

      mockCats[index] = updatedCat;

      resolve({ data: updatedCat });
    }, 500);
  });
};

// 添加猫咪
export const mockAddCat = (data: Omit<CatProfileResponse, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<{ data: CatProfileResponse }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newCat: CatProfileResponse = {
        id: `cat-${mockCats.length + 1}`,
        userId: 'user-1', // 默认用户ID
        ...data,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      mockCats.push(newCat);

      resolve({ data: newCat });
    }, 500);
  });
};