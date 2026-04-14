import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn, OneToMany } from 'typeorm';
import { LocationEntity } from './location.entity';

@Entity('brands')
export class BrandEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @Column({ nullable: true, unique: true, type: 'varchar' })
  company: string | null;

  @Column({ nullable: true, type: 'int' })
  loc_id: number | null;

  @Column({ nullable: true, type: 'varchar' })
  status: string | null;

  @ManyToOne(() => LocationEntity, { nullable: true })
  @JoinColumn({ name: 'loc_id' })
  location: LocationEntity;
}
