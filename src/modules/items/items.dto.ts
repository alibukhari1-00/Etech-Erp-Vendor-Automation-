import {
  IsInt, IsOptional, IsNumber, IsString, IsIn, Min, Max, Matches,
} from 'class-validator';
import { Transform } from 'class-transformer';

const VALID_UOM = ['pcs', 'kg', 'g', 'ltr', 'ml', 'm', 'cm', 'mm', 'ft', 'inch', 'box', 'pack', 'set', 'pair'];

export class ItemCreateDto {
  @IsInt() @Min(1)
  scat_id: number;

  @IsInt() @Min(1)
  brand_id: number;

  @IsOptional() @IsNumber() @Min(0) @Max(100000)
  power_rating_kv?: number | null;

  @IsOptional() @IsNumber() @Min(0) @Max(100000)
  voltage?: number | null;

  @IsOptional() @IsString()
  @Matches(/^IP\d{2}$/, { message: "ip_rating must follow the format 'IP' followed by two digits (e.g., IP65)." })
  @Transform(({ value }) => value?.trim().toUpperCase())
  ip_rating?: string | null;

  @IsOptional() @IsIn(VALID_UOM)
  @Transform(({ value }) => value?.trim().toLowerCase())
  uom?: string | null;

  @IsOptional() @IsNumber() @Min(0)
  purchase_rate?: number | null;

  @IsOptional() @IsNumber() @Min(0) @Max(10000)
  profit_percentage?: number | null;

  @IsOptional() @IsNumber() @Min(0)
  sale_rate?: number | null;

  @IsOptional() @IsNumber() @Min(0)
  sale_rate_manual?: number | null;

  @IsOptional() @IsString() @Transform(({ value }) => value?.trim())
  image?: string | null;
}
