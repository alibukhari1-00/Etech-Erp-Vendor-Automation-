import { IsString, IsInt, MinLength, MaxLength, Matches, Min } from 'class-validator';
import { Transform } from 'class-transformer';

export class SubCategoryCreateDto {
  @IsString()
  @MinLength(2)
  @MaxLength(100)
  @Matches(/^[a-zA-Z0-9 _\-\.&]+$/, { message: 'Sub-category name contains invalid characters.' })
  @Transform(({ value }) => value?.trim())
  name: string;

  @IsInt()
  @Min(1)
  cat_id: number;
}
