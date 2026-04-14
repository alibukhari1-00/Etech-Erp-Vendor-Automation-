import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { VendorsController } from './vendors.controller';
import { VendorsService } from './vendors.service';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { LocationEntity } from '../../database/entities/location.entity';

@Module({
  imports: [TypeOrmModule.forFeature([VendorEntity, LocationEntity])],
  controllers: [VendorsController],
  providers: [VendorsService],
  exports: [VendorsService],
})
export class VendorsModule {}
