import { Module } from '@nestjs/common';
import { UsageController } from './usage.controller';
import { UsageService } from './usage.service';
import { AuthModule } from '../auth/auth.module';
import { ReviewAuditLogController } from './review-audit-log.controller';

@Module({
  imports: [AuthModule],
  controllers: [UsageController, ReviewAuditLogController],
  providers: [UsageService],
})
export class UsageModule {}
