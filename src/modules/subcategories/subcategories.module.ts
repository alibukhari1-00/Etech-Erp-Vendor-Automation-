import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { SubCategoriesController } from './subcategories.controller';
import { SubCategoriesService } from './subcategories.service';
import { SubCategoryEntity } from '../../database/entities/subcategory.entity';
import { CategoryEntity } from '../../database/entities/category.entity';

@Module({
  imports: [TypeOrmModule.forFeature([SubCategoryEntity, CategoryEntity])],
  controllers: [SubCategoriesController],
  providers: [SubCategoriesService],
})
export class SubCategoriesModule {}
