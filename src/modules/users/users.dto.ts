import {
  IsEmail, IsString, IsOptional, IsBoolean, MinLength, MaxLength,
  Matches, IsIn,
} from 'class-validator';
import { Transform } from 'class-transformer';

export class UserCreateDto {
  @IsEmail()
  @Transform(({ value }) => value?.trim().toLowerCase())
  email: string;

  @IsString()
  @MinLength(3)
  @MaxLength(50)
  @Matches(/^[a-zA-Z0-9_@.-]+$/)
  @Transform(({ value }) => value?.trim().toLowerCase())
  username: string;

  @IsString()
  @MinLength(2)
  @MaxLength(100)
  @Transform(({ value }) => value?.trim())
  full_name: string;

  @IsString()
  @MinLength(6)
  @MaxLength(128)
  password: string;

  @IsOptional()
  @IsString()
  avatar_url?: string | null;

  @IsOptional()
  @IsIn(['admin', 'purchaser'])
  role?: string;

  @IsOptional()
  @IsBoolean()
  is_active?: boolean;
}

export class UserUpdateDto {
  @IsOptional()
  @IsEmail()
  @Transform(({ value }) => value?.trim().toLowerCase())
  email?: string;

  @IsOptional()
  @IsString()
  @MinLength(3)
  @MaxLength(50)
  @Transform(({ value }) => value?.trim().toLowerCase())
  username?: string;

  @IsOptional()
  @IsString()
  @MinLength(2)
  @MaxLength(100)
  @Transform(({ value }) => value?.trim())
  full_name?: string;

  @IsOptional()
  @IsString()
  avatar_url?: string | null;

  @IsOptional()
  @IsIn(['admin', 'purchaser'])
  role?: string;

  @IsOptional()
  @IsBoolean()
  is_active?: boolean;

  @IsOptional()
  @IsString()
  @MinLength(6)
  @MaxLength(128)
  password?: string;
}

export class ProfileUpdateDto {
  @IsOptional()
  @IsEmail()
  @Transform(({ value }) => value?.trim().toLowerCase())
  email?: string;

  @IsOptional()
  @IsString()
  @MinLength(3)
  @MaxLength(50)
  @Transform(({ value }) => value?.trim().toLowerCase())
  username?: string;

  @IsOptional()
  @IsString()
  @MinLength(2)
  @MaxLength(100)
  @Transform(({ value }) => value?.trim())
  full_name?: string;

  @IsOptional()
  @IsString()
  avatar_url?: string | null;

  @IsOptional()
  @IsString()
  @MinLength(6)
  @MaxLength(128)
  password?: string;
}
