import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ItemsController } from './items.controller';
import { ItemsService } from './items.service';
import { ItemEntity } from '../../database/entities/item.entity';
import { BrandEntity } from '../../database/entities/brand.entity';
import { SubCategoryEntity } from '../../database/entities/subcategory.entity';
import { CategoryEntity } from '../../database/entities/category.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { VendorBrandEntity } from '../../database/entities/vendor-brand.entity';
import { VendorGroupEntity } from '../../database/entities/vendor-group.entity';
import { VendorContactPersonEntity } from '../../database/entities/vendor-contact-person.entity';

@Module({
  imports: [
    TypeOrmModule.forFeature([
      ItemEntity, BrandEntity, SubCategoryEntity, CategoryEntity,
      VendorEntity, VendorBrandEntity, VendorGroupEntity, VendorContactPersonEntity,
    ]),
  ],
  controllers: [ItemsController],
  providers: [ItemsService],
  exports: [ItemsService],
})
export class ItemsModule {}
