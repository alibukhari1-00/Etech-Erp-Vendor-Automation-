import { Controller, Get, Post, Delete, Body, Param, ParseIntPipe, HttpCode, HttpStatus } from '@nestjs/common';
import { VendorBrandsService } from './vendor-brands.service';
import { VendorBrandCreateDto } from './vendor-brands.dto';

@Controller('vendor-brands')
export class VendorBrandsController {
  constructor(private readonly service: VendorBrandsService) {}

  @Post() @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: VendorBrandCreateDto) { return this.service.create(dto); }

  @Get() findAll() { return this.service.findAll(); }

  @Delete(':id') @HttpCode(HttpStatus.OK)
  remove(@Param('id', ParseIntPipe) id: number) { return this.service.remove(id); }
}
