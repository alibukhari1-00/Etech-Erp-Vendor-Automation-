import { IsString, IsOptional, IsInt, IsIn, MinLength, MaxLength, Matches, Min } from 'class-validator';
import { Transform } from 'class-transformer';

const VALID_TYPES = ['Importer', 'Trader', 'WholeSeller', 'EPC', 'Installer', 'Shopkeeper', 'Manufacturer'];
const VALID_SOURCES = ['Whatsapp', 'Email', 'Call', 'Portal', 'Personal', 'SocialMedia'];

export class VendorCreateDto {
  @IsOptional() @IsString() @MinLength(2) @MaxLength(150)
  @Matches(/^[a-zA-Z0-9 _\-\.&,\(\)]+$/, { message: 'Vendor name contains invalid characters.' })
  @Transform(({ value }) => value?.trim())
  name?: string | null;

  @IsOptional() @IsString()
  @Transform(({ value }) => value?.trim())
  mobile?: string | null;

  @IsOptional() @IsString()
  @Transform(({ value }) => value?.trim().toLowerCase())
  email?: string | null;

  @IsOptional() @IsString() @MaxLength(255)
  @Transform(({ value }) => value?.trim())
  website?: string | null;

  @IsOptional() @IsString() @MinLength(5) @MaxLength(300)
  @Transform(({ value }) => value?.trim())
  address?: string | null;

  @IsOptional() @IsIn(VALID_TYPES)
  type?: string | null;

  @IsOptional() @IsIn(VALID_SOURCES)
  source?: string | null;

  @IsOptional() @IsString() @MaxLength(100)
  @Transform(({ value }) => value?.trim())
  whatsapp_group?: string | null;

  @IsOptional() @IsInt() @Min(1)
  loc_id?: number | null;
}
