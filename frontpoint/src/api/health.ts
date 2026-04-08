import request from '@/utils/request';

type BackendWeightRecord = {
  id: number;
  pet_id: string;
  weight: number;
  record_date: string;
};

type BackendWeightListResponse = {
  total: number;
  list: BackendWeightRecord[];
};

export type WeightRecord = {
  id: number;
  petId: string;
  weight: number;
  recordDate: string;
};

const toWeightRecord = (row: BackendWeightRecord): WeightRecord => ({
  id: row.id,
  petId: row.pet_id,
  weight: row.weight,
  recordDate: row.record_date
});

export function createWeightRecord(data: { petId: string; weight: number; recordDate?: string }) {
  return request<BackendWeightRecord>({
    url: '/health/weight',
    method: 'post',
    data: {
      pet_id: data.petId,
      weight: data.weight,
      record_date: data.recordDate
    }
  }).then((response) => ({
    ...response,
    data: toWeightRecord(response.data)
  }));
}

export function getWeightRecords(params: { petId: string; page?: number; pageSize?: number }) {
  const page = Math.max(1, params.page || 1);
  const pageSize = Math.max(1, params.pageSize || 20);
  return request<BackendWeightListResponse>({
    url: '/health/weight/list',
    method: 'get',
    params: {
      pet_id: params.petId,
      skip: (page - 1) * pageSize,
      limit: pageSize
    }
  }).then((response) => ({
    ...response,
    data: {
      total: response.data.total,
      list: response.data.list.map(toWeightRecord)
    }
  }));
}
