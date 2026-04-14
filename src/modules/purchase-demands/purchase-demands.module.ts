import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { PurchaseDemandsController } from './purchase-demands.controller';
import { PurchaseDemandsService } from './purchase-demands.service';
import { PurchaseDemandEntity } from '../../database/entities/purchase-demand.entity';
import { PurchaseDemandItemEntity } from '../../database/entities/purchase-demand-item.entity';
import { PurchaseDemandVendorEntity } from '../../database/entities/purchase-demand-vendor.entity';
import { ProjectEntity } from '../../database/entities/project.entity';
import { ItemEntity } from '../../database/entities/item.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { VendorBrandEntity } from '../../database/entities/vendor-brand.entity';
import { VendorGroupEntity } from '../../database/entities/vendor-group.entity';
import { VendorContactPersonEntity } from '../../database/entities/vendor-contact-person.entity';
import { SubCategoryEntity } from '../../database/entities/subcategory.entity';
import { LogEntity } from '../../database/entities/log.entity';

@Module({
  imports: [
    TypeOrmModule.forFeature([
      PurchaseDemandEntity, PurchaseDemandItemEntity, PurchaseDemandVendorEntity,
      ProjectEntity, ItemEntity, VendorEntity, VendorBrandEntity, VendorGroupEntity,
      VendorContactPersonEntity, SubCategoryEntity, LogEntity,
    ]),
  ],
  controllers: [PurchaseDemandsController],
  providers: [PurchaseDemandsService],
})
export class PurchaseDemandsModule {}
