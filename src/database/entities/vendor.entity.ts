import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn, OneToMany } from 'typeorm';
import { LocationEntity } from './location.entity';

@Entity('vendors')
export class VendorEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ nullable: true, type: 'varchar' })
  name: string | null;

  @Column({ nullable: true, type: 'varchar' })
  mobile: string | null;

  @Column({ nullable: true, type: 'varchar' })
  email: string | null;

  @Column({ nullable: true, type: 'varchar' })
  website: string | null;

  @Column({ nullable: true, type: 'varchar' })
  address: string | null;

  @Column({
    nullable: true,
    type: 'enum',
    enum: ['Importer', 'Trader', 'WholeSeller', 'EPC', 'Installer', 'Shopkeeper', 'Manufacturer'],
    name: 'type',
  })
  type: string | null;

  @Column({
    nullable: true,
    type: 'enum',
    enum: ['Whatsapp', 'Email', 'Call', 'Portal', 'Personal', 'SocialMedia'],
    name: 'source',
  })
  source: string | null;

  @Column({ nullable: true, type: 'varchar' })
  whatsapp_group: string | null;

  @Column({ nullable: true, type: 'int' })
  loc_id: number | null;

  @ManyToOne(() => LocationEntity, { nullable: true })
  @JoinColumn({ name: 'loc_id' })
  location: LocationEntity;
}
