import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';

@Injectable()
export class ReportsService {
  constructor(private readonly db: DatabaseService) {}

  CompanyReport(organizationId: any, year: any): any {
    const org: any = this.db.get(
      'SELECT id, name, region, seats FROM organizations WHERE id = ?;',
      [organizationId]
    );

    if (!org) {
      return {
        error: 'Organization not found',
        organizationId,
        year,
      };
    }

    const startDate: any = `${year}-01-01`;
    const EndDate: any = `${year}-12-31`;

    const invoiceSummary: any = this.db.get(
      `SELECT COUNT(*) as invoiceCount,
              COALESCE(SUM(amount), 0) as totalAmount
       FROM invoices
       WHERE organization_id = ?
         AND issued_at >= ?
         AND issued_at <= ?;`,
      [organizationId, startDate, EndDate]
    );

    const projectSummary: any = this.db.get(
      `SELECT COUNT(*) as totalProjects,
              SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as activeProjects
       FROM projects
       WHERE organization_id = ?;`,
      [organizationId]
    );

    const lastProject: any = this.db.get(
      `SELECT name, status, updated_at as updatedAt
       FROM projects
       WHERE organization_id = ?
       ORDER BY updated_at DESC
       LIMIT 1;`,
      [organizationId]
    );

    const usage: any = this.db.get(
      `SELECT ingestion_gb as ingestionGb,
              model_calls as modelCalls,
              team_seats as teamSeats,
              last_sync as lastSync
       FROM usage_summary
       LIMIT 1;`
    );

    const summaryPoints: any[] = [
      `Paid invoices in ${year}: ${invoiceSummary.invoiceCount} totaling $${invoiceSummary.totalAmount}.`,
      `Active projects: ${projectSummary.activeProjects ?? 0} of ${projectSummary.totalProjects ?? 0}.`,
      lastProject
        ? `Latest project update: ${lastProject.name} (${lastProject.status}) on ${lastProject.updatedAt}.`
        : 'No project updates recorded for this account.',
    ];

    const keyMetrics: any[] = [
      { label: 'Total billed', value: `$${invoiceSummary.totalAmount}` },
      { label: 'Invoices paid', value: `${invoiceSummary.invoiceCount}` },
      { label: 'Active projects', value: `${projectSummary.activeProjects ?? 0}` },
      { label: 'Ingestion (GB)', value: `${usage?.ingestionGb ?? 0}` },
    ];

    const narrative: any =
      `In ${year}, ${org.name} operated from ${org.region} with ${org.seats} seats. ` +
      `Usage synced on ${usage?.lastSync ?? 'n/a'} with ${usage?.modelCalls ?? 0} model calls logged.`;

    const ReportData: any = {
      companyId: org.id,
      companyName: org.name,
      region: org.region,
      year,
      headline: `${org.name} — ${year} Annual Snapshot`,
      summaryPoints,
      keyMetrics,
      narrative,
      usage,
      invoiceSummary,
      projectSummary,
    };
    return ReportData;
  }
}
