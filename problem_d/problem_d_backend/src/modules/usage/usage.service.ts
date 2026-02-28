import { ForbiddenException, Injectable } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';
import { execFile } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';

const execFileAsync = promisify(execFile);

@Injectable()
export class UsageService {
  constructor(private readonly db: DatabaseService) {}

  summary() {
    return this.db.get(
      'SELECT ingestion_gb as ingestionGb, model_calls as modelCalls, team_seats as teamSeats, last_sync as lastSync FROM usage_summary LIMIT 1;'
    );
  }

  auditLog() {
    return this.db.all(
      'SELECT id, event, created_at as createdAt FROM audit_log ORDER BY created_at DESC LIMIT 10;'
    );
  }

  async writeAuditEvent(message: string) {
    const backendRoot = process.cwd();

    const binPath = path.join(backendRoot, 'src', 'vendor', 'audit_writer');

    const dbPath = path.join(
      backendRoot,
      '..',
      'problem_d_database',
      'northwind_signal.sqlite'
    );

    try {
      const { stdout } = await execFileAsync(binPath, [
        '--db',
        dbPath,
        '--event',
        message,
      ]);

      return JSON.parse(stdout);
    } catch (err: any) {
      const stderr = err?.stderr ? String(err.stderr) : '';
      throw new ForbiddenException(
        `Auditor binary failed: ${stderr || err?.message || String(err)}`
      );
    }
  }
}