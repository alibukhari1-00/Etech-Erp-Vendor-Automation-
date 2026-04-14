import { Controller, Get, Post, Put, Delete, Body, Param, ParseIntPipe, HttpCode, HttpStatus } from '@nestjs/common';
import { VendorsService } from './vendors.service';
import { VendorCreateDto } from './vendors.dto';

@Controller('vendors')
export class VendorsController {
  constructor(private readonly service: VendorsService) {}

  @Post() @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: VendorCreateDto) { return this.service.create(dto); }

  @Get() findAll() { return this.service.findAll(); }

  @Get(':id') findOne(@Param('id', ParseIntPipe) id: number) { return this.service.findOne(id); }

  @Put(':id') update(@Param('id', ParseIntPipe) id: number, @Body() dto: VendorCreateDto) {
    return this.service.update(id, dto);
  }

  @Delete(':id') @HttpCode(HttpStatus.OK)
  remove(@Param('id', ParseIntPipe) id: number) { return this.service.remove(id); }
}
