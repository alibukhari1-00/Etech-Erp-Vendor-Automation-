import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { PurchaseDemandEntity } from './purchase-demand.entity';
import { PurchaseDemandItemEntity } from './purchase-demand-item.entity';
import { VendorEntity } from './vendor.entity';

@Entity('purchase_quotations')
export class PurchaseQuotationEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  purchase_demand_id: number;

  @Column()
  purchase_demand_item_id: number;

  @Column()
  vendor_id: number;

  @Column({ nullable: true, type: 'float' })
  unit_price: number | null;

  @Column({ nullable: true, type: 'float' })
  total_price: number | null;

  @Column({ nullable: true, type: 'int' })
  lead_time_days: number | null;

  @Column({ nullable: true, type: 'text' })
  remarks: string | null;

  @Column({ default: 'pending' })
  status: string;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;

  @ManyToOne(() => PurchaseDemandEntity, { nullable: true })
  @JoinColumn({ name: 'purchase_demand_id' })
  demand: PurchaseDemandEntity;

  @ManyToOne(() => PurchaseDemandItemEntity, { nullable: true })
  @JoinColumn({ name: 'purchase_demand_item_id' })
  demand_item: PurchaseDemandItemEntity;

  @ManyToOne(() => VendorEntity, { nullable: true })
  @JoinColumn({ name: 'vendor_id' })
  vendor: VendorEntity;
}
