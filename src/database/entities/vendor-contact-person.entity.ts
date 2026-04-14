import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn } from 'typeorm';
import { VendorEntity } from './vendor.entity';

@Entity('vendor_contact_persons')
export class VendorContactPersonEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  vendor_id: number;

  @Column({ nullable: true, type: 'varchar' })
  name: string | null;

  @Column({ nullable: true, type: 'varchar' })
  mobile: string | null;

  @Column({ nullable: true, type: 'varchar' })
  designation: string | null;

  @ManyToOne(() => VendorEntity, { nullable: true })
  @JoinColumn({ name: 'vendor_id' })
  vendor: VendorEntity;
}
