export interface PaginatedResponse<T> {
  total: number;
  items: T[];
  page?: number;
  limit?: number;
}

export {};
