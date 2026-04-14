import { Injectable, NotFoundException, ConflictException, UnprocessableEntityException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { VendorBrandEntity } from '../../database/entities/vendor-brand.entity';
import { BrandEntity } from '../../database/entities/brand.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { VendorBrandCreateDto } from './vendor-brands.dto';

@Injectable()
export class VendorBrandsService {
  constructor(
    @InjectRepository(VendorBrandEntity) private readonly repo: Repository<VendorBrandEntity>,
    @InjectRepository(BrandEntity) private readonly brandRepo: Repository<BrandEntity>,
    @InjectRepository(VendorEntity) private readonly vendorRepo: Repository<VendorEntity>,
  ) {}

  async create(dto: VendorBrandCreateDto): Promise<VendorBrandEntity> {
    if (!(await this.brandRepo.findOne({ where: { id: dto.brand_id } }))) {
      throw new NotFoundException(`Brand with id ${dto.brand_id} does not exist.`);
    }
    if (!(await this.vendorRepo.findOne({ where: { id: dto.vendor_id } }))) {
      throw new NotFoundException(`Vendor with id ${dto.vendor_id} does not exist.`);
    }
    const existing = await this.repo.findOne({ where: { brand_id: dto.brand_id, vendor_id: dto.vendor_id } });
    if (existing) throw new ConflictException(`Vendor ${dto.vendor_id} is already linked to brand ${dto.brand_id}.`);
    return this.repo.save(this.repo.create(dto));
  }

  async findAll(): Promise<VendorBrandEntity[]> {
    const items = await this.repo.find();
    if (!items.length) throw new NotFoundException('No vendor-brand links found.');
    return items;
  }

  async remove(id: number): Promise<{ message: string }> {
    if (id <= 0) throw new UnprocessableEntityException('record_id must be a positive integer.');
    const item = await this.repo.findOne({ where: { id } });
    if (!item) throw new NotFoundException(`Vendor-brand link with id ${id} not found.`);
    await this.repo.remove(item);
    return { message: `Vendor ${item.vendor_id} unlinked from brand ${item.brand_id} successfully.` };
  }
}
