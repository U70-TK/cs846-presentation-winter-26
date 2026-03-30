import { Body, Controller, Get, Post, BadRequestException } from '@nestjs/common';
import { UsageService } from './usage.service';

@Controller('usage')
export class UsageController {
  constructor(private readonly usageService: UsageService) {}

  @Get('summary')
  summary() {
    return this.usageService.summary();
  }

  @Get('audit-log')
  auditLog() {
    return this.usageService.auditLog();
  }

  @Post('audit')
  async writeAudit(@Body('message') message: string) {
    if (typeof message !== 'string' || message.trim().length === 0) {
      throw new BadRequestException('message must be a non-empty string');
    }
    if (message.length > 1000) {
      throw new BadRequestException('message too long');
    }
    return this.usageService.writeAuditEvent(message);
  }
}