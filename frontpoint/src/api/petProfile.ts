import request from '@/utils/request';
import type {
  CreateCatProfileRequest,
  UpdateCatProfileRequest,
  CatProfileResponse,
  CatProfileListResponse
} from '@/types/cat';

type BackendCatProfile = {
  id: string;
  user_id: string;
  name: string;
  breed?: string | null;
  age?: number | null;
  gender?: number | null;
  weight?: number | null;
  avatar_url?: string | null;
  is_neutered?: boolean | null;
  medical_history?: string | null;
  vaccine_status?: string | null;
  created_at: string;
  updated_at: string;
};

type BackendCatProfileList = {
  total: number;
  list: BackendCatProfile[];
};

const toBackendPayload = (data: CreateCatProfileRequest | UpdateCatProfileRequest) => ({
  name: data.name,
  breed: data.breed,
  age: data.age,
  gender: data.gender,
  weight: data.weight,
  avatar_url: data.avatarUrl,
  is_neutered: data.isNeutered,
  medical_history: data.medicalHistory,
  vaccine_status: data.vaccineStatus
});

const toFrontendProfile = (data: BackendCatProfile): CatProfileResponse => ({
  id: data.id,
  userId: data.user_id,
  name: data.name,
  breed: data.breed ?? '',
  age: data.age ?? 0,
  gender: data.gender ?? 0,
  weight: data.weight ?? undefined,
  avatarUrl: data.avatar_url ?? undefined,
  isNeutered: data.is_neutered ?? false,
  medicalHistory: data.medical_history ?? undefined,
  vaccineStatus: data.vaccine_status ?? undefined,
  createdAt: data.created_at,
  updatedAt: data.updated_at
});

// 新增猫咪档案
export function createPetProfile(data: CreateCatProfileRequest) {
  return request<BackendCatProfile>({
    url: '/pet-profiles',
    method: 'post',
    data: toBackendPayload(data)
  }).then((response) => ({
    ...response,
    data: toFrontendProfile(response.data)
  }));
}

// 编辑猫咪档案
export function updatePetProfile(catId: string, data: UpdateCatProfileRequest) {
  return request<BackendCatProfile>({
    url: `/pet-profiles/${catId}`,
    method: 'put',
    data: toBackendPayload(data)
  }).then((response) => ({
    ...response,
    data: toFrontendProfile(response.data)
  }));
}

// 查询猫咪档案详情
export function getPetProfile(catId: string) {
  return request<BackendCatProfile>({
    url: `/pet-profiles/${catId}`,
    method: 'get'
  }).then((response) => ({
    ...response,
    data: toFrontendProfile(response.data)
  }));
}

// 删除猫咪档案
export function deletePetProfile(catId: string) {
  return request({
    url: `/pet-profiles/${catId}`,
    method: 'delete'
  });
}

// 查询用户猫咪列表
export function getAllPetProfiles() {
  return request<BackendCatProfileList>({
    url: '/pet-profiles/list',
    method: 'get'
  }).then((response) => ({
    ...response,
    data: {
      total: response.data.total,
      list: response.data.list.map(toFrontendProfile)
    } as CatProfileListResponse
  }));
}