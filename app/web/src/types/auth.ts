export interface OrganizationSummary {
  id: number
  name: string
  slug: string
  type: string | null
  logo_url: string | null
}

export interface OrgMembershipSummary {
  id: number
  org_role: string
  status: string
  organization: OrganizationSummary
}

export interface UserProfile {
  name: string | null
  phone: string | null
  student_id: string | null
  qr_code_uri: string | null
  avatar_url: string | null
}

export interface PlatformAccount {
  created_at: string
}

export interface OrganizationAccount {
  organization_id: number | null
  created_at: string
}

export interface LearnerAccount {
  primary_org_id: number | null
  created_at: string
}

export interface AuthUser {
  id: number
  username: string
  email: string
  role: string
  status: string
  account_type: string
  organization_id: number | null
  organization: OrganizationSummary | null
  profile: UserProfile | null
  memberships: OrgMembershipSummary[]
  platform_account: PlatformAccount | null
  organization_account: OrganizationAccount | null
  learner_account: LearnerAccount | null
}

export interface LoginPayload {
  username?: string
  email?: string
  password: string
}

export interface TokenResponse {
  access_token: string
}
