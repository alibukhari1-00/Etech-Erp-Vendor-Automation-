import { Entity, PrimaryColumn, Column } from 'typeorm';

@Entity('system_settings')
export class SystemSettingEntity {
  @PrimaryColumn()
  key: string;

  @Column()
  value: string;
}
