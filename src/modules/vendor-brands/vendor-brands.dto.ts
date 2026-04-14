import { IsInt, Min } from 'class-validator';

export class VendorBrandCreateDto {
  @IsInt() @Min(1)
  brand_id: number;

  @IsInt() @Min(1)
  vendor_id: number;
}
