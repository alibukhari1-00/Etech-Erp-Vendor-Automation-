import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { SystemSettingEntity } from '../../database/entities/system-setting.entity';

const KEY = 'purchaser_access_enabled';

@Injectable()
export class SettingsService {
  constructor(@InjectRepository(SystemSettingEntity) private readonly repo: Repository<SystemSettingEntity>) {}

  async getPurchaserAccess(): Promise<{ purchaser_access_enabled: boolean }> {
    const row = await this.repo.findOne({ where: { key: KEY } });
    return { purchaser_access_enabled: row ? row.value.trim().toLowerCase() === 'true' : false };
  }

  async setPurchaserAccess(enabled: boolean): Promise<{ purchaser_access_enabled: boolean }> {
    let row = await this.repo.findOne({ where: { key: KEY } });
    if (row) {
      row.value = enabled ? 'true' : 'false';
    } else {
      row = this.repo.create({ key: KEY, value: enabled ? 'true' : 'false' });
    }
    await this.repo.save(row);
    return { purchaser_access_enabled: enabled };
  }
}
