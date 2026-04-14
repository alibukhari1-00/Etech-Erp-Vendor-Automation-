import { Controller, Get, Post, Put, Delete, Body, Param, ParseIntPipe, HttpCode, HttpStatus } from '@nestjs/common';
import { LocationsService } from './locations.service';
import { LocationCreateDto } from './locations.dto';

@Controller('locations')
export class LocationsController {
  constructor(private readonly service: LocationsService) {}

  @Post() @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: LocationCreateDto) { return this.service.create(dto); }

  @Get() findAll() { return this.service.findAll(); }

  @Get(':id') findOne(@Param('id', ParseIntPipe) id: number) { return this.service.findOne(id); }

  @Put(':id') update(@Param('id', ParseIntPipe) id: number, @Body() dto: LocationCreateDto) {
    return this.service.update(id, dto);
  }

  @Delete(':id') @HttpCode(HttpStatus.OK)
  remove(@Param('id', ParseIntPipe) id: number) { return this.service.remove(id); }
}
