import { Injectable, NotFoundException, ConflictException, UnprocessableEntityException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { VendorContactPersonEntity } from '../../database/entities/vendor-contact-person.entity';
import { VendorEntity } from '../../database/entities/vendor.entity';
import { VendorContactPersonCreateDto } from './vendor-contacts.dto';

@Injectable()
export class VendorContactsService {
  constructor(
    @InjectRepository(VendorContactPersonEntity) private readonly repo: Repository<VendorContactPersonEntity>,
    @InjectRepository(VendorEntity) private readonly vendorRepo: Repository<VendorEntity>,
  ) {}

  async create(dto: VendorContactPersonCreateDto): Promise<VendorContactPersonEntity> {
    if (!(await this.vendorRepo.findOne({ where: { id: dto.vendor_id } }))) {
      throw new NotFoundException(`Vendor with id ${dto.vendor_id} does not exist.`);
    }
    const existing = await this.repo.findOne({ where: { mobile: dto.mobile } });
    if (existing) throw new ConflictException(`A contact with mobile '${dto.mobile}' already exists.`);
    return this.repo.save(this.repo.create(dto));
  }

  async findAll(): Promise<VendorContactPersonEntity[]> {
    const items = await this.repo.find();
    if (!items.length) throw new NotFoundException('No vendor contacts found.');
    return items;
  }

  async remove(id: number): Promise<{ message: string }> {
    if (id <= 0) throw new UnprocessableEntityException('contact_id must be a positive integer.');
    const item = await this.repo.findOne({ where: { id } });
    if (!item) throw new NotFoundException(`Contact with id ${id} not found.`);
    await this.repo.remove(item);
    return { message: `Contact '${item.name}' deleted successfully.` };
  }
}
