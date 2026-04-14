import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
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

@Injectable()
export class DashboardService {
  constructor(
    @InjectRepository(VendorEntity) private readonly vendorRepo: Repository<VendorEntity>,
    @InjectRepository(BrandEntity) private readonly brandRepo: Repository<BrandEntity>,
    @InjectRepository(CategoryEntity) private readonly catRepo: Repository<CategoryEntity>,
    @InjectRepository(SubCategoryEntity) private readonly scatRepo: Repository<SubCategoryEntity>,
    @InjectRepository(ItemEntity) private readonly itemRepo: Repository<ItemEntity>,
    @InjectRepository(LocationEntity) private readonly locRepo: Repository<LocationEntity>,
    @InjectRepository(UserEntity) private readonly userRepo: Repository<UserEntity>,
    @InjectRepository(VendorContactPersonEntity) private readonly vcRepo: Repository<VendorContactPersonEntity>,
    @InjectRepository(VendorGroupEntity) private readonly vgRepo: Repository<VendorGroupEntity>,
    @InjectRepository(VendorBrandEntity) private readonly vbRepo: Repository<VendorBrandEntity>,
  ) {}

  async getStats() {
    const [vendors, brands, categories, subcategories, items, locations, users, vendor_contacts, vendor_groups, vendor_brands] =
      await Promise.all([
        this.vendorRepo.count(),
        this.brandRepo.count(),
        this.catRepo.count(),
        this.scatRepo.count(),
        this.itemRepo.count(),
        this.locRepo.count(),
        this.userRepo.count(),
        this.vcRepo.count(),
        this.vgRepo.count(),
        this.vbRepo.count(),
      ]);
    return { vendors, brands, categories, subcategories, items, locations, users, vendor_contacts, vendor_groups, vendor_brands };
  }
}
