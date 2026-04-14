import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { PurchaseQuotationsController } from './purchase-quotations.controller';
import { PurchaseQuotationsService } from './purchase-quotations.service';
import { PurchaseQuotationEntity } from '../../database/entities/purchase-quotation.entity';
import { PurchaseDemandVendorEntity } from '../../database/entities/purchase-demand-vendor.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';

@Module({
  imports: [TypeOrmModule.forFeature([PurchaseQuotationEntity, PurchaseDemandVendorEntity, VendorEntity])],
  controllers: [PurchaseQuotationsController],
  providers: [PurchaseQuotationsService],
})
export class PurchaseQuotationsModule {}
