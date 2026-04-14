import { Controller, Get, Post, Patch, Param, ParseIntPipe, Body, HttpCode, HttpStatus } from '@nestjs/common';
import { PurchaseQuotationsService } from './purchase-quotations.service';
import { PurchaseQuotationUpdateDto } from './purchase-quotations.dto';

@Controller('purchase-quotations')
export class PurchaseQuotationsController {
  constructor(private readonly service: PurchaseQuotationsService) {}

  @Post('initiate/:demandId')
  @HttpCode(HttpStatus.CREATED)
  initiate(@Param('demandId', ParseIntPipe) demandId: number) {
    return this.service.initiate(demandId);
  }

  @Get('demand/:demandId')
  getForDemand(@Param('demandId', ParseIntPipe) demandId: number) {
    return this.service.getForDemand(demandId);
  }

  @Patch(':id')
  update(@Param('id', ParseIntPipe) id: number, @Body() dto: PurchaseQuotationUpdateDto) {
    return this.service.update(id, dto);
  }

  @Post(':id/select')
  @HttpCode(HttpStatus.OK)
  select(@Param('id', ParseIntPipe) id: number) {
    return this.service.select(id);
  }
}
