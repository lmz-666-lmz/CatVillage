import request from '@/utils/request';

export interface Doctor {
  id: string;
  name: string;
  title: string;
  tags: string[];
  price: number;
  rating: string;
  online: boolean;
  avatar: string;
  is_mock: boolean;
}

export interface DoctorListResponse {
  list: Doctor[];
  total: number;
  is_mock: boolean;
  mock_notice: string;
}

export interface ConsultTip {
  title: string;
  content: string;
}

export interface ConsultTipsResponse {
  tips: ConsultTip[];
  is_mock: boolean;
  mock_notice: string;
}

export function listDoctors(params?: { keyword?: string }) {
  return request<DoctorListResponse>({
    url: '/doctors/list',
    method: 'get',
    params,
  });
}

export function getConsultTips() {
  return request<ConsultTipsResponse>({
    url: '/doctors/tips',
    method: 'get',
  });
}
