import { Injectable, NotFoundException, ConflictException, UnprocessableEntityException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { BrandEntity } from '../../database/entities/brand.entity';
import { BrandCreateDto } from './brands.dto';

@Injectable()
export class BrandsService {
  constructor(@InjectRepository(BrandEntity) private readonly repo: Repository<BrandEntity>) {}

  async create(dto: BrandCreateDto): Promise<BrandEntity> {
    const existing = await this.repo.findOne({ where: { name: dto.name } });
    if (existing) throw new ConflictException(`A brand with the name '${dto.name}' already exists.`);
    return this.repo.save(this.repo.create(dto));
  }

  async findAll(): Promise<BrandEntity[]> {
    const brands = await this.repo.find();
    if (!brands.length) throw new NotFoundException('No brands found.');
    return brands;
  }

  async findOne(id: number): Promise<BrandEntity> {
    if (id <= 0) throw new UnprocessableEntityException('brand_id must be a positive integer.');
    const brand = await this.repo.findOne({ where: { id } });
    if (!brand) throw new NotFoundException(`Brand with id ${id} not found.`);
    return brand;
  }

  async update(id: number, dto: BrandCreateDto): Promise<BrandEntity> {
    const brand = await this.findOne(id);
    const dup = await this.repo.findOne({ where: { name: dto.name } });
    if (dup && dup.id !== id) throw new ConflictException(`Another brand with the name '${dto.name}' already exists.`);
    Object.assign(brand, dto);
    return this.repo.save(brand);
  }

  async remove(id: number): Promise<{ message: string }> {
    const brand = await this.findOne(id);
    await this.repo.remove(brand);
    return { message: `Brand '${brand.name}' deleted successfully.` };
  }
}
