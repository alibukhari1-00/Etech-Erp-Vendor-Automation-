import { Controller, Get, Post, Put, Delete, Body, Param, ParseIntPipe, HttpCode, HttpStatus } from '@nestjs/common';
import { SubCategoriesService } from './subcategories.service';
import { SubCategoryCreateDto } from './subcategories.dto';

@Controller('subcategories')
export class SubCategoriesController {
  constructor(private readonly service: SubCategoriesService) {}

  @Post() @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: SubCategoryCreateDto) { return this.service.create(dto); }

  @Get() findAll() { return this.service.findAll(); }

  @Get(':id') findOne(@Param('id', ParseIntPipe) id: number) { return this.service.findOne(id); }

  @Put(':id') update(@Param('id', ParseIntPipe) id: number, @Body() dto: SubCategoryCreateDto) {
    return this.service.update(id, dto);
  }

  @Delete(':id') @HttpCode(HttpStatus.OK)
  remove(@Param('id', ParseIntPipe) id: number) { return this.service.remove(id); }
}
