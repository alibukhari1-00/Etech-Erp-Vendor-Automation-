import { Controller, Get, Post, Delete, Body, Param, ParseIntPipe, HttpCode, HttpStatus } from '@nestjs/common';
import { VendorGroupsService } from './vendor-groups.service';
import { VendorGroupCreateDto } from './vendor-groups.dto';

@Controller('vendor-groups')
export class VendorGroupsController {
  constructor(private readonly service: VendorGroupsService) {}

  @Post() @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: VendorGroupCreateDto) { return this.service.create(dto); }

  @Get() findAll() { return this.service.findAll(); }

  @Delete(':id') @HttpCode(HttpStatus.OK)
  remove(@Param('id', ParseIntPipe) id: number) { return this.service.remove(id); }
}
