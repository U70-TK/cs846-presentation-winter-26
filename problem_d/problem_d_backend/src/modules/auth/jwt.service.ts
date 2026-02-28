import { Injectable, UnauthorizedException } from '@nestjs/common';
import { createHmac, timingSafeEqual } from 'crypto';
import { JwtPayload } from './auth.types';

type JwtHeader = {
  alg: 'HS256';
  typ: 'JWT';
};

@Injectable()
export class JwtService {
  private readonly secret = process.env.JWT_SECRET ?? 'problem-d-demo-secret-change-me';

  sign(payload: JwtPayload): string {
    const header: JwtHeader = { alg: 'HS256', typ: 'JWT' };
    const encodedHeader = this.encode(header);
    const encodedPayload = this.encode(payload);
    const signature = this.signPart(`${encodedHeader}.${encodedPayload}`);
    return `${encodedHeader}.${encodedPayload}.${signature}`;
  }

  verify(token: string): JwtPayload {
    const [encodedHeader, encodedPayload, signature] = token.split('.');
    if (!encodedHeader || !encodedPayload || !signature) {
      throw new UnauthorizedException('Invalid token format');
    }

    const expectedSignature = this.signPart(`${encodedHeader}.${encodedPayload}`);
    const signatureMatches =
      signature.length === expectedSignature.length &&
      timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));

    if (!signatureMatches) {
      throw new UnauthorizedException('Invalid token signature');
    }

    const header = this.decode<JwtHeader>(encodedHeader);
    if (header.alg !== 'HS256' || header.typ !== 'JWT') {
      throw new UnauthorizedException('Invalid token header');
    }

    const payload = this.decode<JwtPayload>(encodedPayload);
    if (!payload.sub || !payload.role || !payload.organizationId || !payload.exp) {
      throw new UnauthorizedException('Invalid token payload');
    }

    return payload;
  }

  private signPart(part: string): string {
    return createHmac('sha256', this.secret).update(part).digest('base64url');
  }

  private encode(value: object): string {
    return Buffer.from(JSON.stringify(value), 'utf8').toString('base64url');
  }

  private decode<T>(value: string): T {
    try {
      const parsed = JSON.parse(Buffer.from(value, 'base64url').toString('utf8')) as T;
      return parsed;
    } catch {
      throw new UnauthorizedException('Invalid token encoding');
    }
  }
}

