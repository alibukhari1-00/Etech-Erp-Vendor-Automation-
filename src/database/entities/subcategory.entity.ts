import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn } from 'typeorm';
import { CategoryEntity } from './category.entity';

@Entity('sub_categories')
export class SubCategoryEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  cat_id: number;

  @Column()
  name: string;

  @ManyToOne(() => CategoryEntity, { nullable: true })
  @JoinColumn({ name: 'cat_id' })
  category: CategoryEntity;
}
