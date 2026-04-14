import { IsString, IsOptional, IsInt, IsIn, MinLength, MaxLength, Min } from 'class-validator';
import { Transform } from 'class-transformer';

export class ProjectCreateDto {
  @IsString() @MinLength(2) @MaxLength(200)
  @Transform(({ value }) => value?.trim())
  name: string;

  @IsOptional() @IsInt() @Min(1)
  location_id?: number | null;

  @IsOptional() @IsIn(['active', 'completed', 'closed'])
  status?: string;
}

export class ProjectUpdateDto {
  @IsOptional() @IsString() @MinLength(2) @MaxLength(200)
  @Transform(({ value }) => value?.trim())
  name?: string;

  @IsOptional() @IsInt() @Min(1)
  location_id?: number | null;

  @IsOptional() @IsIn(['active', 'completed', 'closed'])
  status?: string;
}
