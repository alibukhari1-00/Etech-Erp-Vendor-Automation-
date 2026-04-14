import {
  ExceptionFilter, Catch, ArgumentsHost, HttpException, HttpStatus,
} from '@nestjs/common';
import { Response } from 'express';

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    if (exception instanceof HttpException) {
      const status = exception.getStatus();
      const res = exception.getResponse();
      // Preserve FastAPI-style { detail: "..." } format
      if (typeof res === 'object' && res !== null && 'detail' in res) {
        return response.status(status).json(res);
      }
      const detail = typeof res === 'string' ? res : (res as any).message ?? 'An error occurred';
      return response.status(status).json({ detail });
    }

    response.status(HttpStatus.INTERNAL_SERVER_ERROR).json({ detail: 'Internal server error' });
  }
}
