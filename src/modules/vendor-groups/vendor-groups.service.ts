import { Injectable, NotFoundException, ConflictException, UnprocessableEntityException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { VendorGroupEntity } from '../../database/entities/vendor-group.entity';
import { CategoryEntity } from '../../database/entities/category.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { VendorGroupCreateDto } from './vendor-groups.dto';

@Injectable()
export class VendorGroupsService {
  constructor(
    @InjectRepository(VendorGroupEntity) private readonly repo: Repository<VendorGroupEntity>,
    @InjectRepository(CategoryEntity) private readonly catRepo: Repository<CategoryEntity>,
    @InjectRepository(VendorEntity) private readonly vendorRepo: Repository<VendorEntity>,
  ) {}

  async create(dto: VendorGroupCreateDto): Promise<VendorGroupEntity> {
    if (!(await this.catRepo.findOne({ where: { id: dto.cat_id } }))) {
      throw new NotFoundException(`Category with id ${dto.cat_id} does not exist.`);
    }
    if (!(await this.vendorRepo.findOne({ where: { id: dto.vendor_id } }))) {
      throw new NotFoundException(`Vendor with id ${dto.vendor_id} does not exist.`);
    }
    const existing = await this.repo.findOne({ where: { cat_id: dto.cat_id, vendor_id: dto.vendor_id } });
    if (existing) throw new ConflictException(`Vendor ${dto.vendor_id} is already linked to category ${dto.cat_id}.`);
    return this.repo.save(this.repo.create(dto));
  }

  async findAll(): Promise<VendorGroupEntity[]> {
    const items = await this.repo.find();
    if (!items.length) throw new NotFoundException('No vendor groups found.');
    return items;
  }

  async remove(id: number): Promise<{ message: string }> {
    if (id <= 0) throw new UnprocessableEntityException('group_id must be a positive integer.');
    const item = await this.repo.findOne({ where: { id } });
    if (!item) throw new NotFoundException(`Vendor group with id ${id} not found.`);
    await this.repo.remove(item);
    return { message: `Vendor ${item.vendor_id} unlinked from category ${item.cat_id} successfully.` };
  }
}
