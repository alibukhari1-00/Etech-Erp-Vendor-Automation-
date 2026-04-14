import { registerAs } from '@nestjs/config';

export default registerAs('app', () => ({
  databaseUrl: process.env.DATABASE_URL,
  secretKey: process.env.SECRET_KEY ?? 'etsolar-erp-secret-key-change-in-production',
  algorithm: process.env.ALGORITHM ?? 'HS256',
  accessTokenExpireMinutes: parseInt(process.env.ACCESS_TOKEN_EXPIRE_MINUTES ?? '30', 10),
  refreshTokenExpireMinutes: parseInt(process.env.REFRESH_TOKEN_EXPIRE_MINUTES ?? '10080', 10),
  openaiApiKey: process.env.OPENAI_API_KEY ?? '',
  smtp: {
    tls: (process.env.SMTP_TLS ?? 'true').toLowerCase() === 'true',
    port: parseInt(process.env.SMTP_PORT ?? '587', 10),
    host: process.env.SMTP_HOST ?? 'smtp.gmail.com',
    user: process.env.SMTP_USER ?? '',
    password: process.env.SMTP_PASSWORD ?? '',
    fromEmail: process.env.EMAILS_FROM_EMAIL ?? 'info@etsolar.com',
    fromName: process.env.EMAILS_FROM_NAME ?? 'ETSolar Support',
  },
  port: parseInt(process.env.PORT ?? '8000', 10),
}));
