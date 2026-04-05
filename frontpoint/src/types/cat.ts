// 猫咪档案相关类型定义

// 猫咪档案创建请求
export interface CreateCatProfileRequest {
  name: string;
  breed: string;
  age: number; // 月龄
  gender: number; // 0-母，1-公
  weight?: number;
  isNeutered?: boolean;
  medicalHistory?: string;
  vaccineStatus?: string;
  avatarUrl?: string;
}

// 猫咪档案更新请求
export interface UpdateCatProfileRequest {
  name?: string;
  breed?: string;
  age?: number; // 月龄
  gender?: number; // 0-母，1-公
  weight?: number;
  isNeutered?: boolean;
  medicalHistory?: string;
  vaccineStatus?: string;
  avatarUrl?: string;
}

// 猫咪档案响应
export interface CatProfileResponse {
  id: string;
  userId: string;
  name: string;
  breed: string;
  age: number; // 月龄
  gender: number; // 0-母，1-公
  weight?: number;
  isNeutered?: boolean;
  medicalHistory?: string;
  vaccineStatus?: string;
  avatarUrl?: string;
  createdAt: string;
  updatedAt: string;
}

// 猫咪档案列表响应
export interface CatProfileListResponse {
  total: number;
  list: CatProfileResponse[];
}

// 猫咪品种枚举
export enum CatBreed {
  BritishShorthair = '英国短毛猫',
  AmericanShorthair = '美国短毛猫',
  Persian = '波斯猫',
  Siamese = '暹罗猫',
  MaineCoon = '缅因猫',
  RussianBlue = '俄罗斯蓝猫',
  ScottishFold = '苏格兰折耳猫',
  Other = '其他'
}

// 猫咪性别枚举
export enum CatGender {
  Female = 0,
  Male = 1
}