import { IsOptional, IsNumber, IsInt, IsString, Min } from 'class-validator';

export class PurchaseQuotationUpdateDto {
  @IsOptional() @IsNumber() @Min(0)
  unit_price?: number | null;

  @IsOptional() @IsNumber() @Min(0)
  total_price?: number | null;

  @IsOptional() @IsInt() @Min(0)
  lead_time_days?: number | null;

  @IsOptional() @IsString()
  remarks?: string | null;

  @IsOptional() @IsString()
  status?: string;
}
