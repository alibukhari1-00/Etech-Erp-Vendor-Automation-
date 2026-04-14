import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity('locations')
export class LocationEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  loc_name: string;
}
