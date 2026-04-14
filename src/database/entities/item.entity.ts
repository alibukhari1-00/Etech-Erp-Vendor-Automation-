import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn } from 'typeorm';
import { BrandEntity } from './brand.entity';
import { SubCategoryEntity } from './subcategory.entity';

@Entity('items')
export class ItemEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ nullable: true, type: 'int' })
  scat_id: number | null;

  @Column({ nullable: true, type: 'int' })
  brand_id: number | null;

  @Column({ nullable: true, type: 'float' })
  power_rating_kv: number | null;

  @Column({ nullable: true, type: 'float' })
  voltage: number | null;

  @Column({ nullable: true, type: 'varchar' })
  ip_rating: string | null;

  @Column({ nullable: true, type: 'varchar' })
  uom: string | null;

  @Column({ nullable: true, type: 'float' })
  purchase_rate: number | null;

  @Column({ nullable: true, type: 'float' })
  profit_percentage: number | null;

  @Column({ nullable: true, type: 'float' })
  sale_rate: number | null;

  @Column({ nullable: true, type: 'float' })
  sale_rate_manual: number | null;

  @Column({ nullable: true, type: 'varchar' })
  image: string | null;

  @ManyToOne(() => BrandEntity, { nullable: true })
  @JoinColumn({ name: 'brand_id' })
  brand: BrandEntity;

  @ManyToOne(() => SubCategoryEntity, { nullable: true })
  @JoinColumn({ name: 'scat_id' })
  sub_category: SubCategoryEntity;
}
