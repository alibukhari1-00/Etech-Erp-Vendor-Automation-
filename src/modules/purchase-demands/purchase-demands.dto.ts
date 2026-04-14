import { IsInt, IsOptional, IsString, IsNumber, IsArray, ValidateNested, ArrayMinSize, Min } from 'class-validator';
import { Type } from 'class-transformer';

export class PurchaseDemandItemInputDto {
  @IsInt() @Min(1)
  item_id: number;

  @IsNumber() @Min(0.001)
  quantity: number;

  @IsOptional() @IsString()
  notes?: string | null;
}

export class PurchaseDemandCreateDto {
  @IsInt() @Min(1)
  project_id: number;

  @IsOptional() @IsString()
  remarks?: string | null;

  @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true }) @Type(() => PurchaseDemandItemInputDto)
  items: PurchaseDemandItemInputDto[];
}

export class PurchaseDemandUpdateDto {
  @IsOptional() @IsString()
  remarks?: string | null;

  @IsOptional() @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true }) @Type(() => PurchaseDemandItemInputDto)
  items?: PurchaseDemandItemInputDto[];
}

export class ItemVendorAssignDto {
  @IsInt() @Min(1)
  item_id: number;

  @IsArray() @ArrayMinSize(1)
  vendor_ids: number[];
}

export class VendorAssignBodyDto {
  @IsArray() @ValidateNested({ each: true }) @Type(() => ItemVendorAssignDto)
  assignments: ItemVendorAssignDto[];
}

export class ApproveRequestDto {
  @IsOptional() @IsString()
  remarks?: string | null;
}

export class RejectRequestDto {
  @IsString()
  remarks: string;
}
