import { Controller, Get, Post, Put, Delete, Body, Param, ParseIntPipe, HttpCode, HttpStatus } from '@nestjs/common';
import { BrandsService } from './brands.service';
import { BrandCreateDto } from './brands.dto';

@Controller('brands')
export class BrandsController {
  constructor(private readonly brandsService: BrandsService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: BrandCreateDto) { return this.brandsService.create(dto); }

  @Get()
  findAll() { return this.brandsService.findAll(); }

  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) { return this.brandsService.findOne(id); }

  @Put(':id')
  update(@Param('id', ParseIntPipe) id: number, @Body() dto: BrandCreateDto) {
    return this.brandsService.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.OK)
  remove(@Param('id', ParseIntPipe) id: number) { return this.brandsService.remove(id); }
}
