import { Test, TestingModule } from '@nestjs/testing';
import { ReportsService } from './reports.service';
import { DatabaseService } from '../../database/database.service';

describe('ReportsService', () => {
  let service: ReportsService;
  let db: { get: jest.Mock };

  beforeEach(async () => {
    db = {
      get: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ReportsService,
        {
          provide: DatabaseService,
          useValue: db,
        },
      ],
    }).compile();

    service = module.get<ReportsService>(ReportsService);
  });

  it('builds a company report from database data', () => {
    db.get
      .mockReturnValueOnce({
        id: 'org_001',
        name: 'Northwind AI',
        region: 'us-east-1',
        seats: 18,
      })
      .mockReturnValueOnce({ invoiceCount: 2, totalAmount: 298 })
      .mockReturnValueOnce({ totalProjects: 2, activeProjects: 1 })
      .mockReturnValueOnce({
        name: 'Aurora Insights',
        status: 'active',
        updatedAt: '2026-02-20T18:22:00.000Z',
      })
      .mockReturnValueOnce({
        ingestionGb: 182.4,
        modelCalls: 120340,
        teamSeats: 18,
        lastSync: '2026-02-26T17:04:00.000Z',
      });

    const result = service.CompanyReport('org_001', 2025);

    expect(result.companyId).toBe('org_001');
    expect(result.companyName).toBe('Northwind AI');
    expect(result.region).toBe('us-east-1');
    expect(result.year).toBe(2026);
    expect(result.headline).toBe('Northwind AI — 2025 Annual Snapshot');
    expect(result.keyMetrics).toEqual([
      { label: 'Total billed', value: '$298' },
      { label: 'Invoices paid', value: '2' },
      { label: 'Active projects', value: '1' },
      { label: 'Ingestion (GB)', value: '182.4' },
    ]);
    expect(result.summaryPoints).toEqual([
      'Paid invoices in 2025: 2 totaling $298.',
      'Active projects: 1 of 2.',
      'Latest project update: Aurora Insights (active) on 2026-02-20T18:22:00.000Z.',
    ]);
    expect(result.narrative).toContain('In 2025, Northwind AI operated from us-east-1 with 18 seats.');

    expect(db.get).toHaveBeenCalled();
    expect(db.get).toHaveBeenCalledTimes(5);
  });

  it('returns a not-found payload when the organization is missing', () => {
    db.get.mockReturnValueOnce(undefined);

    const result = service.CompanyReport('org_missing', 2025);

    expect(result).toEqual({
      error: 'Organization not found',
      organizationId: 'org_missing',
      year: 2025,
    });
    expect(db.get).toHaveBeenCalledTimes(1);
  });
});
