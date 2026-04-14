import { Injectable, NotFoundException, ConflictException, UnprocessableEntityException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { LocationEntity } from '../../database/entities/location.entity';
import { LocationCreateDto } from './locations.dto';

@Injectable()
export class LocationsService {
  constructor(@InjectRepository(LocationEntity) private readonly repo: Repository<LocationEntity>) {}

  async create(dto: LocationCreateDto): Promise<LocationEntity> {
    const existing = await this.repo.findOne({ where: { loc_name: dto.loc_name } });
    if (existing) throw new ConflictException(`A location with the name '${dto.loc_name}' already exists.`);
    return this.repo.save(this.repo.create(dto));
  }

  async findAll(): Promise<LocationEntity[]> {
    const items = await this.repo.find();
    if (!items.length) throw new NotFoundException('No locations found.');
    return items;
  }

  async findOne(id: number): Promise<LocationEntity> {
    if (id <= 0) throw new UnprocessableEntityException('location_id must be a positive integer.');
    const item = await this.repo.findOne({ where: { id } });
    if (!item) throw new NotFoundException(`Location with id ${id} not found.`);
    return item;
  }

  async update(id: number, dto: LocationCreateDto): Promise<LocationEntity> {
    const item = await this.findOne(id);
    const dup = await this.repo.findOne({ where: { loc_name: dto.loc_name } });
    if (dup && dup.id !== id) throw new ConflictException(`Another location with the name '${dto.loc_name}' already exists.`);
    Object.assign(item, dto);
    return this.repo.save(item);
  }

  async remove(id: number): Promise<{ message: string }> {
    const item = await this.findOne(id);
    await this.repo.remove(item);
    return { message: `Location '${item.loc_name}' deleted successfully.` };
  }
}
