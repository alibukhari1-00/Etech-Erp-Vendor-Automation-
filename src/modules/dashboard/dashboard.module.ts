import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { DashboardController } from './dashboard.controller';
import { DashboardService } from './dashboard.service';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { BrandEntity } from '../../database/entities/brand.entity';
import { CategoryEntity } from '../../database/entities/category.entity';
import { SubCategoryEntity } from '../../database/entities/subcategory.entity';
import { ItemEntity } from '../../database/entities/item.entity';
import { LocationEntity } from '../../database/entities/location.entity';
import { UserEntity } from '../../database/entities/user.entity';
import { VendorContactPersonEntity } from '../../database/entities/vendor-contact-person.entity';
import { VendorGroupEntity } from '../../database/entities/vendor-group.entity';
import { VendorBrandEntity } from '../../database/entities/vendor-brand.entity';

@Module({
  imports: [
    TypeOrmModule.forFeature([
      VendorEntity, BrandEntity, CategoryEntity, SubCategoryEntity,
      ItemEntity, LocationEntity, UserEntity, VendorContactPersonEntity,
      VendorGroupEntity, VendorBrandEntity,
    ]),
  ],
  controllers: [DashboardController],
  providers: [DashboardService],
})
export class DashboardModule {}
