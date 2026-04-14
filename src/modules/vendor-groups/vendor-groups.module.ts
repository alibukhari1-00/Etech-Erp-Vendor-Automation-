import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { VendorGroupsController } from './vendor-groups.controller';
import { VendorGroupsService } from './vendor-groups.service';
import { VendorGroupEntity } from '../../database/entities/vendor-group.entity';
import { CategoryEntity } from '../../database/entities/category.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';

@Module({
  imports: [TypeOrmModule.forFeature([VendorGroupEntity, CategoryEntity, VendorEntity])],
  controllers: [VendorGroupsController],
  providers: [VendorGroupsService],
})
export class VendorGroupsModule {}
