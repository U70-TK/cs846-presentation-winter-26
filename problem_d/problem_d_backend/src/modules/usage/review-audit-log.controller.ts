import { Controller, Get, Req, UnauthorizedException, UseGuards } from '@nestjs/common';
import { AuthenticatedUser } from '../auth/auth.types';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { UsageService } from './usage.service';

type RequestWithUser = {
  user?: AuthenticatedUser;
};

@Controller()
export class ReviewAuditLogController {
  constructor(private readonly usageService: UsageService) {}

  @UseGuards(JwtAuthGuard)
  @Get('review-audit-log')
  reviewAuditLog(@Req() req: RequestWithUser) {
    if (!req.user) {
      throw new UnauthorizedException('Missing authenticated user');
    }
    return this.usageService.reviewAuditLog(req.user);
  }
}

