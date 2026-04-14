import { Injectable, NotFoundException, ConflictException, UnprocessableEntityException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { CategoryEntity } from '../../database/entities/category.entity';
import { CategoryCreateDto } from './categories.dto';

@Injectable()
export class CategoriesService {
  constructor(@InjectRepository(CategoryEntity) private readonly repo: Repository<CategoryEntity>) {}

  async create(dto: CategoryCreateDto): Promise<CategoryEntity> {
    const existing = await this.repo.findOne({ where: { name: dto.name } });
    if (existing) throw new ConflictException(`A category with the name '${dto.name}' already exists.`);
    return this.repo.save(this.repo.create(dto));
  }

  async findAll(): Promise<CategoryEntity[]> {
    const items = await this.repo.find();
    if (!items.length) throw new NotFoundException('No categories found.');
    return items;
  }

  async findOne(id: number): Promise<CategoryEntity> {
    if (id <= 0) throw new UnprocessableEntityException('category_id must be a positive integer.');
    const item = await this.repo.findOne({ where: { id } });
    if (!item) throw new NotFoundException(`Category with id ${id} not found.`);
    return item;
  }

  async update(id: number, dto: CategoryCreateDto): Promise<CategoryEntity> {
    const item = await this.findOne(id);
    const dup = await this.repo.findOne({ where: { name: dto.name } });
    if (dup && dup.id !== id) throw new ConflictException(`Another category with the name '${dto.name}' already exists.`);
    Object.assign(item, dto);
    return this.repo.save(item);
  }

  async remove(id: number): Promise<{ message: string }> {
    const item = await this.findOne(id);
    await this.repo.remove(item);
    return { message: `Category '${item.name}' deleted successfully.` };
  }
}
