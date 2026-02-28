import { ForbiddenException, Injectable } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';
import { AuthenticatedUser } from '../auth/auth.types';

type AuditPermissionRecord = {
  scope: 'organization' | 'project_assigned' | 'self';
  canViewSensitive: number;
};

type AuditLogRecord = {
  id: string;
  organizationId: string;
  projectId: string | null;
  eventType: string;
  severity: string;
  actorUserId: string;
  actorName: string;
  occurredAt: string;
  isSensitive: number;
  metadata: string;
};

@Injectable()
export class UsageService {
  constructor(private readonly db: DatabaseService) {}

  summary() {
    return this.db.get(
      'SELECT ingestion_gb as ingestionGb, model_calls as modelCalls, team_seats as teamSeats, last_sync as lastSync FROM usage_summary LIMIT 1;'
    );
  }

  reviewAuditLog(user: AuthenticatedUser) {
    const permission = this.db.get(
      `
      SELECT scope, can_view_sensitive as canViewSensitive
      FROM role_audit_permissions
      WHERE role = ?
      LIMIT 1;
      `,
      [user.role]
    ) as AuditPermissionRecord | undefined;

    if (!permission) {
      throw new ForbiddenException('No audit-log permission configured for this role');
    }

    const sensitiveFilter = permission.canViewSensitive ? '' : 'AND al.is_sensitive = 0';
    const baseSelect = `
      SELECT
        al.id as id,
        al.organization_id as organizationId,
        al.project_id as projectId,
        al.event_type as eventType,
        al.severity as severity,
        al.actor_user_id as actorUserId,
        u.name as actorName,
        al.occurred_at as occurredAt,
        al.is_sensitive as isSensitive,
        al.metadata as metadata
      FROM audit_logs al
      INNER JOIN users u ON u.id = al.actor_user_id
    `;

    if (permission.scope === 'organization') {
      return this.db.all<AuditLogRecord>(
        `
        ${baseSelect}
        WHERE al.organization_id = ?
          ${sensitiveFilter}
        ORDER BY al.occurred_at DESC;
        `,
        [user.organizationId]
      );
    }

    if (permission.scope === 'project_assigned') {
      return this.db.all<AuditLogRecord>(
        `
        ${baseSelect}
        INNER JOIN project_memberships pm ON pm.project_id = al.project_id
        WHERE al.organization_id = ?
          AND pm.user_id = ?
          ${sensitiveFilter}
        ORDER BY al.occurred_at DESC;
        `,
        [user.organizationId, user.id]
      );
    }

    return this.db.all<AuditLogRecord>(
      `
      ${baseSelect}
      WHERE al.organization_id = ?
        AND al.actor_user_id = ?
        ${sensitiveFilter}
      ORDER BY al.occurred_at DESC;
      `,
      [user.organizationId, user.id]
    );
  }
}
