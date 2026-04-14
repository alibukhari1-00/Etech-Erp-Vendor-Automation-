import {
  Controller, Get, Post, Put, Delete, Body, Param, ParseIntPipe,
  Query, HttpCode, HttpStatus,
} from '@nestjs/common';
import { ItemsService } from './items.service';
import { ItemCreateDto } from './items.dto';

@Controller('items')
export class ItemsController {
  constructor(private readonly service: ItemsService) {}

  @Post() @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: ItemCreateDto) { return this.service.create(dto); }

  @Get() findAll() { return this.service.findAll(); }

  @Get('search')
  search(@Query('q') q: string, @Query('limit') limit?: string) {
    return this.service.search(q, limit ? parseInt(limit, 10) : 50);
  }

  @Get(':id/vendors')
  getVendors(@Param('id', ParseIntPipe) id: number) { return this.service.getVendorsForItem(id); }

  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) { return this.service.findOne(id); }

  @Put(':id')
  update(@Param('id', ParseIntPipe) id: number, @Body() dto: ItemCreateDto) {
    return this.service.update(id, dto);
  }

  @Delete(':id') @HttpCode(HttpStatus.OK)
  remove(@Param('id', ParseIntPipe) id: number) { return this.service.remove(id); }
}
