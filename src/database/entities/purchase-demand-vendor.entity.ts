import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn, Unique } from 'typeorm';
import { PurchaseDemandEntity } from './purchase-demand.entity';
import { VendorEntity } from './vendor.entity';
import { PurchaseDemandItemEntity } from './purchase-demand-item.entity';
import { UserEntity } from './user.entity';

@Entity('purchase_demand_vendors')
@Unique('uq_purchase_demand_item_vendor', ['purchase_demand_id', 'purchase_demand_item_id', 'vendor_id'])
export class PurchaseDemandVendorEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  purchase_demand_id: number;

  @Column({ nullable: true, type: 'int' })
  purchase_demand_item_id: number | null;

  @Column()
  vendor_id: number;

  @Column()
  selected_by: number;

  @ManyToOne(() => PurchaseDemandEntity, (d) => d.selected_vendors, { nullable: true })
  @JoinColumn({ name: 'purchase_demand_id' })
  demand: PurchaseDemandEntity;

  @ManyToOne(() => VendorEntity, { nullable: true })
  @JoinColumn({ name: 'vendor_id' })
  vendor: VendorEntity;

  @ManyToOne(() => PurchaseDemandItemEntity, { nullable: true })
  @JoinColumn({ name: 'purchase_demand_item_id' })
  item: PurchaseDemandItemEntity;

  @ManyToOne(() => UserEntity, { nullable: true })
  @JoinColumn({ name: 'selected_by' })
  selector: UserEntity;
}
