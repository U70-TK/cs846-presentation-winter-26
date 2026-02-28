export type UserRole = 'owner' | 'admin' | 'auditor' | 'member' | 'viewer';

export type AuthenticatedUser = {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  organizationId: string;
};

export type JwtPayload = {
  sub: string;
  name: string;
  email: string;
  role: UserRole;
  organizationId: string;
  iat: number;
  exp: number;
};

