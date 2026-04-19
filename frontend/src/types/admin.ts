export interface LoginCredentials {
  email: string;
  pid: string;
}

export interface LoginResponse {
  access_token: string;
}

export interface Account {
  id: number;
  email: string;
  pid: string;
  first_name: string;
  last_name: string;
  role: "admin" | "staff";
}

export interface CreateSenator {
  first_name: string;
  last_name: string;
  email: string;
  district_id: number;
  session_number: number;
}

export interface UpdateSenator {
  first_name?: string;
  last_name?: string;
  email?: string;
  district_id?: number;
  is_active?: boolean;
  session_number?: number;
}

export interface CreateNews {
  title: string;
  body: string;
  summary: string;
  image_url: string | null;
  is_published: boolean;
}

export interface AdminNews {
  id: number;
  title: string;
  summary: string;
  body: string;
  image_url: string | null;
  date_published: string;
  date_last_edited: string;
  admin?: Account | null;
  is_published: boolean;
}
export interface UpdateNews {
  title: string;
  body: string;
  summary: string;
  image_url: string | null;
  is_published: boolean;
}

export interface CreateLegislation {
  title: string;
  bill_number: string;
  session_number: number;
  sponsor_id: number | null;
  sponsor_name: string;
  summary: string;
  full_text: string;
  status: string;
  type: string;
  date_introduced: string;
}

export interface CreateLegislationAction {
  legislation_id: number;
  action_date: string;
  description: string;
  action_type: string;
}

export interface CreateCalendarEvent {
  title: string;
  description: string | null;
  start_datetime: string;
  end_datetime: string;
  location: string | null;
  event_type: string;
  is_published: boolean;
}

export interface CreateCarouselSlide {
  image_url: string;
  overlay_text: string;
  link_url: string;
  display_order: number;
  is_active: boolean;
}

export interface UpdateFinanceHearingConfig {
  is_active: boolean;
  season_start: string | null;
  season_end: string | null;
}

export interface CreateFinanceHearingDate {
  hearing_date: string;
  hearing_time: string;
  location: string | null;
  description: string | null;
}

export interface UpdateFinanceHearingDate {
  hearing_date: string;
  hearing_time: string;
  location: string | null;
  description: string | null;
  is_full: boolean;
}

export interface CreateCommittee {
  name: string;
  description: string;
  chair_senator_id: number | null;
  chair_name: string;
  chair_email: string;
  is_active: boolean;
}

export interface AssignCommitteeMember {
  senator_id: number;
  role: string;
}

export interface AdminStaff {
  id: number;
  first_name: string;
  last_name: string;
  title: string;
  email: string;
  photo_url: string | null;
  display_order: number;
  is_active: boolean;
}

export interface CreateStaff {
  first_name: string;
  last_name: string;
  title: string;
  email: string;
  display_order: number;
}

export interface UpdateStaff {
  first_name: string;
  last_name: string;
  title: string;
  email: string;
  photo_url: string | null;
  display_order: number;
  is_active: boolean;
}

export interface AdminDistrict {
  id: number;
  district_name: string;
  description: string | null;
}

export interface CreateDistrict {
  district_name: string;
  description: string | null;
}

export interface UpdateDistrict {
  district_name: string | null;
  description: string | null;
}

export interface DistrictMapping {
  id: number;
  district_id: number;
  mapping_value: string;
}

export interface CreateDistrictMapping {
  mapping_value: string;
}

export interface CreateBudgetData {
  fiscal_year: string;
  category: string;
  amount: number;
  description: string | null;
  parent_category_id: number | null;
  display_order: number;
}

export interface UpdateStaticPage {
  title: string;
  body: string;
}

export interface CreateAccount {
  email: string;
  pid: string;
  first_name: string;
  last_name: string;
  role: "admin" | "staff";
}

export interface CreateLeadership {
  senator_id: number | null;
  title: string;
  first_name: string;
  last_name: string;
  email: string;
  headshot_url?: string | null;
  is_active?: boolean;
  session_number: number;
}

export interface UpdateLeadership {
  senator_id?: number | null;
  title?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  headshot_url?: string | null;
  is_active?: boolean;
  session_number?: number;
}

export interface AdminLeadership {
  id: number;
  senator_id: number | null;
  title: string;
  first_name: string;
  last_name: string;
  email: string;
  photo_url: string | null;
  session_number: number;
  is_current: boolean;
}
