import { Controller, Get } from '@nestjs/common';

@Controller()
export class AppController {
  @Get()
  root() {
    return { message: 'ETSolar ERP API (NestJS)', version: '1.0.0' };
  }
}
