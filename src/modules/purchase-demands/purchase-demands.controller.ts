import {
  Controller, Get, Post, Put, Delete, Body, Param, ParseIntPipe,
  Query, UseGuards, HttpCode, HttpStatus,
} from '@nestjs/common';
import { PurchaseDemandsService } from './purchase-demands.service';
import {
  PurchaseDemandCreateDto, PurchaseDemandUpdateDto, VendorAssignBodyDto,
  ApproveRequestDto, RejectRequestDto, PurchaseDemandItemInputDto,
} from './purchase-demands.dto';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { AdminGuard } from '../../common/guards/admin.guard';
import { CurrentUser } from '../../common/decorators/current-user.decorator';
import { UserEntity } from '../../database/entities/user.entity';

@Controller('purchase-demands')
@UseGuards(JwtAuthGuard)
export class PurchaseDemandsController {
  constructor(private readonly service: PurchaseDemandsService) {}

  @Post() @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: PurchaseDemandCreateDto, @CurrentUser() user: UserEntity) {
    return this.service.create(dto, user.id);
  }

  @Get()
  findAll(@Query('project_id') projectId: string, @CurrentUser() user: UserEntity) {
    return this.service.findAll(projectId ? parseInt(projectId, 10) : undefined, user);
  }

  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number, @CurrentUser() user: UserEntity) {
    return this.service.findOne(id, user);
  }

  @Post(':id/items')
  addItem(
    @Param('id', ParseIntPipe) id: number,
    @Body() dto: PurchaseDemandItemInputDto,
    @CurrentUser() user: UserEntity,
  ) {
    return this.service.addItem(id, dto, user);
  }

  @Put(':id')
  update(
    @Param('id', ParseIntPipe) id: number,
    @Body() dto: PurchaseDemandUpdateDto,
    @CurrentUser() user: UserEntity,
  ) {
    return this.service.update(id, dto, user);
  }

  @Post(':id/submit')
  @HttpCode(HttpStatus.OK)
  submit(@Param('id', ParseIntPipe) id: number, @CurrentUser() user: UserEntity) {
    return this.service.submit(id, user);
  }

  @Get(':id/vendors')
  getVendors(@Param('id', ParseIntPipe) id: number, @CurrentUser() user: UserEntity) {
    return this.service.getSelectedVendors(id, user);
  }

  @Post(':id/vendors')
  @UseGuards(AdminGuard)
  @HttpCode(HttpStatus.OK)
  assignVendors(
    @Param('id', ParseIntPipe) id: number,
    @Body() body: VendorAssignBodyDto,
    @CurrentUser() user: UserEntity,
  ) {
    return this.service.assignVendors(id, body, user);
  }

  @Post(':id/approve')
  @UseGuards(AdminGuard)
  @HttpCode(HttpStatus.OK)
  approve(
    @Param('id', ParseIntPipe) id: number,
    @Body() body: ApproveRequestDto,
    @CurrentUser() user: UserEntity,
  ) {
    return this.service.approve(id, body, user);
  }

  @Post(':id/reject')
  @UseGuards(AdminGuard)
  @HttpCode(HttpStatus.OK)
  reject(
    @Param('id', ParseIntPipe) id: number,
    @Body() body: RejectRequestDto,
    @CurrentUser() user: UserEntity,
  ) {
    return this.service.reject(id, body, user);
  }

  @Post(':id/cancel')
  @HttpCode(HttpStatus.OK)
  cancel(@Param('id', ParseIntPipe) id: number, @CurrentUser() user: UserEntity) {
    return this.service.cancel(id, user);
  }

  @Delete(':id')
  @UseGuards(AdminGuard)
  @HttpCode(HttpStatus.NO_CONTENT)
  remove(@Param('id', ParseIntPipe) id: number) {
    return this.service.remove(id);
  }

  @Get(':id/quotation-candidates')
  @UseGuards(AdminGuard)
  getQuotationCandidates(@Param('id', ParseIntPipe) id: number) {
    return this.service.getQuotationCandidates(id);
  }
}
