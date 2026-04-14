import { Injectable, NotFoundException, ConflictException, UnprocessableEntityException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { SubCategoryEntity } from '../../database/entities/subcategory.entity';
import { CategoryEntity } from '../../database/entities/category.entity';
import { SubCategoryCreateDto } from './subcategories.dto';

@Injectable()
export class SubCategoriesService {
  constructor(
    @InjectRepository(SubCategoryEntity) private readonly repo: Repository<SubCategoryEntity>,
    @InjectRepository(CategoryEntity) private readonly catRepo: Repository<CategoryEntity>,
  ) {}

  async create(dto: SubCategoryCreateDto): Promise<SubCategoryEntity> {
    if (!(await this.catRepo.findOne({ where: { id: dto.cat_id } }))) {
      throw new NotFoundException(`Category with id ${dto.cat_id} does not exist.`);
    }
    const existing = await this.repo.findOne({ where: { name: dto.name, cat_id: dto.cat_id } });
    if (existing) throw new ConflictException(`A sub-category named '${dto.name}' already exists under category ${dto.cat_id}.`);
    return this.repo.save(this.repo.create(dto));
  }

  async findAll(): Promise<SubCategoryEntity[]> {
    const items = await this.repo.find();
    if (!items.length) throw new NotFoundException('No sub-categories found.');
    return items;
  }

  async findOne(id: number): Promise<SubCategoryEntity> {
    if (id <= 0) throw new UnprocessableEntityException('sub_id must be a positive integer.');
    const item = await this.repo.findOne({ where: { id } });
    if (!item) throw new NotFoundException(`Sub-category with id ${id} not found.`);
    return item;
  }

  async update(id: number, dto: SubCategoryCreateDto): Promise<SubCategoryEntity> {
    const item = await this.findOne(id);
    if (!(await this.catRepo.findOne({ where: { id: dto.cat_id } }))) {
      throw new NotFoundException(`Category with id ${dto.cat_id} does not exist.`);
    }
    const dup = await this.repo.findOne({ where: { name: dto.name, cat_id: dto.cat_id } });
    if (dup && dup.id !== id) throw new ConflictException(`Another sub-category named '${dto.name}' already exists under category ${dto.cat_id}.`);
    Object.assign(item, dto);
    return this.repo.save(item);
  }

  async remove(id: number): Promise<{ message: string }> {
    const item = await this.findOne(id);
    await this.repo.remove(item);
    return { message: `Sub-category '${item.name}' deleted successfully.` };
  }
}
