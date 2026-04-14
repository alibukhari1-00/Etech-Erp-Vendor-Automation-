import { Controller, Get, Post, Delete, Body, Param, ParseIntPipe, HttpCode, HttpStatus } from '@nestjs/common';
import { VendorContactsService } from './vendor-contacts.service';
import { VendorContactPersonCreateDto } from './vendor-contacts.dto';

@Controller('vendor-contacts')
export class VendorContactsController {
  constructor(private readonly service: VendorContactsService) {}

  @Post() @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: VendorContactPersonCreateDto) { return this.service.create(dto); }

  @Get() findAll() { return this.service.findAll(); }

  @Delete(':id') @HttpCode(HttpStatus.OK)
  remove(@Param('id', ParseIntPipe) id: number) { return this.service.remove(id); }
}
