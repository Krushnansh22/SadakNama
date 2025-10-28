// Enums
export enum ProjectStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  MAINTENANCE = 'maintenance',
  DELAYED = 'delayed',
  CANCELLED = 'cancelled',
}

export enum RoadType {
  NATIONAL_HIGHWAY = 'national_highway',
  STATE_HIGHWAY = 'state_highway',
  DISTRICT_ROAD = 'district_road',
  RURAL_ROAD = 'rural_road',
  CITY_ROAD = 'city_road',
  EXPRESSWAY = 'expressway',
}

export enum IssueType {
  POTHOLE = 'pothole',
  POOR_QUALITY = 'poor_quality',
  WATERLOGGING = 'waterlogging',
  CRACKS = 'cracks',
  DEBRIS = 'debris',
  SIGNAGE_ISSUE = 'signage_issue',
  DRAINAGE_PROBLEM = 'drainage_problem',
  SAFETY_HAZARD = 'safety_hazard',
  OTHER = 'other',
}

export enum ReportStatus {
  SUBMITTED = 'submitted',
  UNDER_REVIEW = 'under_review',
  ACKNOWLEDGED = 'acknowledged',
  IN_PROGRESS = 'in_progress',
  RESOLVED = 'resolved',
  REJECTED = 'rejected',
}

// Interfaces
export interface Minister {
  id: number;
  name: string;
  party?: string;
  portfolio?: string;
}

export interface Official {
  id: number;
  name: string;
  designation: string;
  department?: string;
}

export interface Firm {
  id: number;
  name: string;
  registration_id: string;
  type: string;
  performance_rating?: number;
  is_blacklisted: boolean;
}

export interface RoadSegment {
  id: number;
  segment_name?: string;
  length_km?: number;
  start_point?: string;
  end_point?: string;
  geometry: GeoJSON.Geometry;
}

export interface Project {
  id: number;
  name: string;
  slug: string;
  description?: string;
  status: ProjectStatus;
  road_type: RoadType;
  district: string;
  city?: string;
  state: string;
  pincode?: string;
  sanctioned_cost: number;
  total_disbursed: number;
  approval_date?: string;
  start_date?: string;
  proposed_end_date?: string;
  actual_end_date?: string;
  minister?: Minister;
  approving_official: Official;
  contractor: Firm;
  maintenance_firm?: Firm;
  created_at: string;
  updated_at?: string;
}

export interface ProjectDetail extends Project {
  road_segments: RoadSegment[];
  reports_count: number;
  disbursements_count: number;
  documents_count: number;
}

export interface PublicReport {
  id: number;
  project_id: number;
  issue_type: IssueType;
  description: string;
  location_description?: string;
  reporter_name?: string;
  reporter_contact?: string;
  status: ReportStatus;
  photo_url?: string;
  upvotes_count: number;
  created_at: string;
  resolution_date?: string;
}

export interface ProjectStats {
  total_projects: number;
  total_cost: number;
  completed_projects: number;
  active_projects: number;
  delayed_projects: number;
  total_reports: number;
  by_status: Record<string, number>;
  by_road_type: Record<string, number>;
  by_state: Record<string, number>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSON.Feature[];
}