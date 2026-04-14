export interface Account {
  id: number;
  email: string;
  pid: string;
  first_name: string;
  last_name: string;
  role: "admin" | "staff";
}

export interface CommitteeAssignment {
  committee_id: number;
  committee_name: string;
  role: string;
}

export interface Senator {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  headshot_url: string | null;
  district_id: number;
  is_active: boolean;
  session_number: number;
  committees: CommitteeAssignment[];
}

export interface Committee {
  id: number;
  name: string;
  description: string;
  chair_name: string;
  chair_email: string;
  members: Senator[];
  is_active: boolean;
}

export interface Leadership {
  id: number;
  title: string;
  first_name: string;
  last_name: string;
  email: string;
  photo_url: string | null;
  session_number: number;
  is_current: boolean;
}

export interface News {
  id: number;
  title: string;
  summary: string;
  body: string;
  image_url: string | null;
  date_published: string;
  date_last_edited: string;
  admin?: Account | null;
  author_name: string;
}

export interface LegislationAction {
  id: number;
  action_date: string;
  description: string;
  action_type: string;
}

export interface Legislation {
  id: number;
  title: string;
  bill_number: string;
  session_number: number;
  sponsor_name: string;
  summary: string;
  full_text: string;
  status: string;
  type: string;
  date_introduced: string;
  date_last_action: string;
  actions?: LegislationAction[];
}

export interface CalendarEvent {
  id: number;
  title: string;
  description: string | null;
  start_datetime: string;
  end_datetime: string;
  location: string | null;
  event_type: string;
  is_published: boolean;
}

export interface CarouselSlide {
  id: number;
  image_url: string;
  overlay_text: string | null;
  link_url: string | null;
  display_order: number;
  is_active: boolean;
}

export interface FinanceHearingDate {
  id: number;
  hearing_date: string;
  hearing_time: string;
  location: string | null;
  description: string | null;
  is_full: boolean;
}

export interface FinanceHearingConfig {
  is_active: boolean;
  season_start: string | null;
  season_end: string | null;
  dates: FinanceHearingDate[];
}

export interface Staff {
  id: number;
  first_name: string;
  last_name: string;
  title: string;
  email: string;
  photo_url: string | null;
}

export interface District {
  id: number;
  district_name: string;
  description: string | null;
  senator: Senator[] | null;
}

export interface BudgetData {
  id: number;
  fiscal_year: string;
  category: string;
  amount: number;
  description: string | null;
  children: BudgetData[];
}

export interface StaticPage {
  id: number;
  page_slug: string;
  title: string;
  body: string;
  updated_at: string;
}
