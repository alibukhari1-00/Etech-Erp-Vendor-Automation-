import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn } from 'typeorm';
import { PurchaseDemandEntity } from './purchase-demand.entity';
import { ItemEntity } from './item.entity';

@Entity('purchase_demand_items')
export class PurchaseDemandItemEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  purchase_demand_id: number;

  @Column()
  item_id: number;

  @Column({ type: 'float' })
  quantity: number;

  @Column({ nullable: true, type: 'text' })
  notes: string | null;

  @ManyToOne(() => PurchaseDemandEntity, (d) => d.items, { nullable: true })
  @JoinColumn({ name: 'purchase_demand_id' })
  demand: PurchaseDemandEntity;

  @ManyToOne(() => ItemEntity, { nullable: true, eager: false })
  @JoinColumn({ name: 'item_id' })
  item: ItemEntity;
}
