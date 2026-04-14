import {
  Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn,
  CreateDateColumn, UpdateDateColumn, OneToMany,
} from 'typeorm';
import { ProjectEntity } from './project.entity';
import { UserEntity } from './user.entity';
import { PurchaseDemandItemEntity } from './purchase-demand-item.entity';
import { PurchaseDemandVendorEntity } from './purchase-demand-vendor.entity';

@Entity('purchase_demands')
export class PurchaseDemandEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  demand_code: string;

  @Column()
  project_id: number;

  @Column({
    type: 'enum',
    enum: ['draft', 'pending_approval', 'approved', 'rejected', 'cancelled'],
    default: 'draft',
  })
  status: string;

  @Column({ nullable: true, type: 'text' })
  remarks: string | null;

  @Column()
  created_by: number;

  @Column({ nullable: true, type: 'int' })
  updated_by: number | null;

  @Column({ nullable: true, type: 'int' })
  approved_by: number | null;

  @Column({ nullable: true, type: 'timestamptz' })
  approved_at: Date | null;

  @CreateDateColumn({ type: 'timestamptz' })
  created_at: Date;

  @UpdateDateColumn({ type: 'timestamptz', nullable: true })
  updated_at: Date | null;

  @ManyToOne(() => ProjectEntity, { nullable: true })
  @JoinColumn({ name: 'project_id' })
  project: ProjectEntity;

  @ManyToOne(() => UserEntity, { nullable: true })
  @JoinColumn({ name: 'created_by' })
  creator: UserEntity;

  @ManyToOne(() => UserEntity, { nullable: true })
  @JoinColumn({ name: 'approved_by' })
  approver: UserEntity;

  @OneToMany(() => PurchaseDemandItemEntity, (item) => item.demand, { cascade: true })
  items: PurchaseDemandItemEntity[];

  @OneToMany(() => PurchaseDemandVendorEntity, (v) => v.demand, { cascade: true })
  selected_vendors: PurchaseDemandVendorEntity[];
}
