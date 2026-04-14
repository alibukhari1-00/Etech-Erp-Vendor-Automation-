import { Injectable, UnauthorizedException, ForbiddenException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { ConfigService } from '@nestjs/config';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { UserEntity } from '../../database/entities/user.entity';
import { SystemSettingEntity } from '../../database/entities/system-setting.entity';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(
    private readonly config: ConfigService,
    @InjectRepository(UserEntity) private readonly userRepo: Repository<UserEntity>,
    @InjectRepository(SystemSettingEntity) private readonly settingRepo: Repository<SystemSettingEntity>,
  ) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: config.get<string>('app.secretKey') ?? 'fallback-secret',
    });
  }

  async validate(payload: any) {
    if (payload.type !== 'access') throw new UnauthorizedException('Invalid or expired token.');

    const user = await this.userRepo.findOne({ where: { id: parseInt(payload.sub, 10) } });
    if (!user) throw new UnauthorizedException('User not found.');
    if (!user.is_active) throw new ForbiddenException('User account is deactivated.');

    if (user.role === 'purchaser') {
      const setting = await this.settingRepo.findOne({ where: { key: 'purchaser_access_enabled' } });
      const enabled = setting ? setting.value.trim().toLowerCase() === 'true' : false;
      if (!enabled) throw new ForbiddenException('Purchaser access is not enabled in the current system yet.');
    }

    return user;
  }
}
