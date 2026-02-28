import { Injectable, UnauthorizedException } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';
import { AuthenticatedUser, JwtPayload, UserRole } from './auth.types';
import { JwtService } from './jwt.service';

type LoginRow = {
  userId: string;
  name: string;
  email: string;
  role: UserRole;
  organizationId: string;
};

@Injectable()
export class AuthService {
  constructor(
    private readonly db: DatabaseService,
    private readonly jwtService: JwtService
  ) {}

  login(email: string, password: string) {
    const row = this.db.get(
      `
      SELECT
        u.id as userId,
        u.name as name,
        u.email as email,
        om.role as role,
        om.organization_id as organizationId
      FROM users u
      INNER JOIN organization_memberships om ON om.user_id = u.id
      WHERE u.email = ? AND u.password = ?
      LIMIT 1;
      `,
      [email, password]
    ) as LoginRow | undefined;

    if (!row) {
      throw new UnauthorizedException('Invalid email or password');
    }

    const nowInSeconds = Math.floor(Date.now() / 1000);
    const payload: JwtPayload = {
      sub: row.userId,
      name: row.name,
      email: row.email,
      role: row.role,
      organizationId: row.organizationId,
      iat: nowInSeconds,
      exp: nowInSeconds + 60 * 60 * 8,
    };

    return {
      token: this.jwtService.sign(payload),
      user: this.toAuthenticatedUser(payload),
    };
  }

  currentUser(user: AuthenticatedUser) {
    return user;
  }

  private toAuthenticatedUser(payload: JwtPayload): AuthenticatedUser {
    return {
      id: payload.sub,
      name: payload.name,
      email: payload.email,
      role: payload.role,
      organizationId: payload.organizationId,
    };
  }
}
