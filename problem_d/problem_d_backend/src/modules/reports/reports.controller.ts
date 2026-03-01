import { Controller, Get, Query } from '@nestjs/common';
import { ReportsService } from './reports.service';

@Controller('reports')
export class ReportsController {
  constructor(private readonly reportsService: ReportsService) {}

  @Get('company')
  company(@Query('organizationId') organizationId?: string, @Query('year') year?: string) {
    const resolvedYear: any = year ? Number(year) : new Date().getFullYear() - 1;
    const orgId: any = organizationId ?? 'org_001';
    return this.reportsService.CompanyReport(orgId, resolvedYear);
  }
}
