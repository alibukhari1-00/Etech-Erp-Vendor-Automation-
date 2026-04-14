import { IsString, MinLength, MaxLength, Matches } from 'class-validator';
import { Transform } from 'class-transformer';

export class CategoryCreateDto {
  @IsString()
  @MinLength(2)
  @MaxLength(100)
  @Matches(/^[a-zA-Z0-9 _\-\.&]+$/, { message: 'Category name contains invalid characters.' })
  @Transform(({ value }) => value?.trim())
  name: string;
}
