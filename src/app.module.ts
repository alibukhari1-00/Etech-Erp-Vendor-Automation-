import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import appConfig from './config/app.config';

import { UserEntity } from './database/entities/user.entity';
import { UserOtpEntity } from './database/entities/user-otp.entity';
import { LocationEntity } from './database/entities/location.entity';
import { BrandEntity } from './database/entities/brand.entity';
import { CategoryEntity } from './database/entities/category.entity';
import { SubCategoryEntity } from './database/entities/subcategory.entity';
import { ItemEntity } from './database/entities/item.entity';
import { VendorEntity } from './database/entities/vendor.entity';
import { VendorContactPersonEntity } from './database/entities/vendor-contact-person.entity';
import { VendorGroupEntity } from './database/entities/vendor-group.entity';
import { VendorBrandEntity } from './database/entities/vendor-brand.entity';
import { ProjectEntity } from './database/entities/project.entity';
import { PurchaseDemandEntity } from './database/entities/purchase-demand.entity';
import { PurchaseDemandItemEntity } from './database/entities/purchase-demand-item.entity';
import { PurchaseDemandVendorEntity } from './database/entities/purchase-demand-vendor.entity';
import { PurchaseQuotationEntity } from './database/entities/purchase-quotation.entity';
import { LogEntity } from './database/entities/log.entity';
import { SystemSettingEntity } from './database/entities/system-setting.entity';

import { AuthModule } from './modules/auth/auth.module';
import { UsersModule } from './modules/users/users.module';
import { DashboardModule } from './modules/dashboard/dashboard.module';
import { SettingsModule } from './modules/settings/settings.module';
import { BrandsModule } from './modules/brands/brands.module';
import { LocationsModule } from './modules/locations/locations.module';
import { CategoriesModule } from './modules/categories/categories.module';
import { SubCategoriesModule } from './modules/subcategories/subcategories.module';
import { ItemsModule } from './modules/items/items.module';
import { VendorsModule } from './modules/vendors/vendors.module';
import { VendorGroupsModule } from './modules/vendor-groups/vendor-groups.module';
import { VendorBrandsModule } from './modules/vendor-brands/vendor-brands.module';
import { VendorContactsModule } from './modules/vendor-contacts/vendor-contacts.module';
import { ProjectsModule } from './modules/projects/projects.module';
import { PurchaseDemandsModule } from './modules/purchase-demands/purchase-demands.module';
import { PurchaseQuotationsModule } from './modules/purchase-quotations/purchase-quotations.module';
import { AiChatModule } from './modules/ai-chat/ai-chat.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, load: [appConfig] }),
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        type: 'postgres',
        url: config.get<string>('app.databaseUrl'),
        entities: [
          UserEntity, UserOtpEntity, LocationEntity, BrandEntity, CategoryEntity,
          SubCategoryEntity, ItemEntity, VendorEntity, VendorContactPersonEntity,
          VendorGroupEntity, VendorBrandEntity, ProjectEntity, PurchaseDemandEntity,
          PurchaseDemandItemEntity, PurchaseDemandVendorEntity, PurchaseQuotationEntity,
          LogEntity, SystemSettingEntity,
        ],
        synchronize: false, // Never auto-sync against existing production DB
        logging: false,
      }),
    }),
    AuthModule,
    UsersModule,
    DashboardModule,
    SettingsModule,
    BrandsModule,
    LocationsModule,
    CategoriesModule,
    SubCategoriesModule,
    ItemsModule,
    VendorsModule,
    VendorGroupsModule,
    VendorBrandsModule,
    VendorContactsModule,
    ProjectsModule,
    PurchaseDemandsModule,
    PurchaseQuotationsModule,
    AiChatModule,
  ],
})
export class AppModule {}
