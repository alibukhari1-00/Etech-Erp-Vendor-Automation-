import { IsString, IsInt, MinLength, MaxLength, Matches, Min } from 'class-validator';
import { Transform } from 'class-transformer';

export class VendorContactPersonCreateDto {
  @IsInt() @Min(1)
  vendor_id: number;

  @IsString() @MinLength(2) @MaxLength(100)
  @Matches(/^[a-zA-Z\s\'\-\.]+$/, { message: "Name can only contain letters, spaces, hyphens, apostrophes, and dots." })
  @Transform(({ value }) => value?.trim())
  name: string;

  @IsString()
  @Transform(({ value }) => value?.trim())
  mobile: string;

  @IsString() @MinLength(2) @MaxLength(100)
  @Matches(/^[a-zA-Z0-9 \s\'\-\.&\/]+$/, { message: 'Designation contains invalid characters.' })
  @Transform(({ value }) => value?.trim())
  designation: string;
}
