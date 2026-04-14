import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn } from 'typeorm';
import { BrandEntity } from './brand.entity';
import { VendorEntity } from './vendor.entity';

@Entity('vendor_brands')
export class VendorBrandEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  brand_id: number;

  @Column()
  vendor_id: number;

  @ManyToOne(() => BrandEntity, { nullable: true })
  @JoinColumn({ name: 'brand_id' })
  brand: BrandEntity;

  @ManyToOne(() => VendorEntity, { nullable: true })
  @JoinColumn({ name: 'vendor_id' })
  vendor: VendorEntity;
}
