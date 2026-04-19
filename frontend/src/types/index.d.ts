// Minimal project ambient types to satisfy imports during CI/build until full types are restored.
declare module "@/types" {
  export interface Senator {
    id: string;
    first_name?: string;
    last_name?: string;
    district?: string;
    committees?: Array<{ name: string; role?: string }>;
    email?: string;
    headshot_url?: string | null;
  }

  export type Legislation = any;
}

declare module "@/types/api" {
  export interface PaginatedResponse<T> {
    total: number;
    items: T[];
  }
}
