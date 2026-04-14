import { Controller, Get, Put, Body, UseGuards } from '@nestjs/common';
import { SettingsService } from './settings.service';
import { PurchaserAccessUpdateDto } from './settings.dto';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { AdminGuard } from '../../common/guards/admin.guard';

@Controller('settings')
@UseGuards(JwtAuthGuard, AdminGuard)
export class SettingsController {
  constructor(private readonly service: SettingsService) {}

  @Get('purchaser-access')
  get() { return this.service.getPurchaserAccess(); }

  @Put('purchaser-access')
  update(@Body() dto: PurchaserAccessUpdateDto) {
    return this.service.setPurchaserAccess(dto.purchaser_access_enabled);
  }
}
