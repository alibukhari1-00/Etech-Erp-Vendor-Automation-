import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { VendorContactsController } from './vendor-contacts.controller';
import { VendorContactsService } from './vendor-contacts.service';
import { VendorContactPersonEntity } from '../../database/entities/vendor-contact-person.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';

@Module({
  imports: [TypeOrmModule.forFeature([VendorContactPersonEntity, VendorEntity])],
  controllers: [VendorContactsController],
  providers: [VendorContactsService],
})
export class VendorContactsModule {}
