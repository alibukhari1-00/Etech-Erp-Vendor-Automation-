import { Injectable, NotFoundException, ConflictException, UnprocessableEntityException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { LocationEntity } from '../../database/entities/location.entity';
import { VendorCreateDto } from './vendors.dto';

@Injectable()
export class VendorsService {
  constructor(
    @InjectRepository(VendorEntity) private readonly repo: Repository<VendorEntity>,
    @InjectRepository(LocationEntity) private readonly locRepo: Repository<LocationEntity>,
  ) {}

  async create(dto: VendorCreateDto): Promise<VendorEntity> {
    if (!dto.name) throw new UnprocessableEntityException('Vendor name is required.');
    if (dto.mobile) {
      const ex = await this.repo.findOne({ where: { mobile: dto.mobile } });
      if (ex) throw new ConflictException(`A vendor with mobile '${dto.mobile}' already exists.`);
    }
    if (dto.email) {
      const ex = await this.repo.findOne({ where: { email: dto.email } });
      if (ex) throw new ConflictException(`A vendor with email '${dto.email}' already exists.`);
    }
    if (dto.loc_id && !(await this.locRepo.findOne({ where: { id: dto.loc_id } }))) {
      throw new NotFoundException(`Location with id ${dto.loc_id} does not exist.`);
    }
    return this.repo.save(this.repo.create(dto));
  }

  async findAll(): Promise<VendorEntity[]> {
    const items = await this.repo.find();
    if (!items.length) throw new NotFoundException('No vendors found.');
    return items;
  }

  async findOne(id: number): Promise<VendorEntity> {
    if (id <= 0) throw new UnprocessableEntityException('vendor_id must be a positive integer.');
    const item = await this.repo.findOne({ where: { id } });
    if (!item) throw new NotFoundException(`Vendor with id ${id} not found.`);
    return item;
  }

  async update(id: number, dto: VendorCreateDto): Promise<VendorEntity> {
    const vendor = await this.findOne(id);
    if (dto.mobile) {
      const dup = await this.repo.findOne({ where: { mobile: dto.mobile } });
      if (dup && dup.id !== id) throw new ConflictException(`Another vendor with mobile '${dto.mobile}' already exists.`);
    }
    if (dto.email) {
      const dup = await this.repo.findOne({ where: { email: dto.email } });
      if (dup && dup.id !== id) throw new ConflictException(`Another vendor with email '${dto.email}' already exists.`);
    }
    if (dto.loc_id && !(await this.locRepo.findOne({ where: { id: dto.loc_id } }))) {
      throw new NotFoundException(`Location with id ${dto.loc_id} does not exist.`);
    }
    Object.assign(vendor, dto);
    return this.repo.save(vendor);
  }

  async remove(id: number): Promise<{ message: string }> {
    const vendor = await this.findOne(id);
    await this.repo.remove(vendor);
    return { message: `Vendor '${vendor.name}' deleted successfully.` };
  }
}
