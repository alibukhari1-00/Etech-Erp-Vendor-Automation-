import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { LocationEntity } from './location.entity';
import { UserEntity } from './user.entity';

@Entity('projects')
export class ProjectEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  project_code: string;

  @Column({ length: 200 })
  name: string;

  @Column({ nullable: true, type: 'int' })
  location_id: number | null;

  @Column({ type: 'enum', enum: ['active', 'completed', 'closed'], default: 'active' })
  status: string;

  @Column()
  created_by: number;

  @CreateDateColumn({ type: 'timestamptz' })
  created_at: Date;

  @UpdateDateColumn({ type: 'timestamptz', nullable: true })
  updated_at: Date | null;

  @ManyToOne(() => LocationEntity, { nullable: true })
  @JoinColumn({ name: 'location_id' })
  location: LocationEntity;

  @ManyToOne(() => UserEntity, { nullable: true })
  @JoinColumn({ name: 'created_by' })
  creator: UserEntity;
}
