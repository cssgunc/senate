// Minimal TypeScript type exports used across the frontend during CI/build.
export type BudgetData = any;
export type CalendarEvent = any;
export type CarouselSlide = any;
export type Committee = any;
export type FinanceHearingConfig = any;
export type FinanceHearingDate = any;
export type Legislation = any;
export type LegislationAction = any;
export type News = any;
export type Senator = {
  id: number | string;
  first_name?: string;
  last_name?: string;
  district?: string;
  committees?: Array<{ name: string; role?: string }>;
  email?: string;
  headshot_url?: string | null;
};
export type Staff = any;
export type StaticPage = any;

// Admin-specific types
export type Account = any;
export type AdminNews = any;
export type AssignCommitteeMember = any;
export type CreateAccount = any;
export type CreateBudgetData = any;
export type CreateCalendarEvent = any;
export type CreateCarouselSlide = any;
export type CreateCommittee = any;
export type CreateFinanceHearingDate = any;
export type CreateLegislation = any;
export type CreateLegislationAction = any;
export type CreateNews = any;
export type CreateSenator = any;
export type CreateStaff = any;
export type LoginCredentials = { email: string; pid: string };
export type LoginResponse = { access_token: string };
export type UpdateFinanceHearingConfig = any;
export type UpdateNews = any;
export type UpdateSenator = any;
export type UpdateStaticPage = any;
