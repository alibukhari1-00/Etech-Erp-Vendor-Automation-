import { IsInt, Min } from 'class-validator';

export class VendorGroupCreateDto {
  @IsInt() @Min(1)
  cat_id: number;

  @IsInt() @Min(1)
  vendor_id: number;
}
