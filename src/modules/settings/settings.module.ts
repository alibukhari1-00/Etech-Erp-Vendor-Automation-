import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { SettingsController } from './settings.controller';
import { SettingsService } from './settings.service';
import { SystemSettingEntity } from '../../database/entities/system-setting.entity';

@Module({
  imports: [TypeOrmModule.forFeature([SystemSettingEntity])],
  controllers: [SettingsController],
  providers: [SettingsService],
})
export class SettingsModule {}
