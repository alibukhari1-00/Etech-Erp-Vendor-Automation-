import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { VendorBrandsController } from './vendor-brands.controller';
import { VendorBrandsService } from './vendor-brands.service';
import { VendorBrandEntity } from '../../database/entities/vendor-brand.entity';
import { BrandEntity } from '../../database/entities/brand.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';

@Module({
  imports: [TypeOrmModule.forFeature([VendorBrandEntity, BrandEntity, VendorEntity])],
  controllers: [VendorBrandsController],
  providers: [VendorBrandsService],
})
export class VendorBrandsModule {}
