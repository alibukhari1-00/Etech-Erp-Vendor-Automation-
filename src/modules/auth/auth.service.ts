import {
  Injectable, UnauthorizedException, ForbiddenException,
  NotFoundException, BadRequestException, ConflictException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcrypt';
import * as crypto from 'crypto';
import * as nodemailer from 'nodemailer';
import { UserEntity } from '../../database/entities/user.entity';
import { UserOtpEntity } from '../../database/entities/user-otp.entity';
import { SystemSettingEntity } from '../../database/entities/system-setting.entity';
import { LoginDto, TokenRefreshDto, ForgotPasswordDto, VerifyOtpDto, ResetPasswordDto } from './auth.dto';
import { ProfileUpdateDto } from '../users/users.dto';

@Injectable()
export class AuthService {
  constructor(
    @InjectRepository(UserEntity) private readonly userRepo: Repository<UserEntity>,
    @InjectRepository(UserOtpEntity) private readonly otpRepo: Repository<UserOtpEntity>,
    @InjectRepository(SystemSettingEntity) private readonly settingRepo: Repository<SystemSettingEntity>,
    private readonly jwtService: JwtService,
    private readonly config: ConfigService,
  ) {}

  private async isPurchaserAccessEnabled(): Promise<boolean> {
    const row = await this.settingRepo.findOne({ where: { key: 'purchaser_access_enabled' } });
    return row ? row.value.trim().toLowerCase() === 'true' : false;
  }

  private createTokens(user: UserEntity) {
    const payload = { sub: String(user.id), email: user.email, role: user.role };
    const accessExpiry = (this.config.get<number>('app.accessTokenExpireMinutes') ?? 30) * 60;
    const refreshExpiry = (this.config.get<number>('app.refreshTokenExpireMinutes') ?? 10080) * 60;
    return {
      access_token: this.jwtService.sign({ ...payload, type: 'access' }, { expiresIn: accessExpiry }),
      refresh_token: this.jwtService.sign({ ...payload, type: 'refresh' }, { expiresIn: refreshExpiry }),
      token_type: 'bearer',
    };
  }

  async login(dto: LoginDto) {
    const user = await this.userRepo.findOne({ where: { email: dto.email.trim().toLowerCase() } });
    if (!user || !(await bcrypt.compare(dto.password, user.hashed_password))) {
      throw new UnauthorizedException('Invalid email or password.');
    }
    if (!user.is_active) throw new ForbiddenException('User account is deactivated.');
    if (user.role === 'purchaser' && !(await this.isPurchaserAccessEnabled())) {
      throw new ForbiddenException('Purchaser access is not enabled in the current system yet.');
    }
    return this.createTokens(user);
  }

  async refresh(dto: TokenRefreshDto) {
    let payload: any;
    try {
      payload = this.jwtService.verify(dto.refresh_token);
    } catch {
      throw new UnauthorizedException('Invalid or expired refresh token.');
    }
    if (payload.type !== 'refresh') throw new UnauthorizedException('Invalid or expired refresh token.');

    const user = await this.userRepo.findOne({ where: { id: parseInt(payload.sub, 10) } });
    if (!user || !user.is_active) throw new UnauthorizedException('User not found or deactivated.');
    if (user.role === 'purchaser' && !(await this.isPurchaserAccessEnabled())) {
      throw new ForbiddenException('Purchaser access is not enabled in the current system yet.');
    }
    return this.createTokens(user);
  }

  async updateMe(currentUser: UserEntity, dto: ProfileUpdateDto): Promise<UserEntity> {
    if (dto.email) {
      const dup = await this.userRepo.findOne({ where: { email: dto.email } });
      if (dup && dup.id !== currentUser.id) {
        throw new ConflictException(`Another user with email '${dto.email}' already exists.`);
      }
    }
    if (dto.username) {
      const dup = await this.userRepo.findOne({ where: { username: dto.username } });
      if (dup && dup.id !== currentUser.id) {
        throw new ConflictException(`Another user with username '${dto.username}' already exists.`);
      }
    }
    if (dto.password) {
      (dto as any).hashed_password = await bcrypt.hash(dto.password, 10);
      delete (dto as any).password;
    }
    Object.assign(currentUser, dto);
    return this.userRepo.save(currentUser);
  }

  async forgotPassword(dto: ForgotPasswordDto) {
    const user = await this.userRepo.findOne({ where: { email: dto.email.toLowerCase() } });
    if (!user) return { message: 'If your email is registered, you will receive an OTP shortly.' };

    await this.otpRepo.delete({ email: dto.email.toLowerCase() });
    const otp = crypto.randomInt(100000, 999999).toString();
    const expires_at = new Date(Date.now() + 10 * 60 * 1000);
    await this.otpRepo.save(this.otpRepo.create({ email: dto.email.toLowerCase(), otp, expires_at }));
    await this.sendOtpEmail(dto.email.toLowerCase(), otp);
    return { message: 'If your email is registered, you will receive an OTP shortly.' };
  }

  async verifyOtp(dto: VerifyOtpDto) {
    const record = await this.otpRepo.findOne({ where: { email: dto.email.toLowerCase(), otp: dto.otp } });
    if (!record || record.isExpired()) throw new BadRequestException('Invalid or expired OTP.');
    return { message: 'OTP verified successfully.' };
  }

  async resetPassword(dto: ResetPasswordDto) {
    const record = await this.otpRepo.findOne({ where: { email: dto.email.toLowerCase(), otp: dto.otp } });
    if (!record || record.isExpired()) throw new BadRequestException('Invalid or expired OTP.');

    const user = await this.userRepo.findOne({ where: { email: dto.email.toLowerCase() } });
    if (!user) throw new NotFoundException('User not found.');

    user.hashed_password = await bcrypt.hash(dto.new_password, 10);
    await this.userRepo.save(user);
    await this.otpRepo.delete({ email: dto.email.toLowerCase() });
    return { message: 'Password reset successfully.' };
  }

  private async sendOtpEmail(email: string, otp: string) {
    const smtp = this.config.get('app.smtp');
    console.log(`\n--- [DEVELOPMENT ONLY] OTP FOR ${email}: ${otp} ---\n`);
    if (!smtp.user || !smtp.password) return;
    try {
      const transporter = nodemailer.createTransport({
        host: smtp.host,
        port: smtp.port,
        secure: false,
        auth: { user: smtp.user, pass: smtp.password },
        ...(smtp.tls ? { starttls: { enable: true } } : {}),
      });
      await transporter.sendMail({
        from: `"${smtp.fromName}" <${smtp.fromEmail}>`,
        to: email,
        subject: 'Your Password Reset OTP',
        html: `<h2>Password Reset Request</h2><p>Your OTP: <strong style="font-size:24px;color:#4F46E5">${otp}</strong></p><p>Valid for 10 minutes.</p>`,
      });
    } catch (e) {
      console.error('Failed to send OTP email:', e);
    }
  }
}
