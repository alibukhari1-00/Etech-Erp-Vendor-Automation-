import { IsString, IsOptional, IsInt, IsIn, MinLength, MaxLength, Matches, Min } from 'class-validator';
import { Transform } from 'class-transformer';

export class BrandCreateDto {
  @IsString()
  @MinLength(2)
  @MaxLength(100)
  @Matches(/^[a-zA-Z0-9 _\-\.&]+$/, { message: 'Brand name contains invalid characters.' })
  @Transform(({ value }) => value?.trim())
  name: string;

  @IsOptional()
  @IsString()
  @MaxLength(150)
  @Transform(({ value }) => value?.trim())
  company?: string | null;

  @IsOptional()
  @IsInt()
  @Min(1)
  loc_id?: number | null;

  @IsOptional()
  @IsIn(['active', 'inactive', 'pending'])
  @Transform(({ value }) => value?.trim().toLowerCase())
  status?: string | null;
}
